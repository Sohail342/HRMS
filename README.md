# HRMS - Human Resource Management System

![HRMS Logo](https://img.shields.io/badge/HRMS-Human%20Resource%20Management%20System-blue)
![Django](https://img.shields.io/badge/Django-5.1.2-green)
![Python](https://img.shields.io/badge/Python-3.13+-yellow)

A comprehensive Human Resource Management System built with Django to streamline employee management, attendance tracking, leave management, and reporting processes.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Environment Setup](#environment-setup)
- [Running the Application](#running-the-application)
- [Admin Access](#admin-access)
- [Usage Guide](#usage-guide)
- [Contributing](#contributing)

## ✨ Features

### 👥 Employee Management
- Complete employee profile management
- Employee onboarding and offboarding
- Organization structure (Regions, Branches, Divisions, Wings)
- Employee transfers and promotions tracking
- Document management (educational documents, contracts)

### 📊 Attendance Management
- Employee attendance tracking
- Non-involvement certificate requests
- Contract renewal processing
- Stationary requests

### 🗓️ Leave Management
- Multiple leave types (Privileged, Casual, Sick, Ex-Pakistan)
- Leave balance tracking and carry-forward
- Mandatory leave management
- Leave application workflow with approvals

### 📝 Reporting
- Expenditure tracking
- Family member management
- Letter templates and signature management
- Custom reports generation

### 🔍 Additional Features
- Employee search functionality
- Analytics dashboard
- Role-based access control
- Group head management

## 🏗️ Project Structure

The project follows a modular Django application structure:

```
HRMS/
├── apps/                   # Main application modules
│   ├── HRIS_App/           # Core HR functionality
│   ├── account/            # User authentication
│   ├── analytics/          # Data analytics
│   ├── employee_attendance/ # Attendance tracking
│   ├── employee_search/    # Employee search functionality
│   ├── employee_user/      # Employee user management
│   ├── group_head/         # Group head management
│   ├── leave_management/   # Leave application and tracking
│   ├── reporting/          # Reporting functionality
│   └── transfer_employees/ # Employee transfer management
├── config/                 # Project configuration
│   ├── settings/           # Environment-specific settings
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI configuration
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── manage.py               # Django management script
├── requirements.txt        # Project dependencies
└── README.md               # Project documentation
```

## 🛠️ Technology Stack

- **Backend**: Django 5.1.2, Python 3.13+
- **Database**: Compatible with PostgreSQL, MySQL, SQLite
- **Frontend**: HTML, CSS, JavaScript, Django Templates
- **File Storage**: Cloudinary
- **Additional Libraries**:
  - django-import-export for data import/export
  - django-unfold for admin interface
  - django-tailwind for styling
  - django-extensions for development utilities

## 🚀 Installation

### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)
- Virtual environment tool (venv, virtualenv, or conda)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd HRMS
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🌐 Environment Setup

1. Create a `.env` file in the project root with the following variables:
   ```
   ENVIRONMENT=development
   SECRET_KEY=your_secret_key
   DEBUG=True
   
   # Database configuration (if using PostgreSQL)
   DATABASE_URL=postgres://user:password@localhost:5432/hrms
   
   # Cloudinary configuration
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

## 🏃‍♂️ Running the Application

1. Apply migrations:
   ```bash
   python manage.py migrate
   ```

2. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

3. Start the development server:
   ```bash
   python manage.py runserver
   ```

4. Access the application at http://127.0.0.1:8000/

## 👑 Admin Access

Access the admin interface at http://127.0.0.1:8000/admin/ using the superuser credentials created earlier.

## 📖 Usage Guide

### Employee Management

1. **Adding Employees**: Navigate to the admin panel or use the employee creation form
2. **Viewing Employee Details**: Use the employee search functionality or browse by department/region
3. **Managing Documents**: Upload and manage employee documents through the document management interface

### Leave Management

1. **Applying for Leave**: Employees can submit leave applications through the leave management interface
2. **Approving Leaves**: Managers can review and approve/reject leave applications
3. **Checking Leave Balance**: Employees can view their remaining leave balance

### Attendance Management

1. **Tracking Attendance**: Record and monitor employee attendance
2. **Processing Requests**: Handle non-involvement certificates and other attendance-related requests

### Reporting

1. **Generating Reports**: Create custom reports based on various HR metrics
2. **Managing Templates**: Create and use letter templates for official communications

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

Developed with ❤️ for efficient human resource management.