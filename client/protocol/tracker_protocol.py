import struct
import socket
import logging
from enum import Enum

class OpCode(Enum):
    REGISTER = 0x01
    UNREGISTER = 0x02
    RESPONSE = 0x03
    GETPEER = 0x04
    GIVEPEER = 0x05

def send_msg(sock, msg: bytes):
    try:
        msg = struct.pack('>I', len(msg)) + msg
        sock.sendall(msg)
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        raise ConnectionError("Connection was closed or failed to send data")

def recv_msg(sock):
    try:
        raw_msglen = recvall(sock, 4)
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall(sock, msglen)
    except ConnectionError as ce:
        logging.warning(f"Connection issue: {ce}")
        raise
    except Exception as e:
        logging.error(f"Protocol/data logic error: {e}")
        return None

def recvall(sock, n: int):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            logging.error(f"Failed to receive expected data. Only {len(data)} bytes received, but {n} expected.")
            raise ConnectionError("Connection was closed or failed to receive data")
        data.extend(packet)
    return data

# ======================= ENCODERS =======================

def encode_register(data: dict):
    return struct.pack(">BHI", OpCode.REGISTER.value, data.get("port"), data.get("pieces_left", 0))

def encode_unregister(data: dict):
    return struct.pack(">BH", OpCode.UNREGISTER.value, data.get("port"))

def encode_response(data: dict):
    response_bytes = data.get("response", "").encode("utf-8")
    ip_bytes = data.get("client_ip", "").encode("utf-8")

    response_len = len(response_bytes)
    ip_len = len(ip_bytes)

    return (
        struct.pack(">BI", OpCode.RESPONSE.value, response_len) +
        response_bytes +
        struct.pack("B", ip_len) +
        ip_bytes
    )

def encode_getpeer(_: dict):
    return struct.pack(">B", OpCode.GETPEER.value)

def encode_givepeer(data: dict):
    peers = data.get("list_peers", [])
    peer_count = len(peers)
    encoded_peers = b""
    for peer in peers:
        ip_str, port = peer.split(":")
        ip_bytes = socket.inet_aton(ip_str)
        encoded_peers += struct.pack(">4sH", ip_bytes, int(port))
    return struct.pack(">BI", OpCode.GIVEPEER.value, peer_count) + encoded_peers

def encode_data(opcode: str, data: dict):
    try:
        return {
            "REGISTER": encode_register,
            "UNREGISTER": encode_unregister,
            "RESPONSE": encode_response,
            "GETPEER": encode_getpeer,
            "GIVEPEER": encode_givepeer
        }[opcode](data)
    except KeyError as e:
        logging.error(f"Invalid or missing opcode: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in encode_data: {e}")
    return None

# ======================= DECODERS =======================

def decode_register(payload: bytes):
    port, pieces_left = struct.unpack(">HI", payload)
    return {"opcode": "REGISTER", "port": port, "pieces_left": pieces_left}

def decode_unregister(payload: bytes):
    port = struct.unpack(">H", payload)[0]
    return {"opcode": "UNREGISTER", "port": port}

def decode_response(payload: bytes):
    response_len = struct.unpack(">I", payload[:4])[0]
    response = payload[4:4+response_len].decode("utf-8")

    ip_len_index = 4 + response_len
    ip_len = struct.unpack("B", payload[ip_len_index:ip_len_index+1])[0]

    ip = payload[ip_len_index+1:ip_len_index+1+ip_len].decode("utf-8")

    return {
        "opcode": "RESPONSE", 
        "response": response, 
        "client_ip": ip}

def decode_getpeer(_: bytes):
    return {"opcode": "GETPEER"}

def decode_givepeer(payload: bytes):
    peer_count = struct.unpack(">I", payload[:4])[0]
    peers = []
    offset = 4
    for _ in range(peer_count):
        ip_bytes, port = struct.unpack(">4sH", payload[offset:offset+6])
        ip_str = socket.inet_ntoa(ip_bytes)
        peers.append({"ip": ip_str, "port": port})
        offset += 6
    return {"opcode": "GIVEPEER", "peers": peers}

def decode_data(binary_data: bytes):
    try:
        opcode_value = struct.unpack(">B", binary_data[:1])[0]
        opcode = OpCode(opcode_value)
        payload = binary_data[1:]
        return {
            OpCode.REGISTER: decode_register,
            OpCode.UNREGISTER: decode_unregister,
            OpCode.RESPONSE: decode_response,
            OpCode.GETPEER: decode_getpeer,
            OpCode.GIVEPEER: decode_givepeer
        }[opcode](payload)
    except Exception as e:
        logging.error(f"Decode error: {e}")
        return None