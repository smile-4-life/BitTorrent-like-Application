import struct
import socket
import logging
from enum import Enum

class PeerOpCode(Enum):
    HANDSHAKE = 0x10
    BITFIELD = 0x11
    INTERESTED = 0x12
    CHOKED = 0x13
    UNCHOKED = 0x14
    REQUEST = 0x15
    PIECE = 0x16
    DONE = 0x17

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
            "HANDSHAKE": encode_handshake,
            "BITFIELD": encode_bitfield,
            "INTERESTED": encode_interested,
            "CHOKED": encode_choked,
            "UNCHOKED": encode_unchoked,
            "REQUEST": encode_request,
            "PIECE": encode_piece,
            "DONE": encode_done
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
        payload = binary_data[1:] if len(binary_data) > 1 else None

        return {
            PeerOpCode.HANDSHAKE: decode_handshake,
            PeerOpCode.BITFIELD: decode_bitfield,
            PeerOpCode.INTERESTED: decode_interested,
            PeerOpCode.CHOKED: decode_choked,
            PeerOpCode.UNCHOKED: decode_unchoked,
            PeerOpCode.REQUEST: decode_request,
            PeerOpCode.PIECE: decode_piece,
            PeerOpCode.DONE: decode_done
        }[opcode](payload)
    except Exception as e:
        logging.error(f"Decode error: {e}")
        raise
        return None

# HANDSHAKE
def encode_handshake(data):
    return struct.pack('>B20sH', PeerOpCode.HANDSHAKE.value, data.get("peer_id").encode('utf-8'), data.get("peer_port"))

def decode_handshake(data: bytes):
    peer_id, peer_port = struct.unpack('>20sH',data)
    return {
        "opcode": "HANDSHAKE",
        "peer_id": peer_id.decode('utf-8'),
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

# INTERESTED

def encode_interested(data):
    return struct.pack('>B20sH', PeerOpCode.INTERESTED.value, data.get("peer_id").encode('utf-8'), data.get("peer_port"))

def decode_interested(data):
    peer_id, peer_port = struct.unpack('>20sH',data)
    return {
        "opcode": "INTERESTED",
        "peer_id": peer_id.decode('utf-8'),
        "peer_port": peer_port
    }
    
# CHOKE

def encode_choked(data=None):
    print("innter")
    if data is None:
        print("None quick")
        return _encode_choked_quick()
    else:
        print("no NONE ID")
        return _encode_choked_id(data)

def _encode_choked_quick():
    return struct.pack('>B', PeerOpCode.CHOKED.value)

def _encode_choked_id(data):
    return struct.pack('>B20s', PeerOpCode.CHOKED.value, data.get("peer_id").encode('utf-8'))

def decode_choked(data=None):
    if not data:
        return _decode_choked_quick()
    else:
        return _decode_choked_id(data)

def _decode_choked_quick(data=None):
    return {
        "opcode": "CHOKED"
    }

def _decode_choked_id(data):
    peer_id = struct.unpack('>20s',data)[0]
    return {
        "opcode": "CHOKED",
        "peer_id": peer_id.decode('utf-8')
    }

# UNCHOKED

def encode_unchoked(data=None):
    if data is None:
        return _encode_unchoked_quick()
    else:
        return _encode_unchoked_id(data)

def _encode_unchoked_quick():
    return struct.pack('>B', PeerOpCode.UNCHOKED.value)

def _encode_unchoked_id(data):
    return struct.pack('>B20s', PeerOpCode.UNCHOKED.value, data.get("peer_id").encode('utf-8'))

def decode_unchoked(data=None):
    if data is None:
        return _decode_unchoked_quick()
    else:
        return _decode_unchoked_id(data)

def _decode_unchoked_quick():
    return {
        "opcode": "UNCHOKED"
    }

def _decode_unchoked_id(data):
    peer_id = struct.unpack('>20s',data)[0]
    return {
        "opcode": "UNCHOKED",
        "peer_id": peer_id.decode('utf-8')
    }

# REQUEST
def encode_request(data):
    return struct.pack('>BI20s', PeerOpCode.REQUEST.value, data.get("piece_index"), data.get("peer_id").encode('utf-8'))

def decode_request(data):
    piece_index, peer_id = struct.unpack('>I20s',data)
    return {
        "opcode": "REQUEST",
        "piece_index": piece_index,
        "peer_id": peer_id.decode('utf-8')
    }

# PIECES
def encode_piece(data):
    piece = data.get("piece")
    length = len(piece)
    return struct.pack('>BII', PeerOpCode.PIECE.value, data.get("piece_index"), length) + piece

def decode_piece(data):
    print("check here")
    piece_index, piece_length = struct.unpack('>II', data[:8])
    print(f"index; {piece_index}, length: {piece_length}")
    piece = data[9:9+piece_length]
    return {
        "opcode": "PIECE",
        "piece_index": piece_index,
        "piece": piece
    }

# DONE
def encode_done(data=None):
    return struct.pack('>B',PeerOpCode.DONE.value)

def decode_done(data=None):
    return {
        "opcode": "DONE"
    }