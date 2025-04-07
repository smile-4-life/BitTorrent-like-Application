import struct
import socket
import logging
from enum import Enum

class PeerOpCode(Enum):
    HANDSHAKE = 0x10
    BITFIELD = 0x11

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

#===== CORE =====
def encode_msg(opcode: str, data: dict):
    try:
        return {
            "HANDSHAKE": encode_handshake(data),
            "BITFIELD": encode_bitfield(data)
        }[opcode](data)
    except KeyError as e:
        logging.error(f"Invalid or missing opcode: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in encode_data: {e}")
    return None

def decode_raw_msg(binary_data: bytes):
    try:
        opcode_value = struct.unpack(">B", binary_data[:1])[0]
        opcode = PeerOpCode(opcode_value)
        payload = binary_data[1:]
        return {
            PeerOpCode.HANDSHAKE: decode_handshake,
            PeerOpCode.BITFIELD: decode_bitfield
        }[opcode](payload)
    except Exception as e:
        logging.error(f"Decode error: {e}")
        return None

# HANDSHAKE
def encode_handshake(data):
    return struct.pack('>B20sH', PeerOpCode.HANDSHAKE.value, data.get("peer_id").encode('utf-8'), data.get("peer_port"))

def decode_handshake(data: bytes):
    peer_id, peer_port = struct.unpack('>20sH',data)
    return {
        "opcode": "HANDSHAKE",
        "peer_id": peer_id,
        "peer_port": peer_port
    }

# BITFIELD
def encode_bitfield(data):
    bit_str = data.get("str_bitfield")
    padded = bit_str.zfill(((len(bit_str) + 7) // 8) * 8)
    chunks = [padded[i:i+8] for i in range(0, len(padded), 8)]
    byte_list = [int(chunk, 2).to_bytes(1, 'big') for chunk in chunks]
    bitfield_bytes = b''.join(byte_list)

    return struct.pack('>BI', PeerOpCode.BITFIELD.value, len(bit_str)) + bitfield_bytes

def decode_bitfield(data):
    bit_len = struct.unpack('>I',data[0:4])[0]
    bitfield_payload = data[4:]
    full_bit_str = ''.join(f'{byte:08b}' for byte in bitfield_payload)
    return {
        "opcode": "BITFIELD",
        "str_bitfield": full_bit_str[-bit_len:]
    }