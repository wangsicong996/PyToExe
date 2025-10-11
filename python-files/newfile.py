from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics import RenderContext
from kivy.clock import Clock  # Для асинхронного анализа, чтобы не блокировать UI
from scapy.all import rdpcap, Dot11, Dot11Beacon, Dot11Elt, EAPOL
import os
import gc  # Для управления памятью

# Запрашиваем разрешения для Android
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

class CapAnalyzerApp(App):
    def build(self):
        # Оптимизация размера окна для мобильных устройств
        Window.size = (360, 640)
        Window.minimum_width, Window.minimum_height = 360, 640  # Фиксируем минимальный размер для сенсорных экранов

        # Настраиваем OpenGL ES 3.2 для Mali-G52 (если поддерживается, иначе fallback на 2.0)
        try:
            Window.canvas = RenderContext(use_es3=True)
        except Exception:
            Window.canvas = RenderContext(use_es2=True)  # Fallback для совместимости
        gl_version = Window.canvas.shader_version
        print(f"OpenGL ES Version: {gl_version}")

        # Основной layout с уменьшенным padding для экономии экрана
        self.layout = BoxLayout(orientation='vertical', padding=5, spacing=5)

        # Кнопка выбора файла (увеличена для сенсорного ввода)
        self.select_button = Button(text="Обзор файла (.cap)", size_hint=(1, 0.15), font_size=20)
        self.select_button.bind(on_press=self.select_file)
        self.layout.add_widget(self.select_button)

        # Текстовое поле для результатов с прокруткой (оптимизировано по высоте)
        self.result_scroll = ScrollView(size_hint=(1, 0.6))
        self.result_text = TextInput(text=f"OpenGL ES Version: {gl_version}\n\n", readonly=True, size_hint=(1, None), height=800, font_size=14)
        self.result_scroll.add_widget(self.result_text)
        self.layout.add_widget(self.result_scroll)

        # Кнопка очистки
        self.clear_button = Button(text="Очистить", size_hint=(1, 0.15), font_size=20)
        self.clear_button.bind(on_press=self.clear_results)
        self.layout.add_widget(self.clear_button)

        # Статус-бар (сокращённый текст для мобильных)
        self.status_label = Label(text="Готово", size_hint=(1, 0.1), font_size=16)
        self.layout.add_widget(self.status_label)

        return self.layout

    def select_file(self, instance):
        if platform == 'android':
            from jnius import autoclass, cast
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("*/*")
            activity = PythonActivity.mActivity
            activity.startActivityForResult(intent, 1)

            def on_activity_result(request_code, result_code, data):
                if request_code == 1 and result_code == -1:
                    uri = data.getData()
                    self.file_path = self.uri_to_path(uri)
                    self.status_label.text = "Анализ..."
                    Clock.schedule_once(lambda dt: self.analyze_cap_file(self.file_path), 0.1)  # Асинхронно, чтобы не блокировать UI
            activity.bind(on_activity_result=on_activity_result)
        else:
            # Для ПК (тестирование)
            from kivy.uix.filechooser import FileChooserListView
            popup = BoxLayout(orientation='vertical')
            file_chooser = FileChooserListView(filters=['*.cap', '*.pcap'])
            def on_submit(instance, selection, touch):
                if selection:
                    self.file_path = selection[0]
                    self.status_label.text = "Анализ..."
                    Clock.schedule_once(lambda dt: self.analyze_cap_file(self.file_path), 0.1)
                popup.dismiss()
            file_chooser.bind(on_submit=on_submit)
            popup.add_widget(file_chooser)
            close_button = Button(text="Закрыть", size_hint=(1, 0.1))
            close_button.bind(on_press=lambda x: popup.dismiss())
            popup.add_widget(close_button)
            from kivy.uix.popup import Popup
            Popup(title="Выберите .cap-файл", content=popup, size_hint=(0.9, 0.9)).open()

    def uri_to_path(self, uri):
        from jnius import autoclass
        DocumentsContract = autoclass('android.provider.DocumentsContract')
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        cursor = context.getContentResolver().query(uri, None, None, None, None)
        cursor.moveToFirst()
        path = cursor.getString(cursor.getColumnIndexOrThrow("_data"))
        cursor.close()
        return path

    def analyze_cap_file(self, cap_file):
        self.result_text.text = f"Анализируем файл: {os.path.basename(cap_file)}\n\n"
        try:
            # Оптимизация: Загружаем пакеты по частям (Scapy PcapReader для экономии памяти на мобильных)
            from scapy.utils import PcapReader
            reader = PcapReader(cap_file)
            ssid = None
            eapol_packets = 0  # Считаем количество вместо списка для экономии памяти
            bssid = None
            packet_count = 0  # Счётчик для прогресса

            for pkt in reader:
                packet_count += 1
                if packet_count % 1000 == 0:  # Обновляем UI каждые 1000 пакетов, чтобы не тормозить
                    self.result_text.text += f"Обработано {packet_count} пакетов...\n"
                    self.result_text.see("end")  # Прокрутка вниз
                    Clock.schedule_once(lambda dt: None, 0)  # Yield для UI обновления
                    gc.collect()  # Сбор мусора для памяти

                if pkt.haslayer(Dot11Beacon):
                    if pkt.haslayer(Dot11Elt) and pkt[Dot11Elt].ID == 0:
                        ssid = pkt[Dot11Elt].info.decode('utf-8', errors='ignore')
                        bssid = pkt[Dot11].addr2
                if pkt.haslayer(EAPOL):
                    eapol_packets += 1

            reader.close()

            # Формируем результат
            if ssid and bssid:
                self.result_text.text += f"Найдена сеть: SSID = {ssid}, BSSID = {bssid}\n"
            else:
                self.result_text.text += "SSID или BSSID не найдены\n"

            if eapol_packets >= 4:
                self.result_text.text += f"\nОбнаружен полный 4-way handshake! ({eapol_packets} EAPOL-пакетов)\n"
                self.result_text.text += "Файл подходит для aircrack-ng.\n"
                self.status_label.text = "Handshake найден!"
            elif eapol_packets > 0:
                self.result_text.text += f"\nНайдено {eapol_packets} EAPOL-пакетов (неполный handshake).\n"
                self.status_label.text = "Неполный HS"
            else:
                self.result_text.text += "\nHandshake не найден.\n"
                self.status_label.text = "HS не найден"

            self.result_text.text += f"\nВсего пакетов: {packet_count}\n"
            gc.collect()  # Финальный сбор мусора

        except Exception as e:
            self.result_text.text += f"Ошибка: {str(e)}\n"
            self.status_label.text = "Ошибка"

        self.result_text.see("end")  # Прокрутка в конец

    def clear_results(self, instance):
        self.result_text.text = f"OpenGL ES Version: {Window.canvas.shader_version}\n\n"
        self.status_label.text = "Готово"
        gc.collect()  # Очистка памяти

if __name__ == "__main__":
    CapAnalyzerApp().run()