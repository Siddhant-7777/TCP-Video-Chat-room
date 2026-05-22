import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import socket
import struct
import pickle
import cv2
import threading
import time

# --- CONFIGURATION ---
SERVER_IP = '127.0.0.1' # Change to your Server's Public IP
PORT = 5555

class VideoChatApp:
    def __init__(self, window):
        self.window = window
        self.window.title("TCP Video & Text Chat")
        self.window.geometry("800x600")

        # --- UI LAYOUT ---
        # Video Container
        self.video_frame = tk.Frame(window, bg="black")
        self.video_frame.pack(side="top", fill="both", expand=True)

        self.remote_video = tk.Label(self.video_frame, bg="black", text="Waiting for Remote...")
        self.remote_video.pack(side="left", fill="both", expand=True, padx=5)

        self.local_video = tk.Label(self.video_frame, bg="black", text="Local Preview")
        self.local_video.pack(side="right", fill="both", expand=True, padx=5)

        # Chat Container
        self.chat_display = scrolledtext.ScrolledText(window, height=8, state='disabled')
        self.chat_display.pack(fill="x", padx=10, pady=5)

        self.input_frame = tk.Frame(window)
        self.input_frame.pack(fill="x", padx=10, pady=5)

        self.entry_field = tk.Entry(self.input_frame)
        self.entry_field.pack(side="left", fill="x", expand=True)
        self.entry_field.bind("<Return>", self.send_text_msg)

        self.send_btn = tk.Button(self.input_frame, text="Send", command=self.send_text_msg)
        self.send_btn.pack(side="right", padx=5)

        # --- NETWORK SETUP ---
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((SERVER_IP, PORT))
        except Exception as e:
            self.log_message(f"SYSTEM: Connection failed - {e}")
            return

        # Start Threads
        self.running = True
        threading.Thread(target=self.receive_loop, daemon=True).start()
        threading.Thread(target=self.send_video_loop, daemon=True).start()

    def send_text_msg(self, event=None):
        msg = self.entry_field.get()
        if msg:
            data = msg.encode('utf-8')
            # Protocol: 1 (Text) + Size + Data
            header = struct.pack("!BL", 1, len(data))
            try:
                self.client_socket.sendall(header + data)
                self.log_message(f"You: {msg}")
                self.entry_field.delete(0, tk.END)
            except:
                self.log_message("SYSTEM: Failed to send.")

    def send_video_loop(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        while self.running:
            ret, frame = cap.read()
            if ret:
                # 1. Show Local Preview
                self.update_ui_image(frame, self.local_video)

                # 2. Compress and Send
                _, encoded = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                data = pickle.dumps(encoded)
                # Protocol: 0 (Video) + Size + Data
                header = struct.pack("!BL", 0, len(data))
                try:
                    self.client_socket.sendall(header + data)
                except:
                    break
            time.sleep(0.04) # Cap at ~25 FPS
        cap.release()

    def receive_loop(self):
        data = b""
        header_size = struct.calcsize("!BL")

        while self.running:
            try:
                # 1. Get Header
                while len(data) < header_size:
                    packet = self.client_socket.recv(8192)
                    if not packet: return
                    data += packet
                
                flag, msg_size = struct.unpack("!BL", data[:header_size])
                data = data[header_size:]

                # 2. Get Full Payload
                while len(data) < msg_size:
                    data += self.client_socket.recv(8192)

                payload = data[:msg_size]
                data = data[msg_size:]

                # 3. Handle by Flag
                if flag == 0: # Video
                    decoded_frame = cv2.imdecode(pickle.loads(payload), cv2.IMREAD_COLOR)
                    self.update_ui_image(decoded_frame, self.remote_video)
                elif flag == 1: # Text
                    text_msg = payload.decode('utf-8')
                    self.log_message(f"Partner: {text_msg}")

            except Exception as e:
                self.log_message(f"SYSTEM: Receiver Error - {e}")
                break

    def update_ui_image(self, cv_img, label):
        """Thread-safe update of Tkinter labels with OpenCV frames."""
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        img_tk = ImageTk.PhotoImage(image=pil_img)
        label.config(image=img_tk)
        label.image = img_tk

    def log_message(self, msg):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, msg + "\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoChatApp(root)
    root.mainloop()