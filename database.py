import mysql.connector
import streamlit as st

def create_connection():
    try:
        # Check if running on Streamlit Cloud with Secrets
        if "db" in st.secrets:
            connection = mysql.connector.connect(
                host=st.secrets["db"]["host"],
                user=st.secrets["db"]["user"],
                password=st.secrets["db"]["password"],
                database=st.secrets["db"]["database"],
                port=st.secrets["db"].get("port", 3306)
            )
        else:
            # Fallback to Local MySQL Configuration
            connection = mysql.connector.connect(
                host="127.0.0.1",
                user="hotel_app",
                password="Pass@231106",
                database="hotel_management"
            )

        if connection.is_connected():
            return connection
    except Exception as error:
        st.error(f"Database Connection Failed: {error}")
    return None