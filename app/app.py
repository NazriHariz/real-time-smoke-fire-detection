import os
import sys
import tempfile
from dataclasses import dataclass
from typing import Annotated
from litestar import Litestar, post, Response
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.config.cors import CORSConfig


# ✅ Correct CORS setup
cors_config = CORSConfig(
    allow_origins=["http://localhost:5173"],  # adjust based on frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include custom module if needed
sys.path.append(os.path.dirname(__file__))
from customFireDetector import YOLOv11Detector

# Init detector
detector = YOLOv11Detector(
    model_path="./best_nano_111.pt"
)

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".mp4", ".avi", ".mov", ".mkv"}

# --- Dataclass to receive multipart form-data ---
@dataclass
class PredictRequest:
    file: UploadFile


@post(path="/predict")
async def predict_handler(
    data: Annotated[PredictRequest, Body(media_type=RequestEncodingType.MULTI_PART)]
) -> Response:
    ext = os.path.splitext(data.file.filename)[1].lower()

    if ext not in ALLOWED_EXTS:
        return Response({"error": f"Unsupported extension: {ext}"}, status_code=400)

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await data.file.read())
        tmp_path = tmp.name

    try:
        detections = detector.predict(tmp_path)
        return Response({"filename": data.file.filename, "detections": detections})
    except Exception as e:
        return Response({"error": str(e)}, status_code=500)
    finally:
        os.remove(tmp_path)


# App init
# app = Litestar(route_handlers=[predict_handler])
app = Litestar(
    route_handlers=[predict_handler],
    cors_config=cors_config
)