import requests
import streamlit as st
import pandas as pd
import pymysql
import streamlit.components.v1 as components

# Replace 'YOUR_BOT_TOKEN' with your bot's token
BOT_TOKEN = st.secrets["BOT_TOKEN"]

# Database configuration
db_config = {
    "host": st.secrets["DB_HOST"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PWD"],
    "database": st.secrets["DB_DB"]
}



# Function to retrieve user IDs and additional information from the database
def get_user_data_from_db():
    try:
        conn = pymysql.connect(**db_config)
        print(conn)
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, responsibility, responsibility_type FROM discord_users")
            user_data = cursor.fetchall()
        return user_data
    except pymysql.Error as e:
        st.warning(f"Failed to retrieve user data from the database. Error: {str(e)}")
    finally:
        conn.close()

st.title('Discord User Info Table')

# Retrieve user data from the database
user_data_from_db = get_user_data_from_db()

# Create an empty list to store user data
user_data_list = []

# Loop through the user data and fetch user information
for user_data in user_data_from_db:
    user_id, responsibility, responsibility_type = user_data

    API_ENDPOINT = f'https://discord.com/api/v10/users/{user_id}'
    headers = {'Authorization': f'Bot {BOT_TOKEN}'}

    try:
        response = requests.get(API_ENDPOINT, headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            avatar_url = f'https://cdn.discordapp.com/avatars/{user_data["id"]}/{user_data["avatar"]}.png'
            username = user_data["username"]

            user_data_list.append({
                "Username": username,
                "Avatar URL": avatar_url,
                "Responsibility": responsibility,
                "Responsibility Type": responsibility_type,
            })
        else:
            st.warning(f"Failed to fetch user data for user ID {user_id}. Status code: {response.status_code}")
    except Exception as e:
        st.warning(f"An error occurred for user ID {user_id}: {str(e)}")

# Display the user data in a Streamlit table with images
if user_data_list:
    user_df = pd.DataFrame(user_data_list)
    st.data_editor(
    user_df,
    column_config={
        "Avatar URL": st.column_config.ImageColumn(
            "Profile Picture", width="medium", help="Discord Profile Picture"
        )
    },
    hide_index=True,
)