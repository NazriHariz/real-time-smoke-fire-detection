import cv2
import os

def draw_boxes_on_video(source_video: str, detections: list, output_path: str):
    if not os.path.isfile(source_video):
        raise FileNotFoundError(f"Source video not found: {source_video}")

    # Group detections by frame
    from collections import defaultdict
    frame_map = defaultdict(list)
    for det in detections:
        frame_map[det["frame_index"]].append(det)

    cap = cv2.VideoCapture(source_video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        for det in frame_map.get(frame_idx, []):
            box = det["bbox"]
            class_name = det["class_name"]
            score = det["score"]
            x1, y1, x2, y2 = map(int, [box["topX"], box["topY"], box["bottomX"], box["bottomY"]])
            color = (0, 0, 255) if class_name.lower() == "fire" else (0, 0, 139)
            label = f"{class_name} {score:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    print(f"✅ Succesfully trim and annotate video")
