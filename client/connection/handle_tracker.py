import socket
import json
import logging
from connection.message_protocol import *

class HandleTracker:
    def __init__(self, client_observer:object):
        self.client_observer = client_observer

    def connect_to_tracker(self,tracker_url):
        try:
            tracker_ip, tracker_port = tracker_url.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((tracker_ip, int(tracker_port)))
            return sock
        except Exception as e:
            logging.error(f"Failed to connect to tracker: {e}")
            return None

    def send_register_request(self):
        sock = self.connect_to_tracker(self.client_observer.tracker_URL)
        try:
            dictMsg = {"port": self.client_observer.port}
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

    def send_hash_list(sock, hash_dict):
        try:
            response = sock.recv(1024).decode()
            if response == "REQUEST_HASH_LIST":
                data = json.dumps(list(hash_dict.keys())).encode() if hash_dict else "BLANK".encode()
                send_msg(sock, data)
                logging.info(f"Sent hash list to tracker: {len(hash_dict)} pieces")
        except Exception as e:
            logging.error(f"Error uploading hash list: {e}")
