import os
import sys
import tempfile
import json
import datetime as dt
from dataclasses import dataclass
from typing import Annotated
from jreedpart import analyze_and_store_detections
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
from upload_detection import upload_to_drive
from trim_drawbb import draw_boxes_on_video

# Init detector
detector = YOLOv11Detector(
    model_path="../best_nano_111.pt"
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
    file_name = os.path.splitext(data.file.filename)[0].lower()

    if ext not in ALLOWED_EXTS:
        return Response({"error": f"Unsupported extension: {ext}"}, status_code=400)

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(await data.file.read())
        tmp_path = tmp.name

    try:
        # Define output file paths
        trimmed_path = f"{file_name}_trimmed{ext}"
        final_path = f"{file_name}_annotated{ext}"

        # Step 1: Detect and trim 5s clip from detection
        detections = detector.detect_and_trim(tmp_path, output_video=trimmed_path)

        if not detections:
            os.remove(tmp_path)
            return Response({"filename": data.file.filename, "message": "No fire/smoke detected."})

        # Step 2: Draw bounding boxes on trimmed video
        draw_boxes_on_video(trimmed_path, detections, output_path=final_path)

        # Step 3: Upload final video to drive (optional)
        file_id = upload_to_drive(final_path, os.path.basename(final_path))

        # Step 4 : Upload to DB
        result = analyze_and_store_detections(detections, file_name,file_id)

        # Clean up
        os.remove(tmp_path)
        os.remove(trimmed_path)
        os.remove(final_path)

        return detections

    except Exception as e:
        return Response({"error": str(e)}, status_code=500)


# App init
# app = Litestar(route_handlers=[predict_handler])
app = Litestar(
    route_handlers=[predict_handler],
    cors_config=cors_config
)