"""HTTP frame receiver"""
from flask import Blueprint, request, jsonify
import cv2
import numpy as np
from datetime import datetime
import json

from server.control.frame_queue import frame_queue
import server.config as config

receiver = Blueprint("receiver", __name__)

stats = {
    "total_received": 0,
    "total_success": 0,
    "total_errors": 0,
    "queue_full_count": 0
}

def check_camera_auth(req):
    """Check camera authentication"""
    if not config.REQUIRE_CAMERA_AUTH:
        return True
    
    camera_id = req.headers.get("camera-id")
    api_key = req.headers.get("API-Key")
    
    if not camera_id or not api_key:
        return False
    
    expected_key = config.AUTHORIZED_CAMERAS.get(camera_id)
    return expected_key == api_key

@receiver.route("/api/upload", methods=["POST"])
def upload_frame():
    """Receive frame via HTTP POST"""
    
    if not check_camera_auth(request):
        stats["total_errors"] += 1
        return jsonify({"error": "unauthorized"}), 401
    
    stats["total_received"] += 1
    
    if "image" not in request.files:
        stats["total_errors"] += 1
        return jsonify({"error": "no image field"}), 400
    
    if "metadata" not in request.form:
        stats["total_errors"] += 1
        return jsonify({"error": "no metadata field"}), 400
    
    file = request.files["image"]
    metadata_raw = request.form.get("metadata")
    metadata = json.loads(metadata_raw)

    if not file or not metadata:
        stats["total_errors"] += 1
        return jsonify({"error": "empty file or metadata"}), 400
    
    try:
        #decode image
        img_bytes = file.read()
        np_img = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        
        if frame is None:
            stats["total_errors"] += 1
            return jsonify({"error": "invalid image format"}), 400
        
        #check queue
        if frame_queue.full():
            stats["queue_full_count"] += 1
            return jsonify({
                "error": "queue full",
                "queue_size": frame_queue.qsize()
            }), 429
        
        #add to queue
        frame_queue.put([frame, metadata])
        stats["total_success"] += 1
        
        if stats["total_success"] % 10 == 0:
            print(f"📡 Frames received: {stats['total_success']} | Queue: {frame_queue.qsize()}")
        
        return jsonify({
            "ok": True,
            "timestamp": datetime.now().isoformat(),
            "queue_size": frame_queue.qsize(),
            "frame_shape": frame.shape
        }), 200
    
    except Exception as e:
        stats["total_errors"] += 1
        print(f"❌ Frame processing error: {e}")
        return jsonify({"error": "processing error", "details": str(e)}), 500