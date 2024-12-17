import streamlit as st
from datetime import date, datetime
import firebase_admin
from firebase_admin import credentials, firestore
import time
import pandas as pd

# Initialize Firebase Admin
if not firebase_admin._apps:
    cred = credentials.Certificate(
        'management-1f113-firebase-adminsdk-5hxme-889f6428a4.json')  # Update with the correct path to your Firebase credentials
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://management-1f113-default-rtdb.asia-southeast1.firebasedatabase.app/'})  # Firebase DB URL
db = firestore.client()

# Set page configuration (only called once at the start)
st.set_page_config(page_title="Task Management", page_icon="📋", layout="centered")

# Signup Page
def signup_page():
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://img.freepik.com/free-photo/top-view-education-day-elements-with-copy-space_23-2148721223.jpg") no-repeat center center fixed; 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='text-align: center;color:yellow;font-family:Geneva;font-size:75'>Signup Page</h1>", unsafe_allow_html=True)
    email = st.text_input("", key="signup_email", placeholder="Enter your email")
    password = st.text_input("", type="password", key="signup_password", placeholder="Enter your password")
    confirm_password = st.text_input("", type="password", key="signup_confirm_password", placeholder="Confirm your password")

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
    if st.session_state.get('logged_in', False):
        st.session_state.page = 'task_management'
        return

    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://img.freepik.com/free-vector/gradient-international-day-education-background_23-2151120687.jpg?semt=ais_hybrid") no-repeat center center fixed; 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h3 style='text-align:center;font-family:algerian;color: black;font-size:60px;'>Login Page</h3>", unsafe_allow_html=True)

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
                st.session_state.username = email
                st.session_state.page = 'task_management'
                time.sleep(0.5)
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
            background: url("https://wallpapers.com/images/high/study-4k-with-candle-e4m05rex51ll6jlf.webp") no-repeat center center fixed; 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<h1 style='font-size:55px;text-align:center;color: pink;'>About Us</h1>", unsafe_allow_html=True)
    st.markdown(
    """
    <div style="font-size: 24px; color: yellow; text-align: center;">
        Welcome to Task Management, a dynamic web application designed to help individuals manage their tasks efficiently. 
        Whether you're a student, professional, or someone looking to organize your day-to-day activities, 
        this platform offers a simple and intuitive interface for managing tasks with ease.
        Our goal is to make task management as seamless as possible, with features like task prioritization, deadlines, 
        and customizable categories. Sign up today and take control of your tasks!
    </div>
    """,
    unsafe_allow_html=True
    )

# Task Management Page
def task_management_page():
    # Custom CSS for styling the page
    st.markdown(
        """
        <style>
        .stApp {
            background: url("https://img.freepik.com/free-vector/paper-style-dynamic-lines-background_23-2149008629.jpg") no-repeat center center fixed; 
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
            <h2 style='text-align:center;color: pink; font-family: "Brush Script MT"; font-size: 80px; '>
                Manage Your Tasks
            </h2>
        """,
        unsafe_allow_html=True
    )

    tasks_ref = db.collection('tasks').document(st.session_state.username).collection('user_tasks')
    tasks = tasks_ref.stream()
    tasks_list = []

    # Collect all tasks from Firestore
    for task in tasks:
        task_data = task.to_dict()
        task_data['task_id'] = task.id  # Add the Firestore document ID as task_id
        tasks_list.append(task_data)

    # Convert tasks to a DataFrame for displaying in table format
    df = pd.DataFrame(tasks_list)

    # Display Add New Task Form
    task_name = st.text_input("", key="task_name_input",placeholder="Task Name")
    task_deadline_date = st.date_input("Task Deadline Date", min_value=date.today(), key="")
    task_priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="")
    task_category = st.selectbox("Category", ["Started", "Processing", "Ended"], key="")

    # Check if the task name already exists
    existing_task_names = [task['Task Name'] for task in tasks_list]

    if st.button("Add Task", key="add_task_button"):
        if not task_name.strip():  # Check for empty task name
            st.error("Task name cannot be empty!")
        elif task_name.strip() in existing_task_names:  # Check for duplicate task name
            st.error(f"Task with name '{task_name.strip()}' already exists!")
        else:
            new_task = {
                "Task Name": task_name.strip(),
                "Task Deadline Date": task_deadline_date.strftime("%Y-%m-%d"),  # Convert date to string
                "Priority": task_priority,
                "Category": task_category
            }

            tasks_ref.add(new_task)
            st.success("Task added successfully.")

    # Display task table and buttons
    if not df.empty:
        st.dataframe(df[['Task Name', 'Task Deadline Date', 'Priority', 'Category']])  # Display the table with relevant columns
        for index, row in df.iterrows():
            task_id = row['task_id']
            # Edit button
            if st.button(f"Edit Task {row['Task Name']}", key=f"edit_{task_id}"):
                # Edit fields for the task
                new_task_name = st.text_input(f"Edit Task Name for {task_id}", value=row['Task Name'], key=f"new_name_{task_id}")
                new_task_deadline = st.date_input(f"Edit Deadline for {task_id}", value=datetime.strptime(row['Task Deadline Date'], '%Y-%m-%d').date(), key=f"new_deadline_{task_id}")
                new_task_priority = st.selectbox(f"Edit Priority for {task_id}", ["High", "Medium", "Low"], index=["High", "Medium", "Low"].index(row['Priority']), key=f"new_priority_{task_id}")
                new_task_category = st.selectbox(f"Edit Category for {task_id}", ["Started", "Processing", "Ended"], index=["Started", "Processing", "Ended"].index(row['Category']), key=f"new_category_{task_id}")
                
                if st.button(f"Save Changes for {task_id}"):
                    task_ref = tasks_ref.document(task_id)
                    task_ref.update({
                        'Task Name': new_task_name,
                        'Task Deadline Date': new_task_deadline.strftime('%Y-%m-%d'),
                        'Priority': new_task_priority,
                        'Category': new_task_category
                    })
                    st.success(f"Task '{new_task_name}' updated successfully!")

            # Delete button
            if st.button(f"Delete Task {row['Task Name']}", key=f"delete_{task_id}"):
                delete_task(task_id)

    else:
        st.warning("No tasks found.")

# Function to delete a task
def delete_task(task_id):
    try:
        tasks_ref = db.collection('tasks').document(st.session_state.username).collection('user_tasks')
        task_to_delete = tasks_ref.document(task_id)  # Use task_id to get the document
        task_to_delete.delete()  # Delete the task from Firestore
        st.success(f"Task with ID '{task_id}' deleted successfully!")
    except Exception as e:
        st.error(f"Error deleting task: {e}")

# Sidebar Navigation (this will be visible only on pages other than Task Management)
if 'page' not in st.session_state:
    st.session_state.page = "login"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.page != 'task_management':
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
