# Study Resource Sharing Platform (StudyShare)

A simple web platform where students can upload, share, and download study materials such as notes, PDFs, and useful links.

## Features

| Module | Description |
|--------|-------------|
| **User Authentication** | Sign up, login, logout, and basic profile management |
| **Upload Resources** | Upload PDFs/notes or share links with title, subject, and description |
| **Browse & Download** | View all resources and download files or open links |
| **Search** | Filter by subject or search by keyword |
| **Admin Control** | Manage resources, remove inappropriate files, manage admin roles |

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite (via SQLAlchemy)
- **Auth:** Flask-Login with password hashing
- **Frontend:** Bootstrap 5, Jinja2 templates

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

### 3. Default admin account

On first run, a default admin account is created:

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

Change the password after first login via **Profile → Edit Profile**.

You can customize admin credentials with environment variables:

```bash
set ADMIN_USERNAME=myadmin
set ADMIN_PASSWORD=securepassword
set ADMIN_EMAIL=admin@example.com
python app.py
```

## Project Structure

```
Study material/
├── app.py              # Application entry point
├── config.py           # Configuration settings
├── models.py           # User and Resource database models
├── extensions.py       # Flask extensions (db, login)
├── routes/
│   ├── auth.py         # Signup, login, profile
│   ├── resources.py    # Browse, upload, download, search
│   └── admin.py        # Admin dashboard
├── templates/          # HTML templates
├── static/css/         # Stylesheets
├── uploads/            # Uploaded files (created at runtime)
└── requirements.txt
```

## Usage Guide

1. **Register** a new student account or use the admin account.
2. **Browse** resources on the home page; use the search bar and subject filter.
3. **Upload** materials (login required) — choose PDF, Note, or Link type.
4. **Download** files or open shared links from the browse or detail pages.
5. **Admin** users can access the Admin panel to remove resources and manage user roles.

## Supported File Types

- PDF (`.pdf`)
- Text notes (`.txt`)
- Word documents (`.doc`, `.docx`)

Maximum upload size: **16 MB**
