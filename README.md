# 🛡️ Audit Trail & Log Monitoring API

A production-ready Django REST API for comprehensive system audit logging and security monitoring.

## 🎯 Overview

Track user actions, monitor security events, and maintain compliance with automated logging and real-time alerts. Built for enterprise applications requiring audit trails and security monitoring.

## ✨ Key Features

- **Automatic Logging**: User logins, failed attempts, database changes
- **Security Alerts**: Email notifications for 5+ failed logins in 1 minute
- **Role-Based Access**: Admins see all logs, users see their own
- **CSV Export**: Download logs for compliance reporting
- **Real-time Statistics**: Monitor system activity and security events
- **Search & Filter**: Find logs by user, action, date, IP address

## 🛠️ Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL 15+
- **Cache/Queue**: Redis 7+ + Celery
- **Authentication**: JWT tokens
- **Deployment**: Docker + Docker Compose

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone repository
git clone <your-repo-url>
cd audit-trail-api

# Setup environment
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Run migrations and create admin user
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# API is ready at http://localhost:8000
```

### Manual Setup

```bash
# Clone and setup
git clone <your-repo-url>
cd audit-trail-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Edit .env with your database and email settings

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Start services (3 separate terminals)
redis-server
celery -A audit_trail worker --loglevel=info
python manage.py runserver
```

## 📚 API Usage

### 1. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "is_staff": true
  }
}
```

### 2. View Audit Logs

```bash
# Get all logs (paginated)
curl -X GET http://localhost:8000/api/logs/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Filter by action type
curl -X GET "http://localhost:8000/api/logs/?action=FAILED_LOGIN" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Search by IP address or username
curl -X GET "http://localhost:8000/api/logs/?search=192.168.1.1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 3. Export Logs (Admin Only)

```bash
curl -X GET http://localhost:8000/api/logs/export/ \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN" \
  -o audit_logs.csv
```

### 4. View Statistics (Admin Only)

```bash
curl -X GET http://localhost:8000/api/logs/statistics/ \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

## ⚙️ Configuration

### Key Environment Variables

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

# Database
DB_NAME=audit_trail_db
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=localhost

# Email (for security alerts)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Gmail Setup for Alerts

1. Enable 2-factor authentication on your Gmail account
2. Go to: Google Account → Security → App passwords
3. Generate an app password and use it in `EMAIL_HOST_PASSWORD`

## 🔐 Security Features

### Automatic Event Logging
- ✅ User login/logout
- ✅ Failed login attempts
- ✅ Database record changes (CREATE/UPDATE/DELETE)
- ✅ Data exports
- ✅ API access attempts

### Security Monitoring
- ✅ Real-time failed login detection
- ✅ Email alerts to administrators
- ✅ IP address tracking
- ✅ Session monitoring
- ✅ Rate limiting on API endpoints

### Access Control
- ✅ JWT token authentication
- ✅ Role-based permissions (admin vs regular user)
- ✅ User can only see their own logs
- ✅ Admin can see all logs and export data

## 📊 What Gets Logged

| Event | Logged Information |
|-------|-------------------|
| **Login** | User, IP address, timestamp, session ID |
| **Failed Login** | Attempted username, IP, timestamp, user agent |
| **Logout** | User, IP address, session end time |
| **Data Changes** | User, action type, resource modified, timestamp |
| **Export** | User, exported data count, filters used |

## 🚨 Security Alerts

The system automatically sends email alerts when:
- 5 or more failed login attempts from same IP in 1 minute
- Critical security events occur
- Suspicious access patterns detected

Alert emails include:
- IP address of attacker
- Number of failed attempts
- Time window of attacks
- Recommended actions

## 🚢 Production Deployment

### Production Checklist
- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Set up SSL/HTTPS
- [ ] Configure email service (Gmail/SendGrid/etc.)
- [ ] Set up log rotation
- [ ] Configure monitoring

### Docker Production
```bash
# Build production image
docker build -t audit-trail-api:latest .

# Deploy with production settings
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing the System

### Test Failed Login Alerts
```bash
# Try multiple failed logins to trigger alert
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "password": "wrongpass"}'
done

# Check logs for alert
curl -X GET "http://localhost:8000/api/logs/?action=FAILED_LOGIN" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## 📁 Project Structure

```
audit_trail_project/
├── audit_trail/          # Django settings
├── logs/                 # Audit logging app
│   ├── models.py        # AuditLog model
│   ├── views.py         # API endpoints
│   ├── serializers.py   # JSON serialization
│   ├── signals.py       # Auto-logging events
│   ├── tasks.py         # Email alerts (Celery)
│   └── middleware.py    # Request logging
├── accounts/             # Authentication
├── requirements.txt      # Dependencies
├── docker-compose.yml    # Docker setup
└── .env                 # Environment config
```

## 💡 Why This Project Stands Out

1. **Real-World Application**: Solves actual business need for audit compliance
2. **Production-Ready**: Proper error handling, logging, and security
3. **Clean Architecture**: Follows Django best practices
4. **Security Focus**: Demonstrates understanding of security concerns
5. **Scalable Design**: Async processing with Celery, proper database indexing
6. **Documentation**: Clear setup and usage instructions
7. **DevOps Ready**: Docker support for easy deployment

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ using Django REST Framework**

For questions or support, please open an issue or contact [your-email@example.com]