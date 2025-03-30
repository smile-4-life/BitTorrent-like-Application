import struct
import logging

def send_msg(sock, msg):
    """Send a message with a length prefix."""
    try:
        msg = struct.pack('>I', len(msg)) + msg
        sock.sendall(msg)
    except Exception as e:
        logging.error(f"Error sending message: {e}")

def recv_msg(sock):
    """Receive a message with a length prefix."""
    try:
        raw_msglen = recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall(sock, msglen)
    except Exception as e:
        logging.error(f"Error receiving message: {e}")
        return None

def recvall(sock, n):
    """Ensure all data is received."""
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def encode_data(data):
    if isinstance(data, dict):
        data_type = b'DICT'
        encoded_data = json.dumps(data).encode()
    elif isinstance(data, list):
        data_type = b'LIST'
        encoded_data = json.dumps(data).encode()
    elif isinstance(data, bytes):
        data_type = b'BIN '
        encoded_data = data
    else:
        data_type = b'RAW '
        encoded_data = str(data).encode()
    
    return data_type, encoded_data

def decode_data(data_type, data):
    if data_type == b'DICT':
        return json.loads(data.decode()) 
    elif data_type == b'LIST':
        return json.loads(data.decode())  
    elif data_type == b'BIN ':
        return data  
    else:
        return data.decode() 