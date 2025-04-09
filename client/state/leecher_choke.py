import logging

from state.choke_strategy_state import ChokeStrategyState

class LeecherState(ChokeStrategyState):
    
    def select_peers_to_unchoke(self, Peer_manager):
        try:
            interested_peers = Peer_manager.get_interested_peers()
            if not interested_peers:
                logging.debug("No interested peers available for unchoking")
                return []

            # Sort peers by download speed (descending) and remove duplicates
            unique_peers = list({peer.id: peer for peer in interested_peers}.values())
            sorted_peers = sorted(unique_peers, 
                                key=lambda p: p.download_speed, 
                                reverse=True)

            unchoked_peers = []
            
            # Select top downloader if available
            if sorted_peers:
                top_downloader = sorted_peers[0]
                unchoked_peers.append(top_downloader)
                logging.debug(f"Selected top downloader: {top_downloader.id} "
                            f"(speed: {top_downloader.download_speed} B/s)")

            # Optimistic unchoking - select random peer from remaining
            remaining_peers = [p for p in sorted_peers[1:] if p not in unchoked_peers]
            if remaining_peers:
                optimistic_peer = random.choice(remaining_peers)
                unchoked_peers.append(optimistic_peer)
                logging.debug(f"Selected optimistic unchoke: {optimistic_peer.id}")

            return unchoked_peers

        except Exception as e:
            logging.error(f"Error in select_peers_to_unchoke: {str(e)}", exc_info=True)
            return []


    '''
    def select_peers_to_unchoke(self, Peer_manager):
        return Peer_manager.active_peers    #for test
'''