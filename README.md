# TerraLumen Website

A professional Flask web application for TerraLumen.org - A Private Members Association dedicated to natural healing, advanced plasma technologies, and personal sovereignty.

## Features

- **Public Pages**: Home, About, Services, Membership, Contact, and Blog
- **Member System**: Registration, authentication, and member dashboard
- **Stripe Integration**: Payment processing for memberships (Annual, Lifetime, Supporter)
- **Blog System**: Article management with member-only content support
- **Admin Panel**: Protected admin interface for managing articles and members
- **Professional Design**: Responsive design with TerraLumen brand colors
- **PDF Membership Cards**: Automatic generation of digital membership cards

## Technology Stack

- **Backend**: Flask 3.0.0
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Flask-Login
- **Payments**: Stripe
- **PDF Generation**: ReportLab
- **Deployment**: Gunicorn (for Render)

## Setup Instructions

### Prerequisites

- Python 3.11+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd terralumen_website
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///instance/terralumen.db
   STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
   STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   ```

5. **Initialize the database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Create an admin user** (optional)
   
   You can create an admin user through the Flask shell:
   ```bash
   flask shell
   ```
   ```python
   from app import db
   from app.models import User, MembershipType, MembershipStatus
   admin = User(
       name='Admin User',
       email='admin@terralumen.org',
       membership_type=MembershipType.ANNUAL,
       membership_status=MembershipStatus.ACTIVE,
       is_admin=True
   )
   admin.set_password('your-admin-password')
   db.session.add(admin)
   db.session.commit()
   ```

7. **Run the application**
   ```bash
   python run.py
   ```
   
   The application will be available at `http://localhost:5000`

## Deployment on Render

### Steps

1. **Push your code to GitHub**

2. **Create a new Web Service on Render**
   - Connect your GitHub repository
   - Select the repository

3. **Configure the service**
   - **Name**: terralumen-website (or your preferred name)
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`

4. **Set environment variables in Render dashboard**
   - `SECRET_KEY`: Generate a secure random key
   - `DATABASE_URL`: Use Render's PostgreSQL database URL (or keep SQLite for development)
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret

5. **Configure Stripe Webhook**
   - In Stripe Dashboard, create a webhook endpoint pointing to: `https://your-app.onrender.com/stripe/webhook`
   - Copy the webhook signing secret to your environment variables

6. **Deploy**
   - Render will automatically deploy your application

## Project Structure

```
terralumen_website/
├── app/
│   ├── __init__.py              # Flask app initialization
│   ├── models.py                # Database models
│   ├── routes.py                # Public routes
│   ├── auth.py                  # Authentication routes
│   ├── admin.py                 # Admin panel routes
│   ├── stripe_handler.py        # Stripe payment handling
│   ├── config.py                 # Configuration
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── about.html
│   │   ├── services.html
│   │   ├── membership.html
│   │   ├── contact.html
│   │   ├── blog.html
│   │   ├── article.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── member_dashboard.html
│   │   ├── member_content.html
│   │   ├── admin/               # Admin templates
│   │   └── errors/              # Error pages
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── images/
│   └── utils/
│       ├── email_handler.py
│       └── membership_card.py
├── migrations/                  # Database migrations
├── instance/                    # Database files (gitignored)
├── requirements.txt
├── Procfile                     # Render deployment config
├── runtime.txt                 # Python version
├── .env.example                # Environment variables example
├── .gitignore
├── README.md
└── run.py                       # Application entry point
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key for sessions | Yes |
| `DATABASE_URL` | Database connection string | Yes |
| `STRIPE_SECRET_KEY` | Stripe API secret key | Yes |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | Yes |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | Yes |
| `MAIL_SERVER` | SMTP server for emails | No |
| `MAIL_PORT` | SMTP port | No |
| `MAIL_USE_TLS` | Use TLS for email | No |
| `MAIL_USERNAME` | Email username | No |
| `MAIL_PASSWORD` | Email password | No |
| `MAIL_DEFAULT_SENDER` | Default sender email | No |

## Features Overview

### Public Features
- Homepage with hero section and service overview
- About page with mission and founders information
- Services page detailing healing modalities
- Membership page with pricing options
- Contact form with validation
- Blog with pagination and article reading

### Member Features
- User registration and authentication
- Member dashboard with status and quick actions
- Exclusive member-only content access
- PDF membership card download
- Priority booking access

### Admin Features
- Protected admin dashboard
- Article management (create, edit, delete, publish)
- Member management and viewing
- Transaction history
- Statistics overview

### Payment Integration
- Stripe checkout for memberships
- Webhook handling for payment events
- Automatic membership status updates
- Support for subscriptions and one-time payments

## Security Features

- Password hashing with Werkzeug
- CSRF protection with Flask-WTF
- SQL injection prevention via SQLAlchemy ORM
- XSS protection via template escaping
- Secure session management
- Admin route protection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is proprietary and confidential.

## Support

For support, email contact@terralumen.org or visit the contact page on the website.

## Acknowledgments

- TerraLumen founders: Nicole Chiplin and Jonathan King
- Built with Flask and modern web technologies

