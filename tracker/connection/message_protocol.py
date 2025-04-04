import struct
import logging
import json
import sys
from enum import Enum 

class OpCode(Enum):
    REGISTER = 0x01
    UNREGISTER = 0x02
    RESPONSE = 0x03
    GETPEER = 0x04
    GIVEPEER = 0x05

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
            pieces_left = data.get("pieces_left", 0)
            port = data.get("port")
            return struct.pack(">BHI", OpCode.REGISTER.value, port, pieces_left)
        
        if opcode == "UNREGISTER":
            return struct.pack(">BH", OpCode.UNREGISTER.value, data.get("port"))

        if opcode == "RESPONSE":
            response_msg = data.get("response", "").encode("utf-8")
            return struct.pack(">BI", OpCode.RESPONSE.value, len(response_msg)) + response_msg

        if opcode == "GETPEER":
            return struct.pack(">B", OpCode.GETPEER.value)

        if opcode == "GIVEPEER":
            peers = data.get("list_peers", [])
            peer_count = len(peers)
            serialized_peers = ''.join([f"{peer}:" for peer in peers]).encode('utf-8')
            return struct.pack(">B", OpCode.GIVEPEER.value) + struct.pack(">I", peer_count) + serialized_peers


    except KeyError as e:
        logging.error(f"Missing required data field: {e}")
    except (TypeError, struct.error) as e:
        logging.error(f"Encoding error: {e}")
        sys.exit()
    except Exception as e:
        logging.error(f"Unexpected error in encode_data: {e}")

    return None  #None if error

def decode_data(binary_data):
    try:
        opcode_value = struct.unpack(">B", binary_data[:1])[0]
        opcode = OpCode(opcode_value)

        if opcode == OpCode.REGISTER:

            port, pieces_left = struct.unpack(">HI", binary_data[1:7])
            return {
                "opcode": "REGISTER", 
                "port": port, 
                "pieces_left": pieces_left
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
        
        if opcode == OpCode.GETPEER:
            return {
                "opcode": "GETPEER"
            }
        
        if opcode == OpCode.GIVEPEER:
            peer_count = struct.unpack(">I", binary_data[1:5])[0]
            addrs = binary_data[5:].decode("utf-8").strip().split(":")
            peer_list = [{"ip": addrs[i], "port": int(addrs[i + 1])} for i in range(0, len(addrs)-1, 2)]
            return {
                "opcode": "GIVEPEER",
                "peers": peer_list
            }

        raise ValueError(f"Unknown opcode: {opcode}")  # Nếu opcode không hợp lệ

    except KeyError as e:
        logging.error(f"Missing required data field: {e}")
    except (TypeError, struct.error) as e:
        logging.error(f"Encoding error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in decode_data: {e}")

    return None  #None if error
