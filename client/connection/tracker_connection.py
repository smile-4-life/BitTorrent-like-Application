import socket
import json
import logging
from connection.message_protocol import *

class HandleTracker:
    def __init__(self):

    def connect_to_tracker(self):
        try:
            tracker_ip, tracker_port = self.client_observer.tracker_URL.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((tracker_ip, int(tracker_port)))
            return sock
        except Exception as e:
            logging.error(f"Failed to connect to tracker: {e}")
            return None

    def send_register_request(self, list_pieces):
        sock = self.connect_to_tracker()
        try:
            dictMsg = {
                "port": self.client_observer.port,
                "piece_bitfield": list_pieces
            }
            biMsg = encode_data("REGISTER",dictMsg)
            send_msg(sock,biMsg)
            raw_response = recv_msg(sock)
            response = decode_data(raw_response)
            logging.info(f"Response from tracker: {response.get("response")}")
            return None
        except Exception as e:
            logging.error(f"Error during registration: {e}")
            return None
        finally:
            sock.close()

    def send_unregister_request(self,tracker_url, client_ip, client_port):
        sock = connect_to_tracker(tracker_url)
        if sock is None:
            return

        try:
            sock.send(f"UNREGISTER {client_ip} {client_port}".encode())
            response = trackersock_socket.recv(1024).decode()
            logging.info(response)
        except Exception as e:
            logging.error(f"Error unregistering: {e}")
        finally:
            sock.close()

    def send_bit_field(self,sock, piece_bitfield):
        try:
            response = sock.recv(1024).decode()
            if response == "REQUEST_HASH_LIST":
                data = json.dumps(list(piece_bitfield.keys())).encode() if piece_bitfield else "BLANK".encode()
                send_msg(sock, data)
                logging.info(f"Sent hash list to tracker: {len(piece_bitfield)} pieces")
        except Exception as e:
            logging.error(f"Error uploading hash list: {e}")
