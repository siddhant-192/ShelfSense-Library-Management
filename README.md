# ShelfSense - Library Management System

ShelfSense is a comprehensive web-based library management system that streamlines the operations of a library, including book management, user management, book issue tracking, and user feedback. The system is built using Flask, a Python web framework, and leverages various technologies for improved performance, scalability, and user experience.

## Features

- **Book Management**: Add, update, and manage book information, including title, authors, content, and associated sections.
- **User Management**: Maintain user accounts, roles, and permissions for secure access to the system.
- **Book Issue Tracking**: Track book issues, including user details, issue dates, and return dates.
- **User Feedback**: Allow users to provide feedback on specific books, fostering a collaborative and engaging library experience.
- **Role-Based Access Control**: Assign roles with varying permissions to users, ensuring appropriate access levels.
- **Caching**: Implement caching with Redis for improved system performance and reduced database load.
- **Task Scheduling**: Schedule and execute periodic tasks, such as sending daily reminders and generating monthly reports, using Celery.

## Technologies Used

- **Frontend**: Vue.js
- **Backend**: Flask (Python)
- **Database**: SQLite (SQLAlchemy for database management)
- **Authentication**: Flask-Security
- **Caching**: Redis
- **Task Scheduling**: Celery (RabbitMQ as the message broker)
- **RESTful API**: Flask-RESTful

## Installation

1. **Clone the Repository**:
   ```
   git clone https://github.com/siddhant-192/ShelfSense-Library-Management.git
   ```

2. **Install Python Requirements**:
   1. **Navigate to Your Project Directory**: Open your terminal or command prompt and navigate to the directory where your `app.py` file is located.
   2. **Install requirements**: Run the following command
      ```
       pip3 install -r requirements.txt
       ```


4. **Install Node Requirements**:
   1. **Navigate to Your Project Directory**: Open your terminal or command prompt and navigate to the directory where your `package.json` and `node_requirements.txt` files are located.
   2. **Generate a** `package.json` **File** (if not already present): If you don't have a `package.json` file, create one by running the following command:
      ```bash
      npm init -y
      ```
   3. **Install Dependencies from** `node_requirements.txt`: Run the following command to install all the required dependencies listed in your `node_requirements.txt` file:
      ```bash
      npm install
      ```
      This command will resolve the dependencies based on the information in your `package.json` file and install the necessary modules into the `node_modules` folder.
   4. **Verify Installation**: After the installation completes, you can verify that the modules are installed by checking the `node_modules` folder in your project directory.

5. **Run the Application**:
   1. **Start the Python Application**: Go to the project folder and run:
      ```
      python3 app.py
      ```
   2. **Start the Frontend**: Go to the frontend folder and run:
      ```
      npm run serve
      ```
   3. **Install MailHog**: Refer to the [MailHog](https://github.com/mailhog/MailHog) repository for installation instructions.
   4. **Run MailHog**: In your terminal, run:
      ```
      mailhog
      ```
   5. **Run Redis Server**:
      ```
      redis-server
      ```
   6. **Run Celery Worker Server**:
      ```
      celery -A app:celery_app worker --loglevel INFO
      ```
   7. **Run Celery Beat Server**:
      ```
      celery -A app:celery_app beat --loglevel INFO
      ```

## Getting Started

To get a local copy of the project up and running, follow the steps in the [Installation](#installation) section.


## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [Vue.js](https://vuejs.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Flask-Security](https://flask-security.readthedocs.io/)
- [Redis](https://redis.io/)
- [Celery](https://docs.celeryq.dev/)
- [Flask-RESTful](https://flask-restful.readthedocs.io/)
