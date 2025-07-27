# Repository Information Overview

## Repository Summary
Maison Truvrā is a comprehensive e-commerce platform designed for both B2C and B2B operations. It features a Flask backend and a Vue.js frontend, supporting advanced product management, inventory control, user accounts, and loyalty programs.

## Repository Structure
- **backend/**: Flask backend application with API routes, models, and services
- **website/**: Vue.js frontend application with components and views
- **.zencoder/**: Documentation and configuration files
- **manage.py**: CLI commands for the application

### Main Repository Components
- **Backend API**: Flask-based REST API with B2C and B2B endpoints
- **Admin Panel**: Administrative interface for managing products, orders, and users
- **Frontend Store**: Vue.js-based customer-facing storefront
- **Authentication System**: Unified auth with MFA support

## Projects

### Backend (Flask Application)
**Configuration File**: backend/requirements.txt

#### Language & Runtime
**Language**: Python
**Version**: Python 3.9+ (3.12 recommended)
**Framework**: Flask 3.0.2
**Database**: PostgreSQL 14+
**Package Manager**: pip

#### Dependencies
**Main Dependencies**:
- Flask-JWT-Extended 4.7.1
- SQLAlchemy 1.4.46
- Flask-Migrate 4.0.5
- Celery 5.5.3
- Redis 4.5.1
- Flask-SQLAlchemy 3.1.1
- Flask-Mail 0.9.1
- Flask-Talisman 1.1.0

**Development Dependencies**:
- Bandit
- Safety
- Playwright 1.53.0

#### Build & Installation
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
python seed.py
```

#### Testing
**Framework**: Built-in Python unittest
**Test Location**: Root directory
**Run Command**:
```bash
python -m unittest discover
```

### Frontend (Vue.js Application)
**Configuration File**: website/package.json

#### Language & Runtime
**Language**: JavaScript
**Version**: Node.js 18+
**Framework**: Vue.js 3.2.47
**Build Tool**: Vite 5.3.1
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- Vue 3.2.47
- Vue Router 4.2.0
- Pinia 2.0.35
- Axios 1.4.0
- Vue-i18n 9.2.2
- Vee-validate 4.12.8
- Socket.io-client 4.8.1

**Development Dependencies**:
- Tailwind CSS 3.3.2
- Vitest 1.6.0
- PostCSS 8.4.23
- Vite 5.3.1

#### Build & Installation
```bash
cd website
npm install
npm run dev  # Development server
npm run build  # Production build
```

#### Testing
**Framework**: Vitest
**Test Location**: website/src/tests
**Run Command**:
```bash
cd website
npm run test
```

### Task Queue System
**Configuration File**: backend/celery_worker.py

#### Language & Runtime
**Language**: Python
**Framework**: Celery 5.5.3
**Message Broker**: Redis

#### Dependencies
**Main Dependencies**:
- Celery 5.5.3
- Redis 4.5.1
- APScheduler 3.11.0

#### Usage & Operations
**Key Commands**:
```bash
# Start Celery worker
celery -A backend.tasks.celery worker --loglevel=info

# Start Celery beat for scheduled tasks
celery -A backend.tasks.celery beat --loglevel=info
```