import json
import os
from ultralytics import YOLO

class YOLOv11Detector:
    def __init__(self, model_path: str):
        """
        Initialize the YOLOv11 detector with the specified model.
        """
        self.model = YOLO(model_path)

    def predict(self, source: str) -> list:
        """
        Run prediction on an image, video, or directory of images.
        Return results as a JSON-compatible list.
        """
        # Determine if source is video or image(s)
        video_extensions = {".mp4", ".avi", ".mov", ".mkv"}
        image_extensions = {".jpg", ".jpeg", ".png", ".bmp"}

        is_video = False
        if os.path.isfile(source):
            ext = os.path.splitext(source)[1].lower()
            if ext in video_extensions:
                is_video = True
            elif ext not in image_extensions:
                raise ValueError(f"Unsupported file extension: {ext}")

        # Run prediction
        results = self.model.predict(source=source, stream=True)

        detections = []

        for result in results:
            # For video, result.path can include frame info
            image_name = os.path.basename(result.path)

            for box in result.boxes:
                bbox = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                detection = {
                    "class_name": self.model.names[int(box.cls[0])],
                    "score": float(box.conf[0]),
                    "bbox": {
                        "topX": round(bbox[0], 2),
                        "topY": round(bbox[1], 2),
                        "bottomX": round(bbox[2], 2),
                        "bottomY": round(bbox[3], 2)
                    }
                }
                detections.append(detection)

        return detections
    
# if __name__ == "__main__":
#     # Replace with your trained model path
#     model_path = "/mnt/c/Users/ASUS/Documents/yolov11/best_nano_111.pt"

#     # Replace with your image, video, or folder
#     test_source = "/mnt/c/Users/ASUS/Documents/yolov11/data/gen_fire.mp4"

#     # Create detector
#     detector = YOLOv11Detector(model_path)

#     # Predict
#     detections = detector.predict(test_source)

#     # Print nicely formatted JSON to console
#     import json
#     print(json.dumps(detections, indent=2))
