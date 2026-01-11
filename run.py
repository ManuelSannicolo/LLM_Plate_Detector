"""Entry point - starts web server and processing"""
from server.web.appWeb import app
import threading
from server.main import processing_thread

if __name__ == "__main__":
    print("🚀 Starting system")
    
    #start processing thread
    processing = threading.Thread(target=processing_thread, daemon=True)
    processing.start()
    
    #start web server
    print("🌐 Starting web server")
    app.run(port=5000, debug=False)