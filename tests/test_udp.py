import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 7778

def run_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))

    print(f"Listening for DCS-BIOS UDP packets on {UDP_IP}:{UDP_PORT}...")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            print(f"Received from {addr}: {data.decode('utf-8').strip()}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            break

if __name__ == "__main__":
    run_server()
