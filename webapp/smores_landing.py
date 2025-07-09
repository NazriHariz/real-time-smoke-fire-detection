import streamlit as st

# Fake user database


import sqlite3
import pandas as pd

conn = sqlite3.connect(r"C:\Users\Irfan\OneDrive\Dokumen\smore detection\smore_database.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM smore_acc_user")
rows = cursor.fetchall()

user_smore_table = pd.DataFrame(rows, columns=["user_id", "user_name", "user_pass"])
conn.close()

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Page routing
def show_login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_match = user_smore_table[
            (user_smore_table["user_name"] == username) & 
            (user_smore_table["user_pass"] == password)
        ]

        if not user_match.empty:
            user = user_match.iloc[0]
            st.session_state.logged_in = True
            st.session_state.user_id = user["user_id"]
            st.session_state.user_name = user["user_name"]
            st.success(f"Login successful. Welcome {user['user_name']}!")
            st.rerun()
        else:
            st.error("Invalid username or password")


def show_main():

    alert_mng = st.Page(
        "page/alert_management.py", title="Alert Management", icon=":material/dashboard:", default = True
    )
    alert_list = st.Page(
        "page/alert_list.py", title="Alert List", icon=":material/dashboard:"
    )
    # bugs = st.Page("reports/bugs.py", title="Bug reports", icon=":material/bug_report:")
    # alerts = st.Page(
    #     "reports/alerts.py", title="System alerts", icon=":material/notification_important:"
    # )

    # search = st.Page("tools/search.py", title="Search", icon=":material/search:")
    # history = st.Page("tools/history.py", title="History", icon=":material/history:")

    # if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Alert": [alert_mng,alert_list]
        }
    )

    pg.run()

# Run app
if not st.session_state.logged_in:
    show_login_page()
else:
    show_main()

