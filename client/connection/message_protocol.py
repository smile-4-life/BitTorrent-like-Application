import struct
import socket
import logging
import json
from enum import Enum 

class OpCode(Enum):
    REGISTER = 0x01
    UNREGISTER = 0x02
    RESPONSE = 0x03
    GETPEER = 0x04
    GIVEPEER = 0x05

def send_msg(sock, msg:bytes):
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

def recvall(sock, n:int):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            logging.error(f"Failed to receive expected data. Only {len(data)} bytes received, but {n} expected.")
            raise ConnectionError("Connection was closed or failed to receive data")
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
            encoded_peers = b""
            for peer in peers:
                ip_str, port = peer.split(":")
                ip_bytes = socket.inet_aton(ip_str)  # 4 bytes
                encoded_peers += struct.pack(">4sH", ip_bytes, int(port))  # 6 bytes per peer

            return struct.pack(">BI", OpCode.GIVEPEER.value, peer_count) + encoded_peers

    except KeyError as e:
        logging.error(f"Missing required data field: {e}")
    except (TypeError, struct.error) as e:
        logging.error(f"Encoding error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in encode_data: {e}")
    return None

def decode_data(binary_data:bytes):
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
            peers = []
            offset = 5
            for _ in range(peer_count):
                ip_bytes, port = struct.unpack(">4sH", binary_data[offset:offset + 6])
                ip_str = socket.inet_ntoa(ip_bytes)
                peers.append({"ip": ip_str, "port": port})
                offset += 6
            return {
                "opcode": "GIVEPEER", 
                "peers": peers
                }

        raise ValueError(f"Unknown opcode: {opcode}")  # for debug

    except KeyError as e:
        logging.error(f"Missing required data field: {e}")
    except (TypeError, struct.error) as e:
        logging.error(f"Encoding error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in decode_data: {e}")

    return None  #None if error
