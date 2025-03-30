import struct
import logging

BUFFER_SIZE = 1024

def send_msg(sock, msg):
    """Send a message with length prefix."""
    try:
        msg = struct.pack(">I", len(msg)) + msg.encode()
        sock.sendall(msg)
    except Exception as e:
        logging.error(f"Error sending message: {e}")

def recv_msg(sock):
    """Receive a message with length prefix."""
    try:
        raw_msglen = recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack(">I", raw_msglen)[0]
        return recvall(sock, msglen).decode()
    except Exception as e:
        logging.error(f"Error receiving message: {e}")
        return None

def recvall(sock, n):
    """Ensure the socket receives exactly `n` bytes."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data
