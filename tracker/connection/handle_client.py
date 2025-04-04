import logging
from connection.message_protocol import *
from subject.peer_factory import PeerFactory

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

        dict_response = {"response": "REGISTER SUCCESSFUL"}
        raw_response = encode_data("RESPONSE", dict_response)
        send_msg(client_socket, raw_response)

        return peer
    
    def handle_get_peers(self, client_socket, peers):
        list_peer_addrs = list(f"{peer.ip}:{peer.port}" for peer in peers)

        dict_response = {"list_peers": list_peer_addrs}
        raw_response = encode_data("GIVEPEER", dict_response)
        send_msg(client_socket, raw_response)
        return
        
'''
    def handle_unregister(self, client_ip, client_port, client_socket):
        """Handles peer unregistration."""
        client_addr =(client_ip,client_port)
        self.tracker_object.unregister_peer(client_addr)
        client_socket.send(b"UNREGISTERED")
        client_socket.close()
'''

'''    
    def handle_update_piece(self, client_ip, client_port, hash_value):
        client_addr = f"{client_ip}:{client_port}"
        self.tracker_object.update_piece(client_addr, hash_value)
'''

'''    
    def handle_get_list_peer(self, client_socket):
        peers = self.tracker_object.get_peers()
        if peers:
            send_msg(client_socket, str(peers))
            logging.info("📤 Sent list of peers to client.")
        else:
            send_msg(client_socket, "BLANK")
            logging.warning("⚠️ Sent empty peer list.")
'''