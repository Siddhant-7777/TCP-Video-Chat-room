🚀 Zoom Clone (Encrypted Real-Time Communication)
A lightweight, multi-threaded, and secure real-time video, audio, and chat application built from scratch using Python.

✨ Features
🎥 Full-Duplex Communication: Simultaneous video, audio, and text transmission.

🔒 E2EE (End-to-End Encryption): All data packets are encrypted using Fernet (AES-128) to ensure privacy.

📦 Custom Protocol: Uses a lightweight 5-byte header for efficient packet routing.

🧵 Multi-threaded: Separate background workers for video, audio, and data handling to keep the UI responsive.

👥 Cross-Client Compatibility: Supports multiple concurrent clients via a central relay server.

🏗️ Architecture
Networking: Implemented using Python's socket library (SOCK_STREAM / TCP).

Concurrency: Uses threading to manage multiple clients and simultaneous data streams.

Data Serialization: Custom binary packet framing using struct to handle network stream fragmentation.

Encryption: Symmetric encryption using the cryptography library.

Media Processing: OpenCV for real-time video capture and compression, PyAudio for low-latency voice streaming.

🛠️ Prerequisites
Python 3.x

Required Libraries:

Bash
pip install opencv-python pillow pyaudio cryptography numpy
🚀 How to Run
1️⃣ Start the Server
Run the server script to begin listening for incoming connections:

Bash
python server.py
2️⃣ Launch the Client
Open one or more client terminals and run the GUI application:

Bash
python gui_client.py
When prompted, enter the Server IP address (use 127.0.0.1 for local testing).

📋 Technical Details
Packet Header (5 Bytes):

Byte 1: Message Type (0: Video, 1: Text, 2: Audio)

Bytes 2-5: Payload Size (Unsigned Long)

Encryption Key: Derives a secure 32-byte key from the hardcoded password using SHA-256 hashing.
