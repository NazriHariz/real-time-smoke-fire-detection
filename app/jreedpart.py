import os
import sqlite3
import datetime

def analyze_and_store_detections(detections,file_name,file_id):
    # Initialize summary variables
    fire_detected, fire_score = False, 0.0
    smoke_detected, smoke_score = False, 0.0
    no_of_fire_detected = 0
    no_of_smoke_detected = 0

    # Analyze detections
    for d in detections:
        class_name = d["class_name"].lower()
        score = d["score"]

        if class_name == "fire":
            no_of_fire_detected += 1
            fire_detected = True
            if score > fire_score:
                fire_score = score

        elif class_name == "smoke":
            no_of_smoke_detected += 1
            smoke_detected = True
            if score > smoke_score:
                smoke_score = score

    # Generate alert ID and timestamp
    alert_id = "A" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    alert_time = datetime.datetime.now()

    # Save to SQLite database
    conn = sqlite3.connect("smore_database_new.db")
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO summary_smore_alert 
        (alert_id, alert_time, modified_time, user_modified, no_of_fire_detected, no_of_smoke_detected, file_id, file_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                alert_id,
                alert_time,
                None,
                None,
                no_of_fire_detected,
                no_of_smoke_detected,
                file_id,
                file_name # os.path.basename(file_name)
            )
        ]
    )
    conn.commit()
    conn.close()

    print("Succesfully insert into db")
    # Return summary result
    return {
        "Summary": {
            "Alert ID": alert_id,
            "Alert_time": alert_time,
            "No_of_fire_detected": no_of_fire_detected,
            "No_of_smoke_detected": no_of_smoke_detected,
            "file_id": file_id,
            "file_name": file_name,
        }
    }
