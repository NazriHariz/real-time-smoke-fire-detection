import requests

API_URL = "http://127.0.0.1:8000/predict"

def post_video_path(path):
    payload = {"path": path}
    response = requests.post(API_URL, json=payload)
    print(response.status_code)
    print(response.json())

if __name__ == "__main__":
    post_video_path("/mnt/c/Users/ASUS/Documents/yolov11/data/gen_fire.mp4")
