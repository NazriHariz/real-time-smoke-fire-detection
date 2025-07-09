import streamlit as st

st.title("Alert Manager👋")

import sqlite3
import pandas as pd
import streamlit.components.v1 as components

conn = sqlite3.connect(r"C:\Users\Irfan\OneDrive\Dokumen\smore detection\smore_database.db")
cursor = conn.cursor()

cursor.execute("SELECT *,case when no_of_fire_detected > 15 or no_of_smoke_detected > 15 then 'High' when (no_of_fire_detected between 9 and 15) or (no_of_smoke_detected between 9 and 15) then 'Medium' " \
"else 'Low' end as risk_level  FROM summary_smore_alert")
rows = cursor.fetchall()

adm_smore_table = pd.DataFrame(rows, columns=["alert_id", "alert_time", "modified_time","user_modified", "no_of_fire_detected", "no_of_smoke_detected","file_id", "file_name", "risk_level"])
conn.close()


def risk_alert_color(alert):
    color_map = {
    "High": "red",
    "Medium": "orange",
    "Low": "gold"  # "yellow" is often too light, "gold" is more readable
    }
    color = color_map.get(alert['risk_level'], "black")
    return color



@st.dialog(title = "Alert Details", width = 'large')
def alert_dialog(alert):

    # color = color_map.get(alert['risk_level'], "black")

    color = risk_alert_color(alert)

    st.write(f"Alert ID: {alert['alert_id']} ")
    st.write(f"Alert Time: {alert['alert_time']} ")
    st.write(f"Modified by: {alert['modified_time']} ")
    st.write(f"Modified Time: {alert['user_modified']} ")
    st.write(f"Number of Fire Detected: {alert['no_of_fire_detected']} ")
    st.write(f"Number of Smoke Detected: {alert['no_of_smoke_detected']} ")
    st.markdown(f"<b>Risk Level:</b> <span style='color:{color}; font-weight:bold'>{alert['risk_level']}</span>", unsafe_allow_html=True)

    
    # st.image(alert['image_path'], caption="This is an example image")

    # video_file = open(r"C:\Users\Irfan\OneDrive\Dokumen\smore detection\video_output\sample2.mp4", "rb")
    # video_bytes = video_file.read()
    # st.video(video_bytes)

    gdrive_link = r"https://drive.google.com/file/d/" + alert['file_name'] + r"/view"
    components.iframe(gdrive_link, height=400)


    # reason = st.text_input("Because...")
    # if st.button("Submit"):
    #     st.session_state.vote = {"item": item, "reason": reason}
    #     st.rerun()


# Apply CSS to simulate a bordered table
st.markdown("""
    <style>
    .table-header, .table-row {
        display: flex;
        border-bottom: 1px solid #ccc;
        padding: 8px 0;
        font-family: sans-serif;
    }
    .table-header {
        font-weight: bold;
        border-bottom: 2px solid #666;
    }
    .cell {
        flex: 1;
        padding: 4px 8px;
        overflow-wrap: anywhere;
    }
    .cell-button {
        flex: 0 0 100px;
        padding: 4px 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Header row
st.markdown(f"""
<div class="table-header">
    <div class="cell">Alert ID</div>
    <div class="cell">Alert Time</div>
    <div class="cell">Alert Status</div>
    <div class="cell">RIsk Level</div>
    <div class="cell-button">Action</div>
</div>
""", unsafe_allow_html=True)


# Table rows
for i, alert in adm_smore_table.iterrows():
    cols = st.columns([2, 2, 2,1,1])
    with cols[0]:
        st.markdown(f"<div class='cell'>{alert['alert_id']}</div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='cell'>{alert['alert_time']}</div>", unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f"<div class='cell'>'test- not review'</div>", unsafe_allow_html=True)
    with cols[3]:
        color = risk_alert_color(alert)
        st.markdown(f"<span style='color:{color}; font-weight:bold'>{alert['risk_level']}</span>", unsafe_allow_html=True)
    with cols[4]:
        if st.button("Review", key=f"view_{i}"):
            alert_dialog(alert)
