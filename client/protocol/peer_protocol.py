import struct
import socket
import logging
from enum import Enum

class PeerOpCode(Enum):
    HANDSHAKE = 0x10
    REQUEST = 0x11
    PIECE = 0x12
    HAVE = 0x13
    # Add more opcodes as needed...

def encode_handshake(peer_id: str):
    try:
        peer_id_bytes = peer_id.encode('utf-8')
        return struct.pack('>B', PeerOpCode.HANDSHAKE.value) + struct.pack('>I', len(peer_id_bytes)) + peer_id_bytes
    except Exception as e:
        logging.error(f"Error encoding handshake: {e}")

def decode_handshake(data: bytes):
    try:
        length = struct.unpack('>I', data[1:5])[0]
        peer_id = data[5:5+length].decode('utf-8')
        return {
            "opcode": "HANDSHAKE", 
            "peer_id": peer_id
            }
    except Exception as e:
        logging.error(f"Error decoding handshake: {e}")

def encode_request(piece_index: int):
    return struct.pack('>BI', PeerOpCode.REQUEST.value, piece_index)

def decode_request(data: bytes):
    piece_index = struct.unpack('>I', data[1:5])[0]
    return {
        "opcode": "REQUEST", 
        "piece_index": piece_index
        }

def encode_piece(piece_index: int, data: bytes):
    return struct.pack('>BI', PeerOpCode.PIECE.value, piece_index) + struct.pack('>I', len(data)) + data

def decode_piece(data: bytes):
    piece_index = struct.unpack('>I', data[1:5])[0]
    length = struct.unpack('>I', data[5:9])[0]
    piece_data = data[9:9+length]
    return {
        "opcode": "PIECE", 
        "piece_index": piece_index, 
        "data": piece_data}

def encode_have(piece_index: int):
    return struct.pack('>BI', PeerOpCode.HAVE.value, piece_index)

def decode_have(data: bytes):
    piece_index = struct.unpack('>I', data[1:5])[0]
    return {
        "opcode": "HAVE", 
        "piece_index": piece_index}

def decode_peer_message(data: bytes):
    opcode = data[0]
    if opcode == PeerOpCode.HANDSHAKE.value:
        return decode_handshake(data)
    elif opcode == PeerOpCode.REQUEST.value:
        return decode_request(data)
    elif opcode == PeerOpCode.PIECE.value:
        return decode_piece(data)
    elif opcode == PeerOpCode.HAVE.value:
        return decode_have(data)
    else:
        logging.warning(f"Unknown peer message opcode: {opcode}")
        return None
