import socket
import json
import logging
import sys
import time

from protocol.tracker_protocol import *

class HandleTracker:
    def __init__(self):
        pass
    def connect_to_tracker(self,tracker_URL):
        for attempt in range(1,4):
            try:
                tracker_ip, tracker_port = tracker_URL.split(':')
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((tracker_ip, int(tracker_port)))
                return sock
            except Exception as e:
                logging.warning(f"⚠️ Attempt {attempt}: Cannot connect to tracker ({tracker_ip}:{tracker_port}) - {e}")
                time.sleep(1)
        #if not return:
        logging.error(f"❌ Failed to connect to tracker after {3} attempts. Exiting.")
        raise ConnectionError("No connection with tracker yet.")

    def send_register_request(self, tracker_URL, port, pieces_left):
        sock = None
        try:
            sock = self.connect_to_tracker(tracker_URL)
            if sock is None:
                return

            dictMsg = {
                "port": port,
                "pieces_left": pieces_left
            }

            biMsg = encode_register(dictMsg)
            send_msg(sock,biMsg)

            raw_response = recv_msg(sock)
            response = decode_data(raw_response)

            logging.info(f"Response from tracker: {response.get('response')}.")
            return response.get("client_ip")
        except Exception as e:
            logging.error(f"Error in send_register_request: {e}")
            raise
        finally:
            if sock:
                sock.close()


    def send_unregister_request(self, tracker_url, port):
        sock = None
        try:
            sock = self.connect_to_tracker(tracker_url)
            if sock is None:
                return

            dictMsg = {
                "port": port,
            }

            rawMsg = encode_unregister(dictMsg)
            send_msg(sock,rawMsg)

            raw_response = recv_msg(sock)
            response = decode_data(raw_response)

            logging.info(f"Response from tracker: {response.get('response')}")
            return 
        except Exception as e:
            logging.error(f"Error during unregistration: {e}")
            raise 
        finally:
            if sock:
                sock.close()
    
    def request_list_peers(self, tracker_url):
        sock = None
        try:
            sock = self.connect_to_tracker(tracker_url)
            if sock is None:
                return
            dictMsg = {"a":"a"}
            rawMsg = encode_getpeer(dictMsg)
            send_msg(sock, rawMsg)

            raw_response = recv_msg(sock)
            dict_response = decode_data(raw_response)
            if dict_response.get("opcode") == "GIVEPEER":
                peer_list = dict_response.get("peers")
                return peer_list
            else:
                raise Exception(f"Expected opcode 'GIVEPEER' but receive {dict_response.get('opcode')}")

        except Exception as e:
            logging.error(f"Error during request list peers: {e}")
            raise 
        finally:
            if sock:
                sock.close()

    def update_downloaded_pieces(self, piece):
        sock = self.connect_to_tracker()
        if sock == None:
            return
        

