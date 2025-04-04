import socket
import json
import logging
import sys

from connection.message_protocol import *

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
                time.sleep(3)
        #if not return:
        logging.error(f"❌ Failed to connect to tracker after {3} attempts. Exiting.")
        sys.exit(0)
        return

    def send_register_request(self, tracker_URL, port, pieces_left):
        try:
            sock = self.connect_to_tracker(tracker_URL)
            if sock is None:
                return

            dictMsg = {
                "port": port,
                "pieces_left": pieces_left
            }

            biMsg = encode_data("REGISTER",dictMsg)
            send_msg(sock,biMsg)

            raw_response = recv_msg(sock)
            response = decode_data(raw_response)

            logging.info(f"Response from tracker: {response.get("response")}.")
            return 
        except Exception as e:
            logging.error(f"Error in send_register_request: {e}")
        finally:
            sock.close()

    def send_unregister_request(self, tracker_url, port):
        try:
            sock = self.connect_to_tracker(tracker_url)
            if sock is None:
                return

            dictMsg = {
                "port": port,
            }

            rawMsg = encode_data("REGISTER",dictMsg)
            send_msg(sock,rawMsg)

            raw_response = recv_msg(sock)
            response = decode_data(raw_response)

            logging.info(f"Response from tracker: {response.get("response")}")
            return 
        except Exception as e:
            logging.error(f"Error during unregistration: {e}")
            return 
        finally:
            sock.close()
    
    def request_list_peers(self, tracker_url):
        try:
            sock = self.connect_to_tracker(tracker_url)
            if sock is None:
                return
            dictMsg = {"a":"a"}
            rawMsg = encode_data("GETPEER",dictMsg)
            send_msg(sock, rawMsg)

            raw_response = recv_msg(sock)
            dict_response = decode_data(raw_response)
            if dict_response.get("opcode") == "GIVEPEER":
                peer_list = dict_response.get("peers")
                return peer_list
            else:
                raise Error(f"No found list_addrs")

            return dict_response
        except Exception as e:
            logging.error(f"Error during request list peers: {e}")
            return 
        finally:
            sock.close()

    def update_downloaded_pieces(self, piece):
        sock = self.connect_to_tracker()
        if sock == None:
            return
        

