import logging
from protocol.tracker_protocol import *
from factory.peer_factory import PeerFactory

class HandleClient:
    """Handles interactions between tracker and clients."""
    def __init__(self):
        pass

    def handle_register(self, client_socket, client_ip, dictMsg):
        client_port = dictMsg.get("port")
        pieces_left = dictMsg.get("pieces_left")
        if client_port is None or pieces_left is None:
            logging.warning(f"Invalid REGISTER request from {client_ip}: {dictMsg}")
            return None

        peer_factory = PeerFactory()
        peer = peer_factory.new_peer(client_ip, client_port, pieces_left)

        dict_response = {
            "response": "REGISTER SUCCESSFUL",
            "client_ip": client_ip
            }
        raw_response = encode_response(dict_response)
        send_msg(client_socket, raw_response)

        return peer
    
    def handle_get_peers(self, client_socket, peers):
        list_peer_addrs = list(f"{peer.ip}:{peer.port}" for peer in peers)

        dict_response = {"list_peers": list_peer_addrs}
        raw_response = encode_givepeer(dict_response)
        send_msg(client_socket, raw_response)
        return
        
    def handle_unregister(self, client_socket, client_ip, dictMsg):
        client_port = dictMsg.get("port")
        if client_port is None:
            logging.warning(f"Invalid UNREGISTER request from {client_ip}: {dictMsg}")
            return None

        peer_factory = PeerFactory()
        peer = peer_factory.new_peer(client_ip, client_port, 1)

        dict_response = {"response": "UNREGISTER SUCCESSFUL"}
        raw_response = encode_response(dict_response)
        send_msg(client_socket, raw_response)

        return peer