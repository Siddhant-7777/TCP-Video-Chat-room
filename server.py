import socket
import threading

# Server Configuration
HOST = '0.0.0.0' 
PORT = 5555      

clients = []

def handle_relay(current_socket, partner_socket):
    """Relays all incoming bytes from one client directly to the other."""
    try:
        while True:
            data = current_socket.recv(8192) # Larger buffer for video chunks
            if not data:
                break
            partner_socket.sendall(data)
    except:
        pass
    finally:
        current_socket.close()
        print("A client has disconnected.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"Server listening on {HOST}:{PORT}...")

    while len(clients) < 2:
        conn, addr = server.accept()
        print(f"Connected to {addr}")
        clients.append(conn)

    print("Both clients connected. Starting bidirectional relay...")
    
    # Start two-way relay threads
    t1 = threading.Thread(target=handle_relay, args=(clients[0], clients[1]), daemon=True)
    t2 = threading.Thread(target=handle_relay, args=(clients[1], clients[0]), daemon=True)

    t1.start()
    t2.start()

    # Keep main thread alive
    t1.join()
    t2.join()

if __name__ == "__main__":
    start_server()