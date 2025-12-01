NoteNest Backend

This is the backend service for NoteNest, a fast and lightweight note-taking system built with a focus on simplicity, speed, and reliability.
The backend is powered by Flask and Appwrite, exposing a clean API for users, notes, folders, chapters, payments, and file handling.

🚀 Features

    User Authentication Token-based email/password login.
    
    Notes System Create, update, delete, organize, and fetch notes.
    
    Folder & Chapter Support Structured note organization.
    
    Payments Integration Paystack-powered credit and subscription handling.
    
    File Storage Upload, fetch, and delete files through backend endpoints.
    
    Modular Architecture Routes, services, models, and utils organized for long-term maintainability.

🏗 Project Structure
notenest-backend/
    ├── app.py
    ├── requirements.txt
    ├── .env.example
    ├── .render.yaml
    ├── config/
    │   └── appwrite.py
    ├── routes/
    │   ├── notes.py
    │   ├── users.py
    │   ├── payments.py
    │   └── files.py
    ├── services/
    │   ├── notes_service.py
    │   ├── users_service.py
    │   ├── payments_service.py
    │   └── files_service.py
    ├── models/
    │   └── schemas.py
    ├── utils/
    │   ├── auth.py
    │   ├── validation.py
    │   └── errors.py
    └── chroma/
        └── chroma_setup.py


Each feature lives in its own route and service. Validation and error-handling are centralized so the codebase stays clean as the app grows.

📦 Installation

Clone the repo:

git clone https://github.com/yourusername/notenest-backend.git
cd notenest-backend


*Install dependencies:*

        pip install -r requirements.txt
        
        
        Copy the environment file:
        
        cp .env.example .env


Fill in your environment variables:

Appwrite endpoint

Appwrite project ID

Database and collection IDs

Paystack keys

File settings

▶️ Running the Server

Run directly:

python app.py


Or via Flask CLI:

flask run


Default address:

http://localhost:5000

🔌 API Overview

All endpoints live under /api/.

Area	Base Path	Description
Users	/api/users	Authentication, profiles
Notes	/api/notes	CRUD notes and organization
Payments	/api/payments	Credit purchases and Paystack verification
Files	/api/files	Upload, download, delete

A complete API collection will be added soon.

☁️ Deployment (Render)

This repo includes:

.render.yaml for automated deployment

Production environment configuration

Automatically triggered deploys from GitHub

Connect the repo to Render and deploy both services as defined.

🛠 Development Notes

Routes handle request/response only.

Business logic lives in the service layer.

Validation schemas keep data clean.

Centralized authentication and error-handling make behavior consistent.

The structure is designed for growth, testing, and easy onboarding of new contributors.
