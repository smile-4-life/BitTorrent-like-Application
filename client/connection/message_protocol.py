import struct
import logging
import json
from enum import Enum 

class OpCode(Enum):
    REGISTER = 0x01
    UNREGISTER = 0x02
    UPDATE = 0x03
    SENDDICT = 0x04
    RESPONSE = 0x05

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

def encode_data(opcode: str, data: dict):
    try:
        if opcode == "REGISTER":
            list_pieces = data.get("list_pieces", [])
            pieces_json = json.dumps(list_pieces).encode("utf-8")
            return struct.pack(">BHI", OpCode.REGISTER.value, data.get("port"), len(pieces_json)) + pieces_json
        
        if opcode == "UNREGISTER":
            return struct.pack(">BH", OpCode.UNREGISTER.value, data.get("port"))

        if opcode == "RESPONSE":
            response_msg = data.get("response", "").encode("utf-8")
            return struct.pack(">BI", OpCode.RESPONSE.value, len(response_msg)) + response_msg

        raise ValueError(f"Unknown opcode: {opcode}")  # Nếu opcode không hợp lệ

    except KeyError as e:
        logging.error(f"Missing required data field: {e}")
    except (TypeError, struct.error) as e:
        logging.error(f"Encoding error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in encode_data: {e}")

    return None  #None if error

def decode_data(binary_data):
    try:
        opcode_value = struct.unpack(">B", binary_data[:1])[0]
        opcode = OpCode(opcode_value)

        if opcode == OpCode.REGISTER:

            port, list_pieces_length = struct.unpack(">HI", binary_data[1:7])

            list_pieces_json = binary_data[7:7 + list_pieces_length].decode("utf-8")
            list_pieces = json.loads(list_pieces_json)  # Convert JSON back to list
            return {
                "opcode": "REGISTER", 
                "port": port, 
                "list_pieces": list_pieces
                }
        
        if opcode == OpCode.UNREGISTER:
            return {
                "opcode": "UNREGISTER", 
                "port": struct.unpack(">H", binary_data[1:3])[0]
                }

        if opcode == OpCode.RESPONSE:
            response_length = struct.unpack(">I", binary_data[1:5])[0]
            response_data = binary_data[5:5 + response_length].decode("utf-8")
            return {
                "opcode": "RESPONSE", 
                "response": response_data}

        raise ValueError(f"Unknown opcode: {opcode}")  # Nếu opcode không hợp lệ

    except KeyError as e:
        logging.error(f"Missing required data field: {e}")
    except (TypeError, struct.error) as e:
        logging.error(f"Encoding error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in encode_data: {e}")

    return None  #None if error
