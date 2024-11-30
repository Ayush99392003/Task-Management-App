import streamlit as st
from datetime import date
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(
        'task-management-869ee-firebase-adminsdk-e8q8e-df9f659f80.json')  # Update with the correct path
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://task-management-869ee-default-rtdb.asia-southeast1.firebasedatabase.app/'})
db = firestore.client()


# Signup Page
def signup_page():
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://wallpapercave.com/wp/wp5529802.jpg") no-repeat center center fixed; 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='text-align: center;color:white;'>Signup Page</h1>", unsafe_allow_html=True)
    email = st.text_input("", key="signup_email", placeholder="Enter your email")
    password = st.text_input("", type="password", key="signup_password", placeholder="Enter your password")
    confirm_password = st.text_input("", type="password", key="signup_confirm_password",
                                     placeholder="Confirm your password")

    if st.button("Signup", key="signup_button"):
        if not email.strip():
            st.error("Email cannot be empty!")
            return
        if password == confirm_password:
            try:
                user_ref = db.collection('users').document(email)
                user_ref.set({'email': email, 'password': password})
                st.success("Signup successful!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Passwords do not match!")


# Login Page
def login_page():
    # Check if the user is already logged in
    if st.session_state.get('logged_in', False):
        st.session_state.page = 'task_management'  # Set the page to task management
        return

    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://i.pinimg.com/originals/70/c6/e4/70c6e4a9e17785bc2b26cc0ff2c4d242.jpg") no-repeat center center fixed; 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h3 style='color: chartreuse;'>Login Page</h3>", unsafe_allow_html=True)

    email = st.text_input("", key="login_email", placeholder="Enter your email")
    password = st.text_input("", type="password", key="login_password", placeholder="Enter your password")

    if st.button("Login", key="login_button"):
        if not email.strip():
            st.error("Email cannot be empty!")
            return
        try:
            user_ref = db.collection('users').document(email)
            user = user_ref.get()

            if user.exists and user.to_dict().get('password') == password:
                st.session_state.logged_in = True
                st.session_state.username = email  # Store username for task management
                st.session_state.page = 'task_management'  # Update page to task management
                st.experimental_rerun()  # Trigger rerun to reload and show task management page
            else:
                st.error("Invalid email or password!")
        except Exception as e:
            st.error(f"An error occurred: {e}")


# About Us Page
def about_us_page():
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://c.wallhere.com/photos/56/b4/selective_coloring_black_background_dark_background_simple_background_anime_girls-2219472.jpg!d") no-repeat center center fixed; 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='color: red;'>About Us</h1>", unsafe_allow_html=True)
    st.write("This is a demo application for user authentication and task management.")


# Task Management Page
def task_management_page():
    st.title("Task Management")

    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://png.pngtree.com/png-clipart/20220125/original/pngtree-sci-tech-line-background-png-image_7212815.png") no-repeat center center fixed; 
            background-size: cover;
        }
        .curved-box {
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 25px;
            padding: 20px;
            margin: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            width: 80%;
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='curved-box'>
            <h2 style='color: "Dark blue"; font-family: "Open Sans", sans-serif; font-size: 35px; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);'>
                Manage Your Tasks
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Retrieve tasks for the logged-in user
    tasks_ref = db.collection('tasks').document(st.session_state.username).collection('user_tasks')
    tasks = tasks_ref.stream()
    tasks_list = []

    for task in tasks:
        task_data = task.to_dict()
        tasks_list.append(task_data)

    # Task Form
    task_name = st.text_input("Task Name", key="task_name_input")
    task_deadline_date = st.date_input("Task Deadline Date", min_value=date.today(), key="task_deadline_date_input")
    task_priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="task_priority_input")
    task_category = st.selectbox("Category", ["Started", "Processing", "Ended"], key="task_category_input")

    if st.button("Add Task", key="add_task_button"):
        new_task = {"Task Name": task_name, "Task Deadline Date": task_deadline_date,
                    "Priority": task_priority, "Category": task_category}
        tasks_ref.add(new_task)
        st.success("Task added successfully.")

    # Display Tasks
    for index, task in enumerate(tasks_list):
        task_name = task["Task Name"]
        task_deadline = task["Task Deadline Date"]
        task_priority = task["Priority"]
        task_category = task["Category"]

        st.write(f"Task {index + 1}: {task_name} | {task_deadline} | {task_priority} | {task_category}")

    # Task Editing and Deleting (not implemented here but can be added similarly)
    # You can add buttons to delete or edit tasks as needed.


# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "login"  # Default page is login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Sidebar Navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Login", key="nav_login"):
    st.session_state.page = 'login'
if st.sidebar.button("Sign Up", key="nav_signup"):
    st.session_state.page = 'signup'
if st.sidebar.button("About Us", key="nav_about"):
    st.session_state.page = 'about'

# Main Page Rendering
if st.session_state.page == "login" and not st.session_state.logged_in:
    login_page()
elif st.session_state.page == "signup":
    signup_page()
elif st.session_state.page == "about":
    about_us_page()
elif st.session_state.page == "task_management" and st.session_state.logged_in:
    task_management_page()
