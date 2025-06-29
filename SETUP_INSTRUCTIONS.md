# Maison Trüvra Backend Setup Instructions

## Prerequisites

Before running the backend, ensure you have the following installed and configured:

### 1. Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Redis Installation and Setup

#### Option A: Using Homebrew (macOS - Recommended)
```bash
# Install Redis
brew install redis

# Start Redis as a service
brew services start redis

# Check if Redis is running
redis-cli ping
# Should return: PONG
```

#### Option B: Using Docker (Cross-platform)
```bash
# Run Redis in Docker
docker run -d --name redis-maison-truvra -p 6379:6379 redis:alpine

# Check if Redis is running
docker ps | grep redis
```

#### Option C: Manual Installation
- **Ubuntu/Debian**: `sudo apt-get install redis-server`
- **CentOS/RHEL**: `sudo yum install redis`
- **Windows**: Download from https://redis.io/download

### 3. Environment Variables Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file and update the following critical variables:
   ```bash
   # Generate secure keys
   SECRET_KEY=your-super-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   
   # Email configuration (for notifications)
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   FROM_EMAIL=your-email@gmail.com
   ```

3. **Generate secure keys** (run these commands and copy the output):
   ```bash
   # Generate SECRET_KEY
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Generate JWT_SECRET_KEY
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Generate ENCRYPTION_KEY
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

### 4. Database Setup

```bash
# Initialize database
python3 manage.py db init

# Create migration
python3 manage.py db migrate -m "Initial migration"

# Apply migration
python3 manage.py db upgrade

# (Optional) Seed database with sample data
python3 -c "from backend.seed import seed_database; seed_database()"
```

### 5. Email Configuration (Optional but Recommended)

For Gmail SMTP:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://support.google.com/accounts/answer/185833
3. Use the App Password in `SMTP_PASSWORD`

## Running the Application

### Option 1: Using the Development Script
```bash
# Make sure the script is executable
chmod +x start_dev.sh

# Run the development environment
./start_dev.sh
```

### Option 2: Manual Start
```bash
# Terminal 1: Start Redis (if not running as service)
redis-server

# Terminal 2: Start Flask backend
export FLASK_APP=manage.py
export FLASK_ENV=development
python3 -m flask run --port=5000

# Terminal 3: Start Celery worker (optional, for background tasks)
celery -A backend.celery_worker.celery worker --loglevel=info

# Terminal 4: Start frontend (in website directory)
cd website
npm install
npm run dev
```

## Verification

1. **Backend**: Visit http://localhost:5000 - should show "Welcome to Maison Trüvra"
2. **Frontend**: Visit http://localhost:5173 - should show the Vue.js application
3. **Redis**: Run `redis-cli ping` - should return "PONG"
4. **API**: Visit http://localhost:5000/api/health - should return health status

## Troubleshooting

### Redis Connection Issues
```bash
# Check if Redis is running
redis-cli ping

# Check Redis logs
tail -f /usr/local/var/log/redis.log  # macOS with Homebrew

# Restart Redis
brew services restart redis  # macOS
sudo systemctl restart redis  # Linux
```

### Database Issues
```bash
# Reset database (WARNING: This will delete all data)
rm backend/dev.db
python3 manage.py db upgrade

# Check database tables
python3 -c "from backend import create_app; from backend.extensions import db; app = create_app(); app.app_context().push(); print(db.engine.table_names())"
```

### Import/Module Issues
```bash
# Ensure you're in the project root directory
pwd  # Should show the project root

# Ensure virtual environment is activated
which python3  # Should show path to venv/bin/python3

# Reinstall dependencies
pip install -r backend/requirements.txt
```

### Port Conflicts
If ports 5000 or 5173 are in use:
```bash
# Find processes using the ports
lsof -i :5000
lsof -i :5173

# Kill processes if needed
kill -9 <PID>

# Or use different ports in .env file
```

## Production Deployment Notes

1. Set `FLASK_ENV=production` in `.env`
2. Use a proper database (PostgreSQL recommended)
3. Use a reverse proxy (nginx)
4. Set up proper SSL certificates
5. Use environment-specific configuration files
6. Set up monitoring and logging
7. Use a process manager (systemd, supervisor, or Docker)

## Support

If you encounter issues:
1. Check the logs in the `logs/` directory
2. Ensure all environment variables are set correctly
3. Verify Redis and database connections
4. Check that all required ports are available