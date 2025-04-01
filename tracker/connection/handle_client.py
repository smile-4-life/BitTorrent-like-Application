import logging
from connection.message_protocol import *

class HandleClient:
    """Handles interactions between tracker and clients."""
    def __init__(self, tracker_object:object):
        self.tracker_object = tracker_object

    def handle_register(self, client_socket, client_ip, dictMsg):
        client_port = dictMsg.get("port")
        list_pieces = dictMsg.get("list_pieces")
        if client_port is None:
            logging.warning(f"Invalid REGISTER request from {client_ip}: {dictMsg}")
            return

        client_addr =(client_ip,client_port)
        if self.tracker_object.register_peer(client_addr, list_pieces):
            response = {"response": "REGISTER SUCCESS"}
        else:
            response = {"response": "ALREADY REGISTERED"}

        raw_response = encode_data("RESPONSE", response)
        send_msg(client_socket, raw_response)

    def handle_unregister(self, client_ip, client_port, client_socket):
        """Handles peer unregistration."""
        client_addr =(client_ip,client_port)
        self.tracker_object.unregister_peer(client_addr)
        client_socket.send(b"UNREGISTERED")
        client_socket.close()

    def handle_update_piece(self, client_ip, client_port, hash_value):
        client_addr = f"{client_ip}:{client_port}"
        self.tracker_object.update_piece(client_addr, hash_value)

    def handle_get_list_peer(self, client_socket):
        peers = self.tracker_object.get_peers()
        if peers:
            send_msg(client_socket, str(peers))
            logging.info("📤 Sent list of peers to client.")
        else:
            send_msg(client_socket, "BLANK")
            logging.warning("⚠️ Sent empty peer list.")
