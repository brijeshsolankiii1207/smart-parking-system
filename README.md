# 🚗 Smart Parking System (ParkEasy)

A full-stack parking management system built with Django that allows users to book parking slots, manage vehicles, and track availability in real-time.

---

## 🔥 Features

* User authentication (Signup / Login)
* Book and manage parking slots
* Real-time slot availability (Basement, Ground, Floors)
* Cancel bookings
* Parking charge calculation
* User dashboard

---

## 🛠️ Tech Stack

* **Backend:** Django (Python)
* **Frontend:** HTML, CSS, Bootstrap
* **Database:** SQLite (Local) / PostgreSQL (Production)
* **Deployment:** Railway

---

## 🚀 Live Demo

👉 https://web-production-56714.up.railway.app

---

## ⚙️ Installation (Local Setup)

```bash
git clone https://github.com/brijeshsolankii1207/smart-parking-system.git
cd smart-parking-system
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 📂 Project Structure

```
smart-parking-system/
│── parking/
│── pms/
│── static/
│── templates/
│── manage.py
│── requirements.txt
│── Procfile
```

---

## ⚠️ Notes

* Static files are handled using WhiteNoise
* Railway is used for production deployment
* Free hosting may have cold start delays

---

## 📌 Author

**Brijesh Solanki**



