import socket

def connect_to_tracker(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print(f"[Client] Connected to tracker at {host}:{port}")
    return s
