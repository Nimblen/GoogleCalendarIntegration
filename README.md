## Google Calendar App
### This project is a Python application for interacting with Google Calendar via the Google API. It allows you to manage calendars and events programmatically using a server-side solution.

Requirements
Python 3.9.2
Google API Client Libraries
client_secret.json and creds.json files for Google OAuth
Project Structure

├── auth/
│   ├── __init__.py
│   ├── gapiworkspace.py
├── event/
│   ├── __init__.py
│   ├── gevent.py
├── gcalendar/
│   ├── __init__.py
│   ├── gcalendar.py
├── scripts/
│   ├── run.sh
│   ├── setup.sh
├── venv/  # Virtual environment directory
├── main.py
├── requirements.txt
├── README.md
└── .env/  # Directory for your OAuth credentials
    ├── client_secret.json
    ├── creds.json


Setup Instructions
Step 1: Clone the repository
First, clone this repository to your local machine:


git clone https://your-repository-url
cd google-calendar-app
Step 2: Setup Python Virtual Environment
If you haven't created a virtual environment yet, you can do so using the following command:


python -m venv venv
Activate the virtual environment:

For Windows:


.\venv\Scripts\activate
For Linux/macOS:


source venv/bin/activate
Step 3: Install Dependencies
Once inside the virtual environment, run the following script to install the required Python packages:


./scripts/setup.sh
Step 4: Set Executable Permissions (For Linux/macOS)
Make the setup.sh script executable by running the following command:


chmod +x scripts/setup.sh
Step 5: Running the Application
You can now run the application by executing the run.sh script:


./scripts/run.sh
This script will:

Install any required dependencies using setup.sh.
Run the main.py file, which interacts with Google Calendar.
Environment Variables and OAuth Setup
Ensure that you have the following files in your .env/ directory:

client_secret.json: This file contains your Google OAuth credentials.
creds.json: This file will store the token information after your first authentication.
Log Files
Logs from the application will be written to the app.log file, located in the project root.

License
MIT License