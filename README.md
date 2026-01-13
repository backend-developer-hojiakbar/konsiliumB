# Konsilium Medical AI Platform - Backend

Django REST Framework backend for the Konsilium Medical AI Consultation Platform.

## Features

- **User Authentication**: JWT-based authentication with phone number
- **Analysis Management**: Store and manage patient analyses
- **AI Integration**: Gemini AI for medical consultation and diagnosis
- **Case Library**: Anonymized case sharing and learning
- **CME Topics**: Personalized continuing medical education recommendations
- **API Documentation**: Auto-generated Swagger/ReDoc documentation

## Technology Stack

- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL
- **AI**: Google Gemini AI
- **Authentication**: JWT (Simple JWT)
- **Documentation**: drf-yasg (Swagger/OpenAPI)

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 13+
- pip or uv package manager

### Setup Steps

1. **Create and activate virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Setup PostgreSQL database**:
```bash
# Create database
createdb konsilium_db

# Or using psql
psql -U postgres
CREATE DATABASE konsilium_db;
\q
```

5. **Run migrations**:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**:
```bash
python manage.py createsuperuser
```

7. **Run development server**:
```bash
python manage.py runserver
```

The API will be available at `https://konsiliumapi.aiproduct.uz`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile
- `POST /api/auth/password/change/` - Change password

### Analyses
- `GET /api/analyses/` - List user's analyses
- `POST /api/analyses/` - Create new analysis
- `GET /api/analyses/{id}/` - Get analysis details
- `PUT /api/analyses/{id}/` - Update analysis
- `DELETE /api/analyses/{id}/` - Delete analysis
- `POST /api/analyses/{id}/complete/` - Mark analysis as completed
- `GET /api/analyses/{id}/longitudinal/` - Get patient's history
- `GET /api/analyses/recent/` - Get recent analyses
- `GET /api/analyses/dashboard-stats/` - Get dashboard statistics

### Case Library
- `GET /api/analyses/case-library/` - List cases
- `POST /api/analyses/case-library/` - Add case to library
- `GET /api/analyses/case-library/{id}/` - Get case details
- `POST /api/analyses/case-library/{id}/view/` - Increment view count
- `GET /api/analyses/case-library/search/?q=query` - Search cases

### CME Topics
- `GET /api/analyses/cme-topics/` - List CME topics
- `POST /api/analyses/cme-topics/` - Create CME topic
- `POST /api/analyses/cme-topics/{id}/complete/` - Mark as completed

### AI Services
- `POST /api/ai/clarifying-questions/` - Generate clarifying questions
- `POST /api/ai/recommend-specialists/` - Recommend specialists
- `POST /api/ai/initial-diagnoses/` - Generate differential diagnoses
- `POST /api/ai/final-report/` - Generate final medical report
- `POST /api/ai/drug-interactions/` - Check drug interactions
- `POST /api/ai/cme-topics/` - Suggest CME topics

## API Documentation

Interactive API documentation is available at:

- **Swagger UI**: https://konsiliumapi.aiproduct.uz/swagger/
- **ReDoc**: https://konsiliumapi.aiproduct.uz/redoc/

## Environment Variables

Required environment variables (see `.env.example`):

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=konsilium_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

GEMINI_API_KEY=your-gemini-api-key

JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# SQLite for quick local dev (optional)
USE_SQLITE=False

# CSRF
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://konsilium.aiproduct.uz,http://konsilium.aiproduct.uz,https://konsiliumapi.aiproduct.uz,http://konsiliumapi.aiproduct.uz
```

## Database Schema

### Users
- Custom user model with phone-based authentication
- Tracks total analyses count

### Analyses
- Stores complete patient analysis records
- Includes patient data, debate history, final report
- Supports longitudinal patient tracking

### CaseLibrary
- Anonymized cases for educational purposes
- Searchable by tags and diagnosis

### CMETopics
- Personalized learning recommendations
- Based on user's case history

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
```bash
# Install development dependencies
pip install black flake8 isort

# Format code
black .
isort .

# Check code style
flake8 .
```

### Making Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Environment Setup

1. Set `DEBUG=False` in `.env`
2. Configure proper `SECRET_KEY` and `JWT_SECRET_KEY`
3. Set `ALLOWED_HOSTS` to your domain
4. Use PostgreSQL in production
5. Configure static files serving
6. Set up SSL/HTTPS

### Static Files

```bash
python manage.py collectstatic --noinput
```

## Security Notes

- Change all secret keys in production
- Use strong passwords
- Enable HTTPS
- Keep dependencies updated
- Implement rate limiting
- Use environment variables for sensitive data

## Support

For issues and questions:
- Email: support@cdcgroup.com
- Phone: +998 94 743 09 12

## License

© 2024 CDCgroup. All rights reserved.
Developed by CraDev Company
