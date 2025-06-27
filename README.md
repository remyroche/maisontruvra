Maison Truvra - Premium Truffle E-Commerce PlatformMaison Truvra is a comprehensive e-commerce solution designed for the sale of premium truffles and truffle-based products. The platform caters to both individual consumers (B2C) and professional clients (B2B), offering a tailored experience for each segment. It includes a sophisticated administrative backend for managing products, orders, users, and a feature-rich loyalty and referral program.✨ Key FeaturesDual B2C & B2B Portals: Separate storefronts and dashboards for retail customers and professional clients, each with a unique feature set.Comprehensive Admin Panel: A secure administrative interface for managing the entire platform, including:Product & Inventory ManagementOrder & Invoice ProcessingUser and Role Management (Admin, Staff, B2B, B2C)Content Management for the BlogAdvanced Loyalty & Referral Program:Tiered Loyalty System: Customers earn points and unlock tiers with escalating benefits based on their spending.Points Redemption: Users can convert points into vouchers or redeem them for exclusive products and experiences.Referral System: Tiered rewards for successful referrals, encouraging evangelism.Social Sharing: Integrated sharing options (Email, WhatsApp, Instagram) for referral links.Secure Authentication: Robust authentication system featuring JWT, MFA (Two-Factor Authentication), and secure password handling.Internationalization (i18n): Frontend is fully configured for English and French, with a language switcher in the header.Client-Side Validation: Forms are protected with VeeValidate and yup to ensure data integrity and provide a better user experience.🚀 Tech StackBackendFramework: FlaskDatabase: PostgreSQLORM: SQLAlchemyAuthentication: Flask-JWT-ExtendedBackground Tasks: Celery with RedisAPI: RESTful principles with Flask BlueprintsFrontendFramework: Vue.js 3 (Composition API)State Management: PiniaStyling: Tailwind CSSValidation: VeeValidate & YupBundler: ViteInternationalization: vue-i18nTestingEnd-to-End: Playwright🛠️ Getting StartedFollow these instructions to set up the project for local development.PrerequisitesPython 3.9+Node.js 16+ and npmPostgreSQL serverRedis server (for Celery)1. Backend SetupClone the repository and navigate to the project root.# 1. Create and activate a Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install Python dependencies
pip install -r backend/requirements.txt

# 3. Set up the database
#    - Create a PostgreSQL database (e.g., 'maisontruvra_db')
#    - Create a database user with privileges for the new database

# 4. Configure Environment Variables
#    - Copy the example environment file
cp .env.example .env

#    - Edit the .env file with your database URL, secret keys, etc.
#      DATABASE_URL="postgresql://user:password@localhost/maisontruvra_db"
#      SECRET_KEY="..."
#      JWT_SECRET_KEY="..."
#      ...and other required variables

# 5. Apply Database Migrations & Seed Data
#    - Ensure your database URL in .env is correct
#    - Run the database schema update script (you may need to adapt this to your migration tool)
psql -U your_user -d maisontruvra_db -a -f backend/database_schema_updates.sql

#    - Seed the database with initial data (e.g., admin user, loyalty tiers)
flask db seed
2. Frontend SetupNavigate to the website directory in a new terminal window.# 1. Go to the frontend directory
cd website

# 2. Install Node.js dependencies
npm install

# 3. Install validation libraries
npm install vee-validate@latest yup@latest
▶️ Running the ApplicationYou will need to run the backend, frontend, and Celery worker in separate terminal windows.Terminal 1: Run the Flask Backend# (From the project root, with venv activated)
flask run
The Flask server will start, typically on http://127.0.0.1:5000.Terminal 2: Run the Vite Frontend Dev Server# (From the website/ directory)
npm run dev
The Vite server will start, typically on http://127.0.0.1:5173. Your browser will open to this address, and it will proxy API requests to the Flask backend.Terminal 3: Run the Celery Worker (Optional)# (From the project root, with venv activated)
celery -A backend.celery_worker.celery worker --loglevel=info
This is required for processing background tasks like sending emails.You can now access the application:B2C Site: http://localhost:5173Admin Panel: http://localhost:5173/admin📂 Project Structure.
├── backend/            # Flask application source code
│   ├── admin_api/      # API routes for the admin panel
│   ├── b2b/            # API routes for the B2B portal
│   ├── models/         # SQLAlchemy database models
│   ├── services/       # Business logic and services
│   ├── templates/      # Email templates
│   └── ...
├── website/            # Frontend source code (Vue.js, Vite)
│   ├── js/             # JavaScript and Vue source files
│   │   ├── admin/      # Admin panel components and views
│   │   ├── stores/     # Pinia stores
│   │   └── vue/        # B2C/B2B components and views
│   └── ...
├── tests/              # E2E tests with Playwright
├── .env                # Local environment variables (DO NOT COMMIT)
└── README.md           # This file
🔒 SecurityAuthentication: User sessions are managed using JSON Web Tokens (JWTs).Authorization: API endpoints are protected using role-based (@admin_required, @b2b_user_required) and permission-based decorators.CSRF Protection: Implemented on session-based routes to prevent cross-site request forgery.Input Validation: Client-side validation is enforced using VeeValidate, with corresponding server-side validation and sanitization.Multi-Factor Authentication (MFA): Available for all user roles to enhance account security.
