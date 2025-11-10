# 🧭 ResQNet — Integrated Disaster Management & Safety System

ResQNet is a **multi-module AI-powered web application** that integrates **real-time disaster management**, **fake news detection**, **a multilingual chatbot**, and **safehouse navigation** into one unified platform.  

Developed using **Flask**, **Python**, and **Machine Learning**, it enables users to access verified safety information, locate nearby shelters, and communicate seamlessly during emergencies.

---

## 🌟 Key Features

### 🧭 1. Navigation & Safehouse System
- Interactive grid-based village map.
- Identifies the nearest safehouse with available capacity.
- Route generation with step-by-step directions.
- Admin panel to mark hazards and reset shelters.

### 🗣️ 2. Multilingual Chatbot
- Built with **Flask** and **Whisper + SentenceTransformer** models.
- Supports **speech-to-text** and **text-based** queries.
- Provides real-time safety, health, and emergency assistance.

### 📰 3. Fake News Detection
- AI model trained to classify fake vs real news articles.
- Uses **Natural Language Processing (NLP)** to analyze user-submitted news.
- Helps prevent misinformation during crisis situations.

### 🔐 4. User Authentication System
- User & Admin login pages built with Flask and SQLAlchemy.
- Passwords secured using **Werkzeug hashing**.
- Session-based login persistence with global cookie management.


## 🧩 Application Architecture
            ┌────────────────────────────┐
            │         Landing App        │
            │ (Main DispatcherMiddleware)│
            └─────────────┬──────────────┘
                          │
            
     ┌────────────────┬────────────────────┬──────────────────┐
     │                │                    │                  │
    ┌────────┐  ┌─────────────┐      ┌─────────────┐       ┌────────────┐
    │ auth   │  │ Navi System │      │   Fake News │       │ Chatbot    │
    │ (Login)│  │ (Safehouses)│      │ Detection   │       │ Assistant  │
    └────────┘  └─────────────┘      └─────────────┘       └────────────┘



## All Flask modules are integrated using:
```python
application = DispatcherMiddleware(
    landing_app,
    {
        "/auth": auth_app,
        "/navi": navi_app,
        "/chatbot": chatbot_app,
        "/fakenews": fake_app,
    },
)
```
# 🧠 Tech Stack

----------------------------------------------------------------------------------------------------------------------
| Layer          | Technology                                                                                        |
| -------------- | ------------------------------------------------------------------------------------------------- |
| **Frontend**   | HTML5, CSS3, JavaScript (Vanilla JS)                                                              |
| **Backend**    | Flask (Python 3), Gunicorn                                                                        |
| **Database**   | SQLite (via SQLAlchemy ORM)                                                                       |
| **AI Models**  | Whisper (Speech Recognition), SentenceTransformer (Chatbot), NLP Classifier (Fake News Detection) |
| **Deployment** | Render (Cloud Hosting)                                                                            |
| **Security**   | Werkzeug Password Hashing, Flask Sessions, Flask-CORS                                             |
----------------------------------------------------------------------------------------------------------------------

# ⚙️ Installation Guide (Local Setup)

## 1️⃣ Clone the Repository
git clone https://github.com/Harsha2614/ResQNet.git
cd ResQNet

## 2️⃣ Install Dependencies
pip install -r requirements.txt

## 3️⃣ Run the Application
python combined.py


Then open your browser at:
👉 http://127.0.0.1:8000

# 🧾 Folder Structure

ResQNet/

├── main.py                 # Combines all Flask modules

├── auth_app.py             # Authentication routes (login/signup)

├── Navi/

│   ├── app.py              # Navigation + Safehouse logic

│   ├── models.py

│   └── static/js/grid.js   # Grid-based map interaction

├── FakeNews/

│   ├── app.py              # Fake News detection module

│   ├── model.pkl

│   └── templates/

├── chatbot/

│   ├── app_backend.py      # Chatbot API + Whisper Integration

│   └── templates/

├── templates/

│   └── index.html

├── requirements.txt

├── session_config.py

└── Procfile

# 🧩 Core Backend Concepts

Werkzeug Security: Handles password hashing & verification.

SQLAlchemy ORM: Simplifies database CRUD operations.

DispatcherMiddleware: Combines multiple Flask apps into one.

Flask-CORS: Enables frontend-backend communication securely.

Gunicorn: Runs the app in production on Render.

# 🧠 Frontend & JS Overview
------------------------------------------------------------------------------------------------
| File                        | Purpose                                                        |
| --------------------------- | -------------------------------------------------------------- |
| `templates/*.html`          | Defines UI for chatbot, login, and safehouses.                 |
| `static/js/grid.js`         | Draws interactive grid map, safehouse logic, hazard placement. |
| `chatbot/static/js/chat.js` | Handles chat UI, mic recording, and API requests.              |
| `style.css`                 | Modern responsive UI design with gradient animations.          |
------------------------------------------------------------------------------------------------
# 🧩 Important Terms
------------------------------------------------------------------------------------------------------
| Term                     | Definition                                                              |
| ------------------------ | ----------------------------------------------------------------------- |
| **CORS**                 | Cross-Origin Resource Sharing – allows frontend to access backend APIs. |
| **Gunicorn**             | A production WSGI HTTP server for running Flask apps on Render.         |
| **DispatcherMiddleware** | Flask/WSGI tool that merges multiple apps into one endpoint.            |
| **Werkzeug**             | Flask’s core utility library for security, routing, and WSGI handling.  |
| **SQLAlchemy**           | ORM layer that connects Python objects to database tables.              |
| **Flask-CORS**           | Adds CORS headers for cross-domain JS communication.                    |
------------------------------------------------------------------------------------------------------

# 👨‍💻 Developed By

Narayana Harsha Vardhan (chatbot and Integration)  

Malapati Saketh Reddy (navigator)

Alla Sai Vinay (Fake news detector)

🎓 B.Tech Computer Science and Engineering
📍 VIT-AP University

# 💡 Future Enhancements

Add real-time weather and flood alert API.

SMS alert system for registered users.

Interactive 3D safehouse mapping.

Integration with IoT-based sensors.
