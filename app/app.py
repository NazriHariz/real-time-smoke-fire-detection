from litestar import Litestar, post, Response
from litestar.params import Body
from litestar.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from customFireDetector import YOLOv11Detector

detector = YOLOv11Detector(model_path="/mnt/c/Users/ASUS/Documents/yolov11/best_nano_111.pt")

# Define request model
class VideoRequest(BaseModel):
    path: str

@post("/predict")
async def predict_endpoint(data: VideoRequest = Body()) -> Response:
    video_path = data.path

    if not os.path.exists(video_path):
        return Response(
            content={"error": f"File does not exist: {video_path}"},
            status_code=400,
        )

    ext = os.path.splitext(video_path)[1].lower()
    allowed_exts = {".jpg", ".jpeg", ".png", ".bmp", ".mp4", ".avi", ".mov", ".mkv"}
    if ext not in allowed_exts:
        return Response(
            content={"error": f"Unsupported extension: {ext}"},
            status_code=400,
        )

    try:
        detections = detector.predict(video_path)
        return Response(content={"detections": detections})
    except Exception as e:
        return Response(content={"error": str(e)}, status_code=500)

app = Litestar(route_handlers=[predict_endpoint])
