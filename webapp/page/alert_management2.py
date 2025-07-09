import streamlit as st

st.title("Alert Manager👋")

import sqlite3
import pandas as pd

conn = sqlite3.connect(r"C:\Users\Irfan\OneDrive\Dokumen\smore detection\smore_database.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM landing_smore_camera_output")
rows = cursor.fetchall()

df = pd.DataFrame(rows, columns=["alert_id", "alert_time", "modified_time","user_modified", "fire_detected", "fire_accuracy","fire_bd_box_area", "smoke_detected", "smoke_accuracy","smoke_bd_box_area","image_path","extend_info"])
conn.close()

# st.table(df)
st.dataframe(df, use_container_width=True,hide_index=True)

if st.button("Send balloons!"):
    st.balloons()
