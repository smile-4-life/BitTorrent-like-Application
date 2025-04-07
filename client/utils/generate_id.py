import hashlib
import random
import time
import uuid

def generate_peer_id(client_name="PYTORRENT"):
    #format: -PY0001-<random_bytes>
    # Client prefix (6 chars): -PY0001-
    prefix = f"-{client_name[:2].upper()}0001-"

    # Random
    unique_data = f"{uuid.getnode()}{time.time()}{random.randint(0, 1 << 32)}"
    hash_suffix = hashlib.sha1(unique_data.encode()).hexdigest()[:12]  # 12 chars

    peer_id = (prefix + hash_suffix)[:20]  # Ensure exactly 20 characters
    return peer_id
