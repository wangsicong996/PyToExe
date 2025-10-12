import asyncio
import json
import os
from pathlib import Path
import time
from typing import Dict, Any

import websockets

from settings import AppSettings, load_settings, save_settings
from serial_io import SerialManager
from simulation import Simulator
from model_loader import ModelManager
from inference import InferenceEngine
from chatbot import Chatbot


class BackendServer:
    def __init__(self, cfg: AppSettings):
        self.cfg = cfg
        self.serial_mgr = SerialManager(cfg)
        self.simulator = Simulator(cfg)
        self.model_mgr = ModelManager(cfg)
        self.engine = InferenceEngine(cfg, self.model_mgr)
        self.chatbot = Chatbot(self.engine)
        self.clients = set()
        self.streaming = False

    async def notify(self, ws, msg: Dict[str, Any]):
        await ws.send(json.dumps(msg))

    async def broadcast(self, msg: Dict[str, Any]):
        if not self.clients:
            return
        data = json.dumps(msg)
        await asyncio.gather(*(c.send(data) for c in self.clients))

    async def handle_message(self, ws, msg: Dict[str, Any]):
        t = msg.get('type')
        if t == 'get_status':
            await self.notify(ws, {
                'type': 'status',
                'connected': self.serial_mgr.is_connected,
                'model_loaded': self.model_mgr.is_loaded,
                'simulation': self.cfg.simulation.enabled,
            })
        elif t == 'start_stream':
            self.streaming = True
            await self.notify(ws, {'type': 'status', 'streaming': True})
        elif t == 'stop_stream':
            self.streaming = False
            await self.notify(ws, {'type': 'status', 'streaming': False})
        elif t == 'update_settings':
            new_settings = msg.get('settings', {})
            self.cfg = load_settings(Path('config/config.json'), overrides=new_settings)
            # Re-init components that depend on config
            self.serial_mgr.update_config(self.cfg)
            self.simulator.update_config(self.cfg)
            self.engine.update_config(self.cfg)
            self.model_mgr.update_config(self.cfg)
            await self.notify(ws, {'type': 'status', 'message': 'settings_updated', 'settings': self.cfg.model_dump()})
        elif t == 'chat_message':
            text = msg.get('text', '')
            ans = self.chatbot.answer(text)
            await self.notify(ws, {'type': 'chat_response', 'text': ans})
        else:
            await self.notify(ws, {'type': 'error', 'message': f'Unknown message type: {t}'})

    async def producer_task(self):
        """Continuously read samples and run inference when streaming."""
        last_broadcast = 0.0
        while True:
            try:
                if not self.streaming:
                    await asyncio.sleep(0.05)
                    continue

                sample = None
                if self.cfg.simulation.enabled:
                    sample = self.simulator.read_sample()
                else:
                    if not self.serial_mgr.is_connected:
                        self.serial_mgr.try_connect()
                        if not self.serial_mgr.is_connected:
                            await asyncio.sleep(0.5)
                            continue
                    sample = self.serial_mgr.read_sample()

                if sample is None:
                    await asyncio.sleep(0.001)
                    continue

                ts, value, meta = sample['ts'], sample['value'], sample['meta']

                # Push to inference engine
                anomaly, score, info = self.engine.push_sample(value, ts)

                # Broadcast raw sample periodically and anomalies immediately
                now = time.time()
                if now - last_broadcast > 0.05:  # 20 Hz for UI
                    scale = self.engine.scale_hint()
                    payload = {'type': 'ecg_data', 'ts': ts, 'value': value, 'meta': meta}
                    if scale:
                        payload['scale'] = scale
                    await self.broadcast(payload)
                    last_broadcast = now

                if anomaly:
                    await self.broadcast({'type': 'anomaly', 'ts': ts, 'score': score, 'info': info})
                    # Signal Arduino if connected
                    if self.serial_mgr.is_connected:
                        self.serial_mgr.trigger_alarm()

            except Exception as e:
                await self.broadcast({'type': 'error', 'message': 'producer_loop_error', 'detail': str(e)})
                await asyncio.sleep(0.2)

    async def ws_handler(self, ws):
        self.clients.add(ws)
        try:
            await self.notify(ws, {'type': 'status', 'connected': self.serial_mgr.is_connected, 'model_loaded': self.model_mgr.is_loaded})
            async for message in ws:
                try:
                    msg = json.loads(message)
                except Exception:
                    await self.notify(ws, {'type': 'error', 'message': 'Malformed JSON'})
                    continue
                await self.handle_message(ws, msg)
        finally:
            self.clients.discard(ws)


async def main():
    cfg = load_settings(Path('config/config.json'))
    server = BackendServer(cfg)

    # Start producer loop
    prod_task = asyncio.create_task(server.producer_task())

    async with websockets.serve(server.ws_handler, cfg.server.host, cfg.server.port, ping_interval=20, ping_timeout=20):
        print(f"Backend WebSocket server running at ws://{cfg.server.host}:{cfg.server.port}")
        await asyncio.Future()  # run forever

    await prod_task


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
