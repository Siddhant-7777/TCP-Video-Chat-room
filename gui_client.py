import tkinter as tk
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk
import socket
import struct
import pickle
import cv2
import threading
import time
import pyaudio
import numpy as np
from cryptography.fernet import Fernet
import base64
import hashlib

PASSWORD = "secure123"  # Must match server password

def get_cipher_key(password):
    hash_obj = hashlib.sha256(password.encode())
    key = base64.urlsafe_b64encode(hash_obj.digest())
    return key

class VideoChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Chat with Audio & Encryption")
        self.root.geometry("800x650")

        # Get server IP
        self.server_ip = simpledialog.askstring("Connect", "Enter Server IP (e.g., 192.168.1.100):")
        if not self.server_ip:
            self.root.destroy()
            return

        # Connect to server
        try:
            self.socket = socket.socket()
            self.socket.connect((self.server_ip, 5555))
            print(f"Connected to {self.server_ip}")
        except:
            messagebox.showerror("Error", "Could not connect to server")
            self.root.destroy()
            return

        # Setup encryption
        self.cipher = Fernet(get_cipher_key(PASSWORD))

        # UI
        self.video_frame = tk.Frame(root, bg="black")
        self.video_frame.pack(side="top", fill="both", expand=True)

        self.remote_label = tk.Label(self.video_frame, bg="black", text="Remote Video")
        self.remote_label.pack(side="left", fill="both", expand=True)

        self.local_label = tk.Label(self.video_frame, bg="black", text="Your Video")
        self.local_label.pack(side="right", fill="both", expand=True)

        # Chat
        chat_frame = tk.Frame(root)
        chat_frame.pack(fill="x", padx=10, pady=5)

        self.chat_box = tk.Text(chat_frame, height=4, state="disabled")
        self.chat_box.pack(fill="x")

        self.msg_entry = tk.Entry(chat_frame)
        self.msg_entry.pack(fill="x", pady=5)
        self.msg_entry.bind("<Return>", self.send_message)

        tk.Button(chat_frame, text="Send", command=self.send_message).pack()

        # Audio status
        status_frame = tk.Frame(root)
        status_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(status_frame, text="🔒 Encrypted | 🔊 Audio Enabled", fg="green").pack()

        self.running = True

        # Setup audio
        self.p = pyaudio.PyAudio()
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100

        # Audio stream
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS,
                                   rate=self.RATE, input=True, output=True,
                                   frames_per_buffer=self.CHUNK)

        threading.Thread(target=self.send_video, daemon=True).start()
        threading.Thread(target=self.send_audio, daemon=True).start()
        threading.Thread(target=self.receive_data, daemon=True).start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def send_message(self, event=None):
        msg = self.msg_entry.get()
        if not msg:
            return

        data = msg.encode()
        encrypted = self.cipher.encrypt(data)
        header = struct.pack("!BL", 1, len(encrypted))  # 1 = text
        self.socket.sendall(header + encrypted)

        self.log_message(f"You: {msg}")
        self.msg_entry.delete(0, tk.END)

    def send_video(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        while self.running:
            ret, frame = cap.read()
            if ret:
                self.show_image(frame, self.local_label)

                _, img_encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
                data = pickle.dumps(img_encoded)
                encrypted = self.cipher.encrypt(pickle.dumps(data))
                header = struct.pack("!BL", 0, len(encrypted))  # 0 = video
                try:
                    self.socket.sendall(header + encrypted)
                except:
                    break

            time.sleep(0.04)  # 25 FPS

        cap.release()

    def send_audio(self):
        while self.running:
            try:
                # Record audio
                audio_data = self.stream.read(self.CHUNK, exception_on_overflow=False)
                audio_array = np.frombuffer(audio_data, dtype=np.float32)

                # Compress audio (simple downsampling)
                compressed = audio_array[::2]
                data = pickle.dumps(compressed)
                encrypted = self.cipher.encrypt(data)
                header = struct.pack("!BL", 2, len(encrypted))  # 2 = audio

                try:
                    self.socket.sendall(header + encrypted)
                except:
                    break

                time.sleep(0.02)
            except:
                break

    def receive_data(self):
        buffer = b""
        header_size = 5

        while self.running:
            try:
                # Get header
                while len(buffer) < header_size:
                    chunk = self.socket.recv(4096)
                    if not chunk:
                        return
                    buffer += chunk

                msg_type, size = struct.unpack("!BL", buffer[:header_size])
                buffer = buffer[header_size:]

                # Get message body
                while len(buffer) < size:
                    chunk = self.socket.recv(4096)
                    if not chunk:
                        return
                    buffer += chunk

                payload = buffer[:size]
                buffer = buffer[size:]

                # Decrypt
                decrypted = self.cipher.decrypt(payload)

                if msg_type == 0:  # Video
                    frame_data = pickle.loads(pickle.loads(decrypted))
                    frame = cv2.imdecode(frame_data, cv2.IMREAD_COLOR)
                    self.show_image(frame, self.remote_label)
                elif msg_type == 1:  # Text
                    text = decrypted.decode()
                    self.log_message(f"Other: {text}")
                elif msg_type == 2:  # Audio
                    audio_array = pickle.loads(decrypted)
                    audio_bytes = (audio_array * 32767).astype(np.int16).tobytes()
                    self.stream.write(audio_bytes)
            except:
                break

    def show_image(self, cv_frame, label):
        rgb = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)
        photo = ImageTk.PhotoImage(image=img)
        label.config(image=photo)
        label.image = photo

    def log_message(self, msg):
        self.chat_box.config(state="normal")
        self.chat_box.insert(tk.END, msg + "\n")
        self.chat_box.config(state="disabled")

    def on_close(self):
        self.running = False
        try:
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            self.socket.close()
        except:
            pass
        self.root.destroy()

root = tk.Tk()
app = VideoChatApp(root)
root.mainloop()
