# 🍲 Rescue Meal

**Rescue Meal** is a full-stack web application designed to eliminate food waste and reduce hunger by bridging the gap between food donors (restaurants, hotels, event organizers, individuals) and NGOs/shelters in need.

---

## ✨ Features

- **🔑 Multi-Role Authentication**
  - Secure registration and login for **Donors**, **NGOs**, and **Admins**.
  - Password hashing and secure session management.

- **🍱 Donor Dashboard**
  - Post surplus food listings with details such as food type, quantity, prepared date/time, expiry window, and pickup location.
  - Track donation status and pickup history.

- **🤝 NGO Dashboard**
  - Real-time view of available food donations nearby.
  - Request and claim food listings to feed communities efficiently.

- **🛡️ Admin Dashboard**
  - Complete overview of system activity, user management, and donation statistics.
  - Verify and manage donor and NGO accounts.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-CORS, Werkzeug Security
- **Database:** MySQL
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Server:** Flask Web Server (Serves API endpoints + static frontend assets)

---

## 📁 Project Structure

```
RESCUE MEAL/
├── backend/
│   ├── app.py              # Main Flask application & REST API routes
│   ├── config.py           # Configuration settings
│   ├── test_db.py          # Database connection test utility
│   └── frontend/           # Static Web Interfaces
│       ├── index.html      # Main landing / dashboard page
│       ├── login.html      # User login page
│       ├── register.html   # User registration page
│       ├── donor-dashboard.html # Donor management interface
│       ├── ngo-dashboard.html   # NGO claim interface
│       ├── admin-dashboard.html # System admin dashboard
│       ├── about.html      # About page
│       ├── style.css       # Custom styling & dynamic UI theme
│       └── script.js       # Client-side logic & API interaction
├── .gitignore              # Ignored files (venv, cache, configs)
└── README.md               # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- [Python 3.8+](https://www.python.org/downloads/)
- [MySQL Server](https://dev.mysql.com/downloads/mysql/)

---

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Josiyaa/RESCUE_MEAL.git
   cd RESCUE_MEAL
   ```

2. **Set Up Python Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   # On Linux / macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install flask flask-cors mysql-connector-python werkzeug
   ```

4. **Database Configuration**
   - Create a MySQL database named `rescuemeal`.
   - Update database credentials in `backend/app.py` or `backend/config.py` if necessary:
     ```python
     host="localhost",
     user="root",
     password="YOUR_MYSQL_PASSWORD",
     database="rescuemeal"
     ```

5. **Run the Application**
   ```bash
   cd backend
   python app.py
   ```

6. **Access the Website**
   Open your browser and navigate to:
   ```text
   http://127.0.0.1:5000/dashboard
   ```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to check out the [issues page](https://github.com/Josiyaa/RESCUE_MEAL/issues).

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
