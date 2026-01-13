"""Frame queue for producer-consumer pattern"""
from queue import Queue
import server.config as config

frame_queue = Queue(maxsize=100)

if config.VERBOSE:
    print("📥 Frame queue initialized")