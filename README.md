# Campus Connect – Campus Placement and Internship Management System 🎓

## About the Project
Campus Connect is a web-based Campus Placement and Internship Management System developed using Python Flask and MySQL. It provides a centralized platform to connect students, recruiters, and administrators and simplifies the campus recruitment process.

The system helps students manage their profiles and explore job and internship opportunities, while recruiters can manage company information and recruitment activities.

## Features

### Student Module
- Student registration and login
- Student dashboard
- View and edit student profile
- Upload resume
- Manage academic and personal details

### Recruiter Module
- Recruiter registration and login
- Recruiter dashboard
- Company registration and management
- Manage job and internship opportunities

### Admin Module
- Admin login and dashboard
- Manage users and system activities (if implemented)

### General Features
- Secure login and session management
- Form validation
- Role-based access
- Database integration

## Technologies Used
- **Python** – Backend programming
- **Flask** – Web application framework
- **MySQL** – Database management
- **HTML5** – Webpage structure
- **CSS3** – Styling and layout
- **Bootstrap 5** – Responsive user interface
- **JavaScript** – Frontend interactions (if implemented)

## Project Structure
```text
Campus-Connect/
│
├── app.py
├── templates/
│   ├── home.html
│   ├── login.html
│   ├── student_register.html
│   ├── recruiter_register.html
│   ├── dashboard.html
│   ├── profile.html
│   └── edit_profile.html
│
├── static/
│   └── style.css
│
├── uploads/
│   └── resumes/
│
└── README.md
```

*Note: Your actual folder and file structure may differ.*

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR-USERNAME/Campus-Connect.git
```

### 2. Open the Project Folder
```bash
cd Campus-Connect
```

### 3. Install Required Packages
```bash
pip install flask mysql-connector-python
```

### 4. Configure MySQL
- Create a MySQL database named `campus_placement`.
- Create the required tables.
- Update the database connection settings in `app.py`.

### 5. Run the Application
```bash
py app.py
```

### 6. Open in Browser
```text
http://127.0.0.1:5000
```

## Database
The project uses MySQL to store and manage application data, including:
- User details
- Student profiles
- Company information
- Job and internship details

## Project Objective
The main objective of Campus Connect is to digitize and simplify campus placement and internship management by providing a centralized platform for students, recruiters, and administrators.

## Future Enhancements
- Online application tracking
- Email notifications
- Resume analysis
- Advanced job search and filtering
- Placement statistics and reports

## Author
**Trisha Shetty**

## License
This project is developed for educational purposes.
