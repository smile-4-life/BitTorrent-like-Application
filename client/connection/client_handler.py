import socket
import json
import logging
from connection.message_protocol import send_msg, recv_msg

def connect_to_tracker(tracker_url):
    """Establish a connection to the tracker and return the socket."""
    try:
        tracker_ip, tracker_port = tracker_url.split(':')
        tracker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tracker_socket.connect((tracker_ip, int(tracker_port)))
        return tracker_socket
    except Exception as e:
        logging.error(f"Failed to connect to tracker: {e}")
        return None

def send_register_request(tracker_socket, client_ip, client_port):
    """Send a REGISTER request to the tracker and return the assigned address."""
    try:
        tracker_socket.send(f"REGISTER {client_ip} {client_port}".encode())
        response = tracker_socket.recv(1024).decode().split(":")
        logging.info(response[0])
        if len(response) >= 3:
            return f"{response[1]}:{response[2]}"
        return None
    except Exception as e:
        logging.error(f"Error during registration: {e}")
        return None

def send_unregister_request(tracker_url, client_ip, client_port):
    """Send an UNREGISTER request to the tracker."""
    tracker_socket = connect_to_tracker(tracker_url)
    if tracker_socket is None:
        return

    try:
        tracker_socket.send(f"UNREGISTER {client_ip} {client_port}".encode())
        response = tracker_socket.recv(1024).decode()
        logging.info(response)
    except Exception as e:
        logging.error(f"Error unregistering: {e}")
    finally:
        tracker_socket.close()

def send_hash_list(tracker_socket, hash_dict):
    """Send available piece hashes to the tracker."""
    try:
        response = tracker_socket.recv(1024).decode()
        if response == "REQUEST_HASH_LIST":
            data = json.dumps(list(hash_dict.keys())).encode() if hash_dict else "BLANK".encode()
            send_msg(tracker_socket, data)
            logging.info(f"Sent hash list to tracker: {len(hash_dict)} pieces")
    except Exception as e:
        logging.error(f"Error uploading hash list: {e}")
