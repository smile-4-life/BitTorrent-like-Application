import socket
import logging
import struct
import time
from protocol.peer_protocol import *  # Import peer-related protocol methods

class HandlePeer:
    def __init__(self):
        pass

    def receive_message(self, sock):
        try:
            raw_msg = recv_msg(sock)
            msg = decode_raw_msg(raw_msg)
            logging.info(f"Received {msg['opcode']} message from {sock.getpeername()}")
            logging.debug(f"{msg}")
            return msg
        except Exception as e:
            logging.error(f"Error during listen: {e}")
            return None


    def connect_to_addr(self, addr):
        for attempt in range(1, 4):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((addr[0], addr[1]))
                return sock
            except Exception as e:
                logging.warning(f"⚠️ Attempt {attempt}: Cannot connect to peer ({addr[0]}:{addr[1]}) - {e}")
                time.sleep(1)
        logging.error(f"❌ Failed to connect to peer {addr[0]}:{addr[1]} after 3 attempts.")
        raise ConnectionError(f"Unable to connect to peer {addr[0]}:{addr[1]}")
    
    def connect_to_peer(self, peer):
        addr = (peer.ip, peer.port)
        return self.connect_to_addr(addr)
    

    def send_unchoke(sock, peer):
        unchoke_msg = encode_unchoked()
        send_msg(sock, choke_msg)

    def send_choke(sock, peer):
        choke_msg = encode_choked()
        send_msg(sock, choke_msg)