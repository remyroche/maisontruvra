# Maison Truvrā E-commerce Platform

Maison Truvrā is a comprehensive, modern e-commerce platform designed for both B2C (Business-to-Consumer) and B2B (Business-to-Business) operations. It features a robust backend built with Flask and a reactive frontend using Vue.js.

## ✨ Key Features

- **Dual B2C/B2B Functionality**: Separate product visibility, pricing, and user experiences.
- **Advanced Product Management**: Support for product variants, categories, collections, and custom attributes.
- **Inventory Control**: Real-time stock tracking with inventory reservation for carts to prevent overselling.
- **Comprehensive Order System**: Manages orders from creation to fulfillment, including guest checkouts.
- **User Account System**:
    - Separate B2C and B2B user profiles.
    - Secure authentication with JWT.
    - Multi-Factor Authentication (2FA/MFA) for enhanced security.
    - User address book management.
- **Loyalty & Referral Program**: Tier-based loyalty system with points, vouchers, and referral rewards.
- **Full-Featured Admin Panel**:
    - User, product, order, and B2B account management.
    - Role-Based Access Control (RBAC) with granular permissions.
    - System monitoring, audit logs, and site settings management.
- **Content Management**: Integrated blog system with categories and posts.
- **Automated PDF Generation**: Creates PDF invoices and unique Product Passports for traceability.
- **Asynchronous Operations**: Uses Celery and Redis for background tasks like sending emails and processing orders.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy, PostgreSQL
- **Frontend**: Vue.js, Vite
- **Task Queue**: Celery
- **Caching/Broker**: Redis
- **Authentication**: Flask-JWT-Extended
- **Database Migrations**: Flask-Migrate

## 📂 Project Structure

```
/
├── backend/         # Flask backend application
│   ├── admin_api/   # Admin-specific API routes
│   ├── auth/        # Authentication routes and logic
│   ├── b2b/         # B2B-specific routes
│   ├── models/      # SQLAlchemy database models
│   ├── services/    # Business logic services
│   ├── tasks.py     # Celery background tasks
│   ├── requirements.py
│   └── ...
├── website/         # Vue.js frontend application
│   ├── public/
│   ├── src/
│   └── package.json
├── instance/        # Instance-specific files (e.g., uploads, db)
├── logs/            # Application logs
├── manage.py        # CLI commands for the application
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+ & npm
- PostgreSQL 14+
- Redis

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd <project-directory-name>
```

### 2. Backend Setup

```bash
# Navigate to the backend directory
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r ../requirements.txt

# Create a .env file from the example in the project root
cd ..
cp .env.example .env

# Edit the .env file with your local configuration (database, redis, etc.)
# Make sure to generate a new ENCRYPTION_KEY. You can use:
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set up the database
flask db upgrade

# Seed the database with initial roles and data
python backend/seed.py

# Create an initial admin user
# You will be prompted to scan a QR code for MFA setup.
flask create-admin your-admin-email@example.com your-secure-password
```

### 3. Frontend Setup

```bash
# Navigate to the frontend directory
cd website

# Install npm dependencies
npm install

# The frontend may require its own .env file for variables like VITE_API_BASE_URL
# to connect to the backend.
```

## 🏃 Running the Application

You will need to run multiple processes in separate terminal windows.

1.  **Start the Backend Server:**
    ```bash
    # From the root directory, with the backend venv activated
    flask run
    ```

2.  **Start the Frontend Dev Server:**
    ```bash
    # From the root directory
    cd website
    npm run dev
    ```

3.  **Start the Celery Worker:**
    ```bash
    # From the root directory, with the backend venv activated
    celery -A backend.tasks.celery worker --loglevel=info
    ```

4.  **Start Celery Beat (for scheduled tasks):**
    ```bash
    # From the root directory, with the backend venv activated
    celery -A backend.tasks.celery beat --loglevel=info
    ```

The application should now be accessible at your `FRONTEND_URL` (e.g., `http://localhost:5173`).

## 🧪 Running Tests & Audits

This project includes a custom security audit script.

```bash
# From the root directory
run_audits.sh
```

## 📄 License

This project is proprietary. All rights reserved.
