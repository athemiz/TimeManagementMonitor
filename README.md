
# Time Management Monitor

Time Management Monitor is a simple task management application designed to help you manage your daily tasks and events. It integrates with Google Calendar to automatically import events as tasks.

## Getting Started

### Prerequisites

-   Python 3.6 or higher
-   A Google Account with access to Google Calendar

### Installation

1.  Clone the repository or download the project files: `git clone https://github.com/athemiz/TimeManagementMonitor.git`
    
2.  Navigate to the project directory: `cd TimeManagementMonitor`
    
3.  Install the required dependencies using the `requirements.txt` file: `pip install -r requirements.txt`
    

### Google Calendar Configuration

1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
    
2.  Create a new project or select an existing one.
    
3.  Enable the Google Calendar API for your project. To do so, go to the [APIs & Services Dashboard](https://console.cloud.google.com/apis/dashboard), click on "+ ENABLE APIS AND SERVICES" at the top, search for "Google Calendar API" and enable it.
    
4.  Create OAuth 2.0 credentials by going to the [Credentials page](https://console.cloud.google.com/apis/credentials) and clicking on "Create credentials" > "OAuth client ID". Select "Desktop app" as the application type and give it a name.
    
5.  Download the generated `credentials.json` file by clicking on the download icon next to your newly created credentials on the [Credentials page](https://console.cloud.google.com/apis/credentials).
    
6.  Place the `credentials.json` file in the `TimeManagementMonitor` project directory.
    

### Running the Application

1.  Run the `run_app.bat` file.
    
2.  The application will open, and you will be prompted to sign in to your Google Account if it's your first time running the application. Grant the necessary permissions, and the application will start importing events from your calendar as tasks.
    
3.  Use the application to manage and track your tasks.
    

## Features

-   Create and manage tasks with a start and end time
-   Import events from Google Calendar as tasks
-   Save tasks for each day of the week and load them automatically when the program starts
-   Customize task colors

## License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).