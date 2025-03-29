import socket

def create_server_socket(host="0.0.0.0", port=8000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print(f"[Tracker] Listening on port {port}")
    return s
