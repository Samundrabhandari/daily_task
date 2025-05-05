import streamlit as st
import json
import os
import datetime
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import calendar
import base64
from io import BytesIO
from pathlib import Path

# Define constants and paths
DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"

# Create data directory if it doesn't exist
DATA_DIR.mkdir(exist_ok=True)

# Initialize global variables
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "first_login" not in st.session_state:
    st.session_state.first_login = False
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Home"

# Helper functions for user authentication
def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from the users.json file."""
    if not USERS_FILE.exists():
        return {}
    
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users):
    """Save users to the users.json file."""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def verify_user(username, password):
    """Verify user credentials."""
    users = load_users()
    if username in users and users[username]["password"] == hash_password(password):
        return True
    return False

def create_user(username, password):
    """Create a new user."""
    users = load_users()
    if username in users:
        return False
    
    users[username] = {
        "password": hash_password(password),
        "created_at": datetime.datetime.now().isoformat()
    }
    save_users(users)
    
    # Create user data file with default habits
    user_data = {
        "habits": ["Drink Water", "Exercise", "Read", "Meditate"],
        "history": {}
    }
    save_user_data(username, user_data)
    return True

def get_user_data_file(username):
    """Get the path to a user's data file."""
    return DATA_DIR / f"{username}.json"

def load_user_data(username):
    """Load user data from their JSON file."""
    user_file = get_user_data_file(username)
    if not user_file.exists():
        return {
            "habits": [],
            "history": {}
        }
    
    with open(user_file, "r") as f:
        return json.load(f)

def save_user_data(username, data):
    """Save user data to their JSON file."""
    user_file = get_user_data_file(username)
    with open(user_file, "w") as f:
        json.dump(data, f)

def get_today_str():
    """Get today's date as a string in YYYY-MM-DD format."""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def get_today_display():
    """Get today's date in a display format."""
    return datetime.datetime.now().strftime("%A, %B %d, %Y")

def initialize_today(username):
    """Initialize today's habit tracking data if it doesn't exist."""
    user_data = load_user_data(username)
    today = get_today_str()
    
    if today not in user_data["history"]:
        user_data["history"][today] = {habit: False for habit in user_data["habits"]}
        save_user_data(username, user_data)

def logout_user():
    """Log out the current user."""
    st.session_state.user_logged_in = False
    st.session_state.current_user = None
    st.session_state.active_tab = "Home"

# UI Helper Functions
def set_page_config():
    """Set page config based on dark/light mode."""
    st.set_page_config(
        page_title="Daily Habit Tracker",
        page_icon="✅", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS based on dark/light mode
    if st.session_state.dark_mode:
        st.markdown("""
        <style>
            .stApp {
                background-color: #0E1117;
                color: #FAFAFA;
            }
            .st-emotion-cache-16txtl3 h1 {
                color: #FAFAFA;
            }
            .st-emotion-cache-16txtl3 h2 {
                color: #FAFAFA;
            }
            .st-emotion-cache-16txtl3 h3 {
                color: #FAFAFA;
            }
            .big-font {
                font-size: 24px !important;
                font-weight: bold;
            }
            .habit-container {
                background-color: #262730;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            .completed {
                color: #00C853;
                font-weight: bold;
            }
            .not-completed {
                color: #FF5252;
            }
            .habit-card {
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .day-header {
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 15px;
                color: #FAFAFA;
            }
            .streak-good {
                color: #00C853;
                font-weight: bold;
            }
            .streak-average {
                color: #FFD600;
                font-weight: bold;
            }
            .streak-poor {
                color: #FF5252;
                font-weight: bold;
            }
            .nav-link {
                padding: 10px 15px;
                margin: 2px 0;
                border-radius: 5px;
                text-decoration: none;
                transition: background-color 0.3s;
            }
            .nav-link:hover {
                background-color: #343A40;
            }
            .nav-link-active {
                background-color: #4B5563;
                font-weight: bold;
            }
            .welcome-card {
                background-color: #262730;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 5px solid #4CAF50;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            .stApp {
                background-color: #FFFFFF;
            }
            .big-font {
                font-size: 24px !important;
                font-weight: bold;
            }
            .habit-container {
                background-color: #F8F9FA;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            }
            .completed {
                color: #00C853;
                font-weight: bold;
            }
            .not-completed {
                color: #FF5252;
            }
            .habit-card {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                border: 1px solid #E0E0E0;
            }
            .day-header {
                font-weight: bold;
                font-size: 18px;
                margin-bottom: 15px;
            }
            .streak-good {
                color: #00C853;
                font-weight: bold;
            }
            .streak-average {
                color: #FFD600;
                font-weight: bold;
            }
            .streak-poor {
                color: #FF5252;
                font-weight: bold;
            }
            .nav-link {
                padding: 10px 15px;
                margin: 2px 0;
                border-radius: 5px;
                text-decoration: none;
                transition: background-color 0.3s;
            }
            .nav-link:hover {
                background-color: #F0F0F0;
            }
            .nav-link-active {
                background-color: #E9ECEF;
                font-weight: bold;
            }
            .welcome-card {
                background-color: #E8F5E9;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                border-left: 5px solid #4CAF50;
            }
        </style>
        """, unsafe_allow_html=True)

def display_welcome_tour():
    """Display welcome tour for first-time users."""
    st.markdown("""
    <div class="welcome-card">
        <h2>👋 Welcome to Your Daily Habit Tracker!</h2>
        <p>Thank you for joining! Here's a quick guide to get you started:</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏠 Home")
        st.write("Check off your daily habits and see your progress at a glance.")
        
        st.markdown("### ➕ Add/Edit Habits")
        st.write("Create new habits or modify existing ones to customize your tracker.")
    
    with col2:
        st.markdown("### 📅 History")
        st.write("Review your past performance and see how consistent you've been.")
        
        st.markdown("### 📊 Progress Summary")
        st.write("View detailed analytics and visualizations of your habit completion data.")
    
    st.markdown("---")
    if st.button("Got it! Let's start tracking", type="primary"):
        st.session_state.first_login = False
        st.experimental_rerun()

def sidebar_navigation():
    """Create sidebar navigation."""
    with st.sidebar:
        st.title("Daily Habit Tracker")
        
        # User info
        st.markdown(f"### Welcome, {st.session_state.current_user}!")
        st.write(f"Today is {get_today_display()}")
        
        st.markdown("---")
        
        # Navigation links
        nav_items = ["Home", "Add/Edit Habits", "History", "Progress Summary"]
        
        for item in nav_items:
            button_class = "nav-link-active" if st.session_state.active_tab == item else "nav-link"
            if st.button(item, key=f"nav_{item}", help=f"Go to {item} page", use_container_width=True):
                st.session_state.active_tab = item
                st.experimental_rerun()
        
        st.markdown("---")
        
        # Settings
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.experimental_rerun()
        
        # Export option
        if st.button("Export Data (CSV)", use_container_width=True):
            export_data_as_csv()
        
        # Logout button
        if st.button("Logout", use_container_width=True, type="primary"):
            logout_user()
            st.experimental_rerun()

def export_data_as_csv():
    """Generate and download a CSV export of user data."""
    user_data = load_user_data(st.session_state.current_user)
    
    # Convert history to a DataFrame
    data = []
    for date, habits in user_data["history"].items():
        row = {"Date": date}
        row.update(habits)
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # Create a CSV and offer download
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="habit_data_{st.session_state.current_user}.csv">Download CSV File</a>'
    st.sidebar.markdown(href, unsafe_allow_html=True)

# Page/Screen Functions
def login_screen():
    """Display login/signup screen."""
    st.title("Daily Habit Tracker")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Login")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submitted:
                if verify_user(username, password):
                    st.session_state.user_logged_in = True
                    st.session_state.current_user = username
                    st.session_state.active_tab = "Home"
                    
                    # Check if this is the user's first login
                    user_data = load_user_data(username)
                    if not user_data.get("history"):
                        st.session_state.first_login = True
                    
                    initialize_today(username)
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password. Please try again.")
    
    with col2:
        st.markdown("### Sign Up")
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_username")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submitted:
                if not new_username or not new_password:
                    st.error("Username and password cannot be empty.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif create_user(new_username, new_password):
                    st.success("Account created successfully! You can now log in.")
                    st.session_state.user_logged_in = True
                    st.session_state.current_user = new_username
                    st.session_state.first_login = True
                    st.session_state.active_tab = "Home"
                    initialize_today(new_username)
                    st.experimental_rerun()
                else:
                    st.error("Username already exists. Please choose a different one.")

def home_screen():
    """Display home screen with today's habits."""
    st.title("Today's Habits")
    
    username = st.session_state.current_user
    user_data = load_user_data(username)
    today = get_today_str()
    
    # Check if today's data exists, if not create it
    if today not in user_data["history"]:
        initialize_today(username)
        user_data = load_user_data(username)
    
    # Display today's date
    st.markdown(f"<div class='day-header'>{get_today_display()}</div>", unsafe_allow_html=True)
    
    # Show habits
    if not user_data["habits"]:
        st.info("You haven't added any habits yet. Go to the Add/Edit Habits page to create some!")
    else:
        # Calculate completion stats
        completed = sum(user_data["history"][today].values())
        total = len(user_data["habits"])
        completion_percentage = (completed / total) * 100 if total > 0 else 0
        
        # Progress bar
        st.progress(completion_percentage / 100)
        st.markdown(f"**{completed}/{total}** habits completed ({completion_percentage:.1f}%)")
        
        st.markdown("---")
        
        # Display each habit with checkbox
        with st.form("habits_form"):
            for habit in user_data["habits"]:
                habit_status = user_data["history"][today].get(habit, False)
                habit_status_new = st.checkbox(
                    habit,
                    value=habit_status,
                    key=f"habit_{habit}"
                )
                
                # Update habit status if changed
                user_data["history"][today][habit] = habit_status_new
            
            if st.form_submit_button("Save", type="primary", use_container_width=True):
                save_user_data(username, user_data)
                st.success("Habits updated successfully!")
        
        # Display streaks for each habit
        st.markdown("### Current Streaks")
        streaks = calculate_streaks(username)
        
        for habit, streak in streaks.items():
            streak_class = "streak-good" if streak >= 5 else "streak-average" if streak >= 3 else "streak-poor"
            st.markdown(f"<div class='habit-card'><span>{habit}</span>: <span class='{streak_class}'>{streak} days</span></div>", unsafe_allow_html=True)

def add_edit_habits_screen():
    """Display add/edit habits screen."""
    st.title("Add/Edit Habits")
    
    username = st.session_state.current_user
    user_data = load_user_data(username)
    
    # Add new habit
    with st.form("add_habit_form"):
        st.markdown("### Add New Habit")
        new_habit = st.text_input("Habit Name", key="new_habit")
        submitted = st.form_submit_button("Add Habit", type="primary")
        
        if submitted and new_habit:
            if new_habit in user_data["habits"]:
                st.error("This habit already exists.")
            else:
                # Add to habits list
                user_data["habits"].append(new_habit)
                
                # Add to today's tracking
                today = get_today_str()
                if today in user_data["history"]:
                    user_data["history"][today][new_habit] = False
                
                save_user_data(username, user_data)
                st.success(f"Added new habit: {new_habit}")
                st.experimental_rerun()
    
    st.markdown("---")
    st.markdown("### Edit Existing Habits")
    
    if not user_data["habits"]:
        st.info("You haven't added any habits yet.")
    else:
        for i, habit in enumerate(user_data["habits"]):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"<div class='habit-card'>{habit}</div>", unsafe_allow_html=True)
            
            with col2:
                if st.button("Edit", key=f"edit_{i}"):
                    st.session_state.habit_to_edit = habit
                    st.session_state.edit_mode = True
                    st.experimental_rerun()
            
            with col3:
                if st.button("Delete", key=f"delete_{i}"):
                    # Remove from habits list
                    user_data["habits"].remove(habit)
                    
                    # Remove from history
                    for date in user_data["history"]:
                        if habit in user_data["history"][date]:
                            del user_data["history"][date][habit]
                    
                    save_user_data(username, user_data)
                    st.success(f"Deleted habit: {habit}")
                    st.experimental_rerun()
    
    # Edit mode
    if hasattr(st.session_state, 'edit_mode') and st.session_state.edit_mode:
        st.markdown("---")
        st.markdown("### Edit Habit")
        
        with st.form("edit_habit_form"):
            old_habit = st.session_state.habit_to_edit
            edited_habit = st.text_input("New Habit Name", value=old_habit)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Changes", type="primary"):
                    if edited_habit and edited_habit != old_habit:
                        # Update habit name in the list
                        user_data["habits"][user_data["habits"].index(old_habit)] = edited_habit
                        
                        # Update in history
                        for date in user_data["history"]:
                            if old_habit in user_data["history"][date]:
                                user_data["history"][date][edited_habit] = user_data["history"][date][old_habit]
                                del user_data["history"][date][old_habit]
                        
                        save_user_data(username, user_data)
                        st.success(f"Updated habit: {old_habit} → {edited_habit}")
                    
                    st.session_state.edit_mode = False
                    st.experimental_rerun()
            
            with col2:
                if st.form_submit_button("Cancel"):
                    st.session_state.edit_mode = False
                    st.experimental_rerun()

def history_screen():
    """Display history screen with past habit completions."""
    st.title("Habit History")
    
    username = st.session_state.current_user
    user_data = load_user_data(username)
    
    # Handle case with no history
    if not user_data["history"]:
        st.info("No history available yet. Start tracking your habits to see your history!")
        return
    
    # Display view options
    view_type = st.radio("View Type", ["Calendar", "List"], horizontal=True)
    
    if view_type == "Calendar":
        display_calendar_view(user_data)
    else:
        display_list_view(user_data)

def display_calendar_view(user_data):
    """Display habit history in a calendar view."""
    # Get list of months with data
    dates = sorted(user_data["history"].keys())
    
    if not dates:
        st.info("No history data available yet.")
        return
    
    # Extract months and years
    months_years = set()
    for date_str in dates:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        months_years.add((date_obj.year, date_obj.month))
    
    months_years = sorted(list(months_years), reverse=True)
    
    # Let user select month/year
    if months_years:
        selected_year, selected_month = months_years[0]  # Default to most recent
        
        # Create month-year options
        month_options = []
        for year, month in months_years:
            month_name = calendar.month_name[month]
            month_options.append(f"{month_name} {year}")
        
        selected_month_year = st.selectbox("Select Month", month_options)
        selected_month_name, selected_year_str = selected_month_year.split()
        selected_month = list(calendar.month_name).index(selected_month_name)
        selected_year = int(selected_year_str)
        
        # Create calendar for selected month
        cal = calendar.monthcalendar(selected_year, selected_month)
        
        # Create calendar header
        header = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        
        # Display calendar
        st.markdown(f"### {calendar.month_name[selected_month]} {selected_year}")
        
        # Create calendar grid
        cal_container = st.container()
        
        with cal_container:
            # Create header row
            header_cols = st.columns(7)
            for i, day_name in enumerate(header):
                with header_cols[i]:
                    st.markdown(f"<div style='text-align: center; font-weight: bold;'>{day_name}</div>", unsafe_allow_html=True)
            
            # Create calendar rows
            for week in cal:
                week_cols = st.columns(7)
                for i, day in enumerate(week):
                    with week_cols[i]:
                        if day == 0:
                            st.write("")  # Empty cell
                        else:
                            date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
                            
                            if date_str in user_data["history"]:
                                # Count completed habits
                                completed = sum(user_data["history"][date_str].values())
                                total = len(user_data["history"][date_str])
                                
                                if completed == total and total > 0:
                                    color = "#4CAF50"  # Green for 100%
                                elif completed > 0:
                                    color = "#FFC107"  # Yellow for partial
                                else:
                                    color = "#F44336"  # Red for none
                                
                                st.markdown(
                                    f"""
                                    <div style='
                                        background-color: {color}; 
                                        color: white; 
                                        padding: 10px; 
                                        border-radius: 5px; 
                                        text-align: center;
                                        cursor: pointer;'
                                        onclick="alert('Completed: {completed}/{total}')">
                                        {day}<br>
                                        <small>{completed}/{total}</small>
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
                            else:
                                st.markdown(
                                    f"""
                                    <div style='
                                        background-color: #E0E0E0; 
                                        padding: 10px; 
                                        border-radius: 5px; 
                                        text-align: center;'>
                                        {day}
                                    </div>
                                    """, 
                                    unsafe_allow_html=True
                                )
        
        # Display detailed habit info for selected day
        st.markdown("### Daily Details")
        detailed_date = st.date_input(
            "Select date to view details",
            value=datetime.datetime(selected_year, selected_month, 1),
            min_value=datetime.datetime(months_years[-1][0], months_years[-1][1], 1),
            max_value=datetime.datetime.now()
        )
        
        detailed_date_str = detailed_date.strftime("%Y-%m-%d")
        
        if detailed_date_str in user_data["history"]:
            st.markdown(f"#### {detailed_date.strftime('%A, %B %d, %Y')}")
            
            habits_completed = []
            habits_not_completed = []
            
            for habit, completed in user_data["history"][detailed_date_str].items():
                if completed:
                    habits_completed.append(habit)
                else:
                    habits_not_completed.append(habit)
            
            if habits_completed:
                st.markdown("##### ✅ Completed")
                for habit in habits_completed:
                    st.markdown(f"<div class='habit-card completed'>• {habit}</div>", unsafe_allow_html=True)
            
            if habits_not_completed:
                st.markdown("##### ❌ Not Completed")
                for habit in habits_not_completed:
                    st.markdown(f"<div class='habit-card not-completed'>• {habit}</div>", unsafe_allow_html=True)
        else:
            st.info("No data available for this date.")

def display_list_view(user_data):
    """Display habit history in a list view."""
    # Get sorted dates
    dates = sorted(user_data["history"].keys(), reverse=True)
    
    if not dates:
        st.info("No history data available yet.")
        return
    
    # Create a date range selector
    date_range = st.slider(
        "Select date range",
        min_value=datetime.datetime.strptime(dates[-1], "%Y-%m-%d").date(),
        max_value=datetime.datetime.strptime(dates[0], "%Y-%m-%d").date(),
        value=(
            datetime.datetime.strptime(dates[-1], "%Y-%m-%d").date(),
            datetime.datetime.strptime(dates[0], "%Y-%m-%d").date()
        )
    )
    
    start_date, end_date = date_range
    
    # Filter dates in range
    filtered_dates = [
        date for date in dates 
        if start_date <= datetime.datetime.strptime(date, "%Y-%m-%d").date() <= end_date
    ]
    
    # Display data for each date
    for date_str in filtered_dates:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        display_date = date_obj.strftime("%A, %B %d, %Y")
        
        with st.expander(display_date):
            habits_data = user_data["history"][date_str]
            
            # Count completed habits
            completed = sum(habits_data.values())
            total = len(habits_data)
            
            # Show completion rate
            st.progress(completed / total if total > 0 else 0)
            st.markdown(f"**{completed}/{total}** habits completed")
            
            # Display individual habits
            habits_completed = []
            habits_not_completed = []
            
            for habit, is_completed in habits_data.items():
                if is_completed:
                    habits_completed.append(habit)
                else:
                    habits_not_completed.append(habit)
            
            if habits_completed:
                st.markdown("##### ✅ Completed")
                for habit in habits_completed:
                    st.markdown(f"<div class='habit-card completed'>• {habit}</div>", unsafe_allow_html=True)
            
            if habits_not_completed:
                st.markdown("##### ❌ Not Completed")
                for habit in habits_not_completed:
                    st.markdown(f"<div class='habit-card not-completed'>• {habit}</div>", unsafe_allow_html=True)

def progress_summary_screen():
    """Display progress summary with charts and stats."""
    st.title("Progress Summary")