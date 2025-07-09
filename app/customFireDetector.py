import os
import cv2
from ultralytics import YOLO

class YOLOv11Detector:
    def __init__(self, model_path: str, threshold: float = 0.5):
        self.model = YOLO(model_path)
        self.threshold = threshold

    def detect_and_trim(self, source: str, output_video: str,
                        trigger_classes=("fire", "smoke"), alert_duration_sec=5) -> list:
        """
        Detects fire/smoke, trims 5 seconds of video from detection point,
        collects detections only within that segment.
        Returns JSON-compatible list of detections for that 5-second clip.
        """
        cap = cv2.VideoCapture(source)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Output writer (initialize later)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = None

        detection_found = False
        start_frame = None
        end_frame = None
        frame_idx = 0
        detections = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if detection_found and (frame_idx > end_frame):
                break

            current_time_sec = frame_idx / fps

            # Inference only until detection or within trimmed window
            if not detection_found or (start_frame <= frame_idx <= end_frame):
                results = self.model.predict(source=frame, stream=False, conf=self.threshold)
                result = results[0]

                for box in result.boxes:
                    bbox = box.xyxy[0].tolist()
                    class_id = int(box.cls[0])
                    class_name = self.model.names[class_id]
                    score = float(box.conf[0])

                    # Initial detection triggers trim
                    if not detection_found and class_name.lower() in trigger_classes:
                        detection_found = True
                        start_frame = frame_idx
                        end_frame = start_frame + int(fps * alert_duration_sec)
                        out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
                        print(f"🚨 Detected {class_name} at frame {frame_idx}. Trimming for 5 seconds.")

                    # Save detection only if within clip range
                    if detection_found and start_frame <= frame_idx <= end_frame:
                        detections.append({
                            "frame_index": frame_idx - start_frame,
                            "timestamp_sec": round((frame_idx - start_frame) / fps, 2),
                            "class_name": class_name,
                            "score": score,
                            "bbox": {
                                "topX": round(bbox[0], 2),
                                "topY": round(bbox[1], 2),
                                "bottomX": round(bbox[2], 2),
                                "bottomY": round(bbox[3], 2)
                            }
                        })

            # Save video frames only if in trim window
            if detection_found and start_frame <= frame_idx <= end_frame:
                out.write(frame)

            frame_idx += 1

        cap.release()
        if out:
            out.release()

        if not detection_found:
            print("⚠️ No fire/smoke detected. No clip trimmed.")
        else:
            print(f"🎥 Trimmed clip saved to {output_video}")

        return detections
