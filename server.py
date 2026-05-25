import socket
import threading
from cryptography.fernet import Fernet
import base64
import hashlib

HOST = '0.0.0.0'
PORT = 5555
PASSWORD = "secure123"  # Change this to your password

# Generate encryption key from password
def get_cipher_key(password):
    hash_obj = hashlib.sha256(password.encode())
    key = base64.urlsafe_b64encode(hash_obj.digest())
    return key

CIPHER_KEY = get_cipher_key(PASSWORD)

def relay_data(sender, receiver, cipher):
    """Relay encrypted data from one client to another."""
    while True:
        try:
            data = sender.recv(4096)
            if not data:
                break
            receiver.sendall(data)
        except:
            break
    sender.close()
    receiver.close()

print(f"Server starting on port {PORT}...")
print(f"Using password: {PASSWORD}")

server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(2)
print(f"Waiting for 2 clients to connect...")

# Accept 2 clients
client1, addr1 = server.accept()
print(f"Client 1 connected: {addr1}")

client2, addr2 = server.accept()
print(f"Client 2 connected: {addr2}")

print("Both clients connected! Starting relay...")

cipher = Fernet(CIPHER_KEY)

# Create relay threads
thread1 = threading.Thread(target=relay_data, args=(client1, client2, cipher), daemon=True)
thread2 = threading.Thread(target=relay_data, args=(client2, client1, cipher), daemon=True)

thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("Clients disconnected.")
server.close()
