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

Pyaudio issue (Debugging) --- Run only if needed :

Bash
pip install pipwin
pipwin install pyaudio

For macOS
You need to install the PortAudio library via Homebrew first:

Bash
brew install portaudio
pip install pyaudio
For Linux (Ubuntu/Debian)
You need the development headers for the audio system:

Bash
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev
# Or if that fails:
pip install pyaudio

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

Handling Audio Overflow: In the send_audio method, we use exception_on_overflow=False. This is critical because if the CPU lags for a millisecond, the audio buffer might fill up faster than the network can send it. By setting this to False, the application ignores the overflow error rather than crashing the entire audio thread.
