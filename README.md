# 🏫 Smart College Assistant

Smart College Assistant is an all-in-one, modern Django-based university portal. It integrates traditional academic administration (timetables, notices, study notes, assignment submissions) with cutting-edge utilities like **Dynamic QR-Code Attendance Tracking** and a **Context-Aware Google Gemini AI Chatbot**.

---

## 🚀 Key Modules & Features

### 1. 🔐 User Accounts & Custom Dashboards
* **Role-Based Portals**: Dedicated, structured dashboards for **Students**, **Teachers**, and **Admins**.
* **Profile Completeness**: Multi-step registration flow with profiles detailing semester, department, roll number, or teacher designation.
* **Custom Admin Panel**: Visual overview of registrations, notices, and department status.

### 2. ⚡ QR-Code Attendance Tracking
* **Dynamic Generation**: Teachers can generate class session QR codes mapped to specific subjects.
* **Anti-Cheating Mechanisms**: QR sessions can be dynamically refreshed to invalidate previous session screenshots and prevent proxy marking.
* **Real-time Camera Scan**: Students scan the live QR code directly via their device's webcam to mark their attendance.
* **Reports**: Breakdown of student attendance rates (both manual and scanned inputs).

### 3. 📝 Study Notes Repository
* **File Uploads**: Teachers and students can easily upload course materials, lecture notes, and PDFs.
* **Directory Listings**: Filterable directory for downloading peer-shared notes.

### 4. 📂 Assignment Submissions & Grading
* **Submission Portal**: Students can view active assignments, download attachments, and submit their files.
* **Grading System**: Teachers view all submissions, assign marks, and provide grading feedback.

### 5. 📢 Notice Board
* **Campus Updates**: Official board displaying announcements from department heads or administrators.
* **JSON APIs**: Live notices are indexed dynamically for AI model querying.

### 6. 🤖 Context-Aware Gemini Chatbot
* **Gemini Core**: Interfaces with the `google-genai` SDK using `gemini-2.5-flash`.
* **Deep Integration**: The chatbot is automatically initialized with user context:
  * **For Students**: Hydrated with the student's department, current semester, live attendance percentage, timetables, and pending assignments.
  * **For Teachers**: Hydrated with assigned subject timetables and designation.
* **Smart Queries**: Answers specific timetable requests, assignment due dates, or general knowledge questions contextually.

---

## 🛠️ Technology Stack

* **Backend**: Django (Python 3)
* **Database**: SQLite (Development)
* **AI Engine**: Google Gemini Developer API (`google-genai` SDK, `gemini-2.5-flash` model)
* **QR Services**: `qrcode`, `Pillow`
* **CSS Framework**: Bootstrap 5
* **State Management**: standard Django sessions and CSRF protections

---

## ⚙️ Installation & Local Setup

### 1. Clone & Navigate
```bash
git clone <repository-url>
cd CollegeDjango
```

### 2. Set Up Virtual Environment
Create and activate a python virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create or update the `.env` file in the root project folder:
```ini
SECRET_KEY=django-insecure-smart-college-assistant-dev-key
DEBUG=True
GEMINI_API_KEY=your_google_gemini_api_key_here
```

### 5. Run Database Migrations
Create database tables:
```bash
python manage.py migrate
```

### 6. Start Development Server
```bash
python manage.py runserver
```

Now, navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 📂 Project Architecture

```
CollegeDjango/
│
├── smart_college_assistant/   # Main settings, routing, and configurations
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                  # User logins, registration, and profile complete dashboard
├── attendance/                # QR code generation, scanning, and reports
├── assignments/               # Assignment uploads, submissions, and grading
├── chatbot/                   # Context gathering service and Gemini API integrations
├── courses/                   # Subjects, semesters, and class timetables
├── notes/                     # Shareable notes directory
├── notices/                   # Notifications system
│
├── templates/                 # Global UI layouts and app HTML files
├── static/                    # Custom CSS, JS scripts, and brand assets
│
├── .env                       # Environment configs
├── requirements.txt           # App requirements list
└── manage.py                  # Django administrative script
```
