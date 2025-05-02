import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO('yolov8s.pt')

# Video Capture
cap = cv2.VideoCapture('monitoring-system/src/assets/sample_vids/vid1.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Inference
    results = model(frame, conf=0.5)

    count = 0

    # Draw bounding boxes
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0]) # Bounding box coordinates
            conf = box.conf[0].item() # Confidence
            cls = int(box.cls[0].item()) # Detected class

            if cls == 0:
                count += 1
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
                cv2.putText(frame, f'Person {conf:.2f}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

    # Display person count
    cv2.putText(frame, f'Person Count: {count}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.imshow('Person Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()