import logging
from connection.message_protocol import send_msg, recv_msg

class HandleClient:
    """Handles interactions between tracker and clients."""
    def __init__(self, tracker_observer):
        self.tracker_observer = tracker_observer

    def handle_register(self, client_ip, client_port, client_socket):
        """Handles peer registration."""
        client_addr = f"{client_ip}:{client_port}"
        if self.tracker_observer.register_peer(client_addr):
            client_socket.send(f"REGISTERED:{client_ip}:{client_port}".encode())
        else:
            client_socket.send(f"ALREADY_REGISTERED:{client_ip}:{client_port}".encode())

    def handle_update_piece(self, client_ip, client_port, hash_value):
        """Updates the piece list for a registered peer."""
        client_addr = f"{client_ip}:{client_port}"
        self.tracker_observer.update_piece(client_addr, hash_value)

    def handle_get_list_peer(self, client_socket):
        """Sends the list of peers to the requesting client."""
        peers = self.tracker_observer.get_peers()
        if peers:
            send_msg(client_socket, str(peers))
            logging.info("📤 Sent list of peers to client.")
        else:
            send_msg(client_socket, "BLANK")
            logging.warning("⚠️ Sent empty peer list.")

    def handle_unregister(self, client_ip, client_port, client_socket):
        """Handles peer unregistration."""
        client_addr = f"{client_ip}:{client_port}"
        self.tracker_observer.unregister_peer(client_addr)
        client_socket.send(b"UNREGISTERED")
        client_socket.close()
