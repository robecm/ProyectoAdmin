# backend/server.py
from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import os
from ultralytics import YOLO
import threading
import time
import queue
from collections import deque

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Global variables
video_sources = {}
detection_results = {}
client_connections = {}
max_connections = 20  # Limit total connections

# Directory with sample videos
VIDEO_DIR = r'C:\Users\robec\WebstormProjects\ProyectoAdmin\monitoring-system\src\assets\sample_vids'

# Load YOLO model - use nano for better performance
model = YOLO('yolov8n.pt')  # Using smaller model for speed

class VideoProcessor:
    def __init__(self, camera_id, video_path):
        self.camera_id = camera_id
        self.video_path = video_path
        self.processed_frame = None
        self.count = 0
        self.running = False
        self.lock = threading.Lock()
        self.frame_buffer = deque(maxlen=5)  # Store a few frames to avoid stuttering
        self.process_every = 4  # Process every Nth frame
        self.frame_count = 0

    def start(self):
        self.running = True
        # Start separate threads for reading and processing
        threading.Thread(target=self.process_video, daemon=True).start()

    def process_video(self):
        """Main processing thread that handles the video loop"""
        last_processed_time = 0
        processing_interval = 0.25  # Process at most 4 times per second

        while self.running:
            try:
                cap = cv2.VideoCapture(self.video_path)
                if not cap.isOpened():
                    print(f"Error: Could not open video {self.video_path}")
                    time.sleep(5)  # Wait before retry
                    continue

                # Lower resolution for better performance
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

                # Process frames in a loop
                while self.running:
                    ret, frame = cap.read()
                    if not ret:
                        print(f"End of video {self.camera_id}, reopening...")
                        break  # End of video, will reopen

                    self.frame_count += 1
                    current_time = time.time()

                    # Decide whether to process this frame with YOLO or just copy the previous results
                    should_process = (self.frame_count % self.process_every == 0 and
                                     current_time - last_processed_time >= processing_interval)

                    if should_process:
                        # Resize for faster processing
                        frame_small = cv2.resize(frame, (320, 240))

                        # Process with YOLO
                        results = model(frame_small, conf=0.5, classes=0)  # Only detect people
                        count = len(results[0].boxes)

                        # Scale factor for drawing boxes on the original frame
                        scale_x = frame.shape[1] / frame_small.shape[1]
                        scale_y = frame.shape[0] / frame_small.shape[0]

                        # Draw bounding boxes
                        for result in results:
                            for box in result.boxes:
                                x1, y1, x2, y2 = map(int, box.xyxy[0])
                                # Scale coordinates
                                x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
                                y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

                        # Update count and last processed time
                        self.count = count
                        last_processed_time = current_time
                        detection_results[self.camera_id] = count

                    # Add count text to the frame
                    cv2.putText(frame, f'Personas: {self.count}', (20, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    # Update shared frame with lock
                    with self.lock:
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]  # Lower quality for speed
                        _, buffer = cv2.imencode('.jpg', frame, encode_param)
                        encoded_frame = buffer.tobytes()
                        self.processed_frame = encoded_frame
                        self.frame_buffer.append(encoded_frame)

                # Close and prepare to reopen video
                cap.release()

            except Exception as e:
                print(f"Error in camera {self.camera_id}: {str(e)}")
                time.sleep(1)  # Wait before retry

    def get_frame(self):
        with self.lock:
            if not self.frame_buffer:
                return self.processed_frame
            return self.frame_buffer[-1]  # Return most recent frame

    def stop(self):
        self.running = False

def initialize_videos():
    """Initialize video processors for all cameras"""
    # Check if directory exists
    if not os.path.exists(VIDEO_DIR):
        print(f"Warning: Video directory {VIDEO_DIR} not found. Using synthetic videos.")
        # Create synthetic videos if directory doesn't exist
        for i in range(9):
            camera_id = f"camera_{i+1}"
            processor = SyntheticVideoProcessor(camera_id)
            video_sources[camera_id] = processor
            processor.start()
            print(f"Started synthetic camera {camera_id}")
        return

    # Get video files
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.lower().endswith(('.mp4', '.avi', '.mov'))]
    print(f"Found {len(video_files)} video files in {VIDEO_DIR}")

    # If no videos found, use synthetic
    if not video_files:
        print("No video files found. Using synthetic videos.")
        for i in range(9):
            camera_id = f"camera_{i+1}"
            processor = SyntheticVideoProcessor(camera_id)
            video_sources[camera_id] = processor
            processor.start()
            print(f"Started synthetic camera {camera_id}")
        return

    # If less than 9 videos, use duplicates to fill
    while len(video_files) < 9:
        video_files.extend(video_files[:9-len(video_files)])

    # Initialize processors for up to 9 cameras
    for i in range(min(9, len(video_files))):
        camera_id = f"camera_{i+1}"
        video_path = os.path.join(VIDEO_DIR, video_files[i])

        try:
            processor = VideoProcessor(camera_id, video_path)
            video_sources[camera_id] = processor
            processor.start()
            print(f"Started camera {camera_id} with video {video_files[i]}")
        except Exception as e:
            print(f"Error initializing camera {camera_id}: {str(e)}")
            # Fall back to synthetic if there's an error
            processor = SyntheticVideoProcessor(camera_id)
            video_sources[camera_id] = processor
            processor.start()
            print(f"Started synthetic camera {camera_id} as fallback")

class SyntheticVideoProcessor:
    # Same as your existing SyntheticVideoProcessor but with a frame buffer
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.processed_frame = None
        self.frame_buffer = deque(maxlen=10)  # Buffer multiple frames
        self.count = 0
        self.running = False
        self.lock = threading.Lock()
        self.frame_counter = 0

    def start(self):
        self.running = True
        threading.Thread(target=self.generate_frames, daemon=True).start()

    def generate_frames(self):
        while self.running:
            # Create synthetic frame
            self.frame_counter += 1
            frame = np.zeros((360, 640, 3), dtype=np.uint8)  # Lower resolution

            # Add some movement
            timestamp = time.time()
            offset_x = int(100 * np.sin(timestamp))
            offset_y = int(50 * np.cos(timestamp))

            # Random number of "people"
            num_boxes = np.random.randint(1, 6)
            self.count = num_boxes

            # Draw boxes
            for i in range(num_boxes):
                x1 = (100 + i * 60 + offset_x) % 540
                y1 = (100 + i * 40 + offset_y) % 280
                cv2.rectangle(frame, (x1, y1), (x1 + 60, y1 + 100), (0, 255, 0), 2)

            # Add text
            cv2.putText(frame, f'Camera: {self.camera_id}', (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, f'Personas: {self.count}', (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            cv2.putText(frame, f'Frame: {self.frame_counter}', (20, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # Update frame with lock
            with self.lock:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 60]
                _, buffer = cv2.imencode('.jpg', frame, encode_param)
                encoded_frame = buffer.tobytes()
                self.processed_frame = encoded_frame
                self.frame_buffer.append(encoded_frame)
                detection_results[self.camera_id] = self.count

            # Control frame rate - higher for synthetic
            time.sleep(0.05)

    def get_frame(self):
        with self.lock:
            if not self.frame_buffer:
                return self.processed_frame
            return self.frame_buffer[-1]

    def stop(self):
        self.running = False

# Rest of your code for initialize_videos() stays the same

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    """Stream video for a specific camera"""
    connection_id = f"{camera_id}-{time.time()}"

    # Check connection limits
    if len(client_connections) >= max_connections:
        # Return a error message if too many connections
        return Response("Too many connections. Try again later.", status=503)

    client_connections[connection_id] = True

    def generate():
        try:
            processor = video_sources.get(camera_id)
            if not processor:
                # Generate a "no signal" frame
                img = np.zeros((360, 640, 3), dtype=np.uint8)
                cv2.putText(img, "No Signal", (240, 180),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                _, buffer = cv2.imencode('.jpg', img)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                return

            last_frame = None
            last_frame_time = 0
            min_frame_interval = 0.03  # Maximum ~30fps

            while connection_id in client_connections:
                current_time = time.time()
                if current_time - last_frame_time < min_frame_interval:
                    time.sleep(0.005)  # Short sleep
                    continue

                frame = processor.get_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue

                # Don't send duplicate frames
                if frame != last_frame:
                    last_frame = frame
                    last_frame_time = current_time
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except GeneratorExit:
            # Client disconnected
            pass
        except Exception as e:
            print(f"Stream error for {camera_id}: {str(e)}")
        finally:
            # Always clean up
            if connection_id in client_connections:
                del client_connections[connection_id]

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detection_counts')
def detection_counts():
    """Return current detection counts for all cameras"""
    return jsonify(detection_results)

@app.route('/status')
def status():
    """Return server status for debugging"""
    return jsonify({
        "status": "running",
        "active_connections": len(client_connections),
        "cameras": list(video_sources.keys()),
        "fps_settings": {
            "process_every": video_sources.get("camera_1").process_every if "camera_1" in video_sources else None,
        }
    })

if __name__ == '__main__':
    print("Initializing video processors...")
    initialize_videos()
    print("Starting Flask server...")
    # Use threaded=True for better performance
    app.run(host='0.0.0.0', port=5000, threaded=True)