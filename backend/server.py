import os
import csv
import threading
import time
from datetime import datetime
from flask import Flask, Response, jsonify
import cv2
import numpy as np

app = Flask(__name__)

# ----- Camera configuration -----
BASE_PATH = r"C:\Users\robec\WebstormProjects\ProyectoAdmin\monitoring-system\src\assets\sample_vids"
CAMERA_SOURCES = {
    f"camera_{i+1}": fr"{BASE_PATH}\vid{i+1}.mp4"
    for i in range(9)
}

detection_counts = {camera_id: 0 for camera_id in CAMERA_SOURCES}

# Directory to save csv summaries
SUMMARY_EXPORT_DIR = "csv_exports"
os.makedirs(SUMMARY_EXPORT_DIR, exist_ok=True)

# In-memory summary:
# {
#   "YYYY-MM-DD": {
#       "camera_1": {"00": N, ..., "23": N},
#       ...
#   }
# }
summary = {}  # Maps date -> camera_id -> hour ("HH") -> int

# ----- Person detector setup -----
hog = cv2.HOGDescriptor()
default_people_detector = getattr(cv2, "HOGDescriptor_getDefaultPeopleDetector")()
hog.setSVMDetector(default_people_detector)

def detect_people(frame):
    """Detect people and return list of bounding boxes."""
    (rects, _) = hog.detectMultiScale(frame, winStride=(4, 4), padding=(8, 8), scale=1.05)
    return [(x, y, x + w, y + h) for (x, y, w, h) in rects]

def generate_frames(camera_id):
    """Yields JPEG-encoded frames with count displayed, but no rectangles."""
    cap = cv2.VideoCapture(CAMERA_SOURCES[camera_id])
    global detection_counts

    if not cap.isOpened():
        print(f"Error: Unable to open source for {camera_id}")
        blank = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(blank, "Camera Not Found", (150, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        while True:
            ret, jpeg = cv2.imencode('.jpg', blank)
            if not ret:
                continue
            frame_bytes = jpeg.tobytes()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )
    else:
        while True:
            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop the video if it reaches the end
                continue
            bboxes = detect_people(frame)
            # Rectangles are not drawn here

            detection_counts[camera_id] = len(bboxes)

            # Draw detected people count at bottom right (with some padding)
            count_text = f"People: {len(bboxes)}"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            font_thickness = 2
            text_size, _ = cv2.getTextSize(count_text, font, font_scale, font_thickness)
            text_w, text_h = text_size
            height, width = frame.shape[:2]
            text_x = width - text_w - 20
            text_y = height - 20
            cv2.rectangle(frame, (text_x - 7, text_y - text_h - 7),
                                 (text_x + text_w + 7, text_y + 7), (0, 0, 0), -1)
            cv2.putText(frame, count_text, (text_x, text_y), font, font_scale, (0, 255, 255), font_thickness, cv2.LINE_AA)

            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = jpeg.tobytes()
            yield (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n'
            )

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    if camera_id not in CAMERA_SOURCES:
        return "Camera not found", 404
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_counts')
def get_detection_counts():
    return jsonify(detection_counts)

@app.route('/status')
def get_status():
    return jsonify({"status": "ok"})

def log_and_export_summary():
    """
    Every minute:
      - Updates per-hour per-camera summary for current day.
      - Appends/writes current daily summary to csv_exports/summary_<YYYY-MM-DD>.csv.
    At midnight, switches to new file.
    """
    global summary, detection_counts
    last_date_str = None
    while True:
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        hour_str = now.strftime("%H")

        # Init a new day's summary if needed
        if (last_date_str is None) or (date_str != last_date_str):
            summary.clear()
            summary[date_str] = {cam: {f"{h:02d}": 0 for h in range(24)} for cam in CAMERA_SOURCES}
            last_date_str = date_str

        # Add the current detection counts for each camera into the current hour
        for cam, count in detection_counts.items():
            summary[date_str][cam][hour_str] += count

        # Prepare & write the CSV
        csv_path = os.path.join(SUMMARY_EXPORT_DIR, f"summary_{date_str}.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Hour", "Camera", "Person_Count"])
            # Each row: hour, camera_id, cumulative count for that hour for that camera
            for cam in CAMERA_SOURCES:
                for hour in range(24):
                    hstr = f"{hour:02d}"
                    cnt = summary[date_str][cam][hstr]
                    writer.writerow([hstr, cam, cnt])

        # Sleep until start of next minute for accuracy
        now2 = datetime.now()
        sleep_secs = 60 - now2.second - (now2.microsecond / 1_000_000)
        if sleep_secs < 0.5:
            sleep_secs = 0.5
        time.sleep(sleep_secs)

if __name__ == '__main__':
    # Start the background summary logger thread
    threading.Thread(target=log_and_export_summary, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, threaded=True)