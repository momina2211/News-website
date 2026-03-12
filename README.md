# 📰 NewsHub - AI-Powered News Website

[![Django](https://img.shields.io/badge/Django-5.1-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Ready-brightblue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A production-ready, AI-powered news platform built with **Django 5**, **HTMX**, **Tailwind CSS**, and **PostgreSQL**. Features advanced AI capabilities, personalized recommendations, and a complete content management system.

## 🎯 Features Overview

### 🤖 AI-Powered Features (15 Total)

| # | Feature | Status | Details |
|---|---------|--------|---------|
| 1 | AI Article Summarization | ✅ | Auto-generate summaries using OpenAI |
| 2 | AI Tag Recommendations | ✅ | Intelligent tag suggestions with confidence scores |
| 3 | AI Headline Generator | ✅ | Generate SEO-optimized headlines (3 variants) |
| 4 | Trending Algorithm | ✅ | Engagement-based trending with recency decay |
| 5 | Personalized Recommendations | ✅ | ML-based article recommendations per user |
| 6 | Real-Time Notifications | ✅ | Comment replies, approvals, follows |
| 7 | Advanced Search | ✅ | PostgreSQL full-text search with ranking |
| 8 | Analytics Dashboard | ✅ | View tracking, user interactions, insights |
| 9 | Newsletter System | ✅ | Weekly digest emails to subscribers |
| 10 | Reading Time Estimation | ✅ | Auto-calculated reading time |
| 11 | Performance Optimization | ✅ | Indexes, caching, query optimization |
| 12 | REST API Layer | ✅ | 12 API endpoints with DRF |
| 13 | Image Optimization | ✅ | Responsive image handling |
| 14 | Comprehensive Tests | ✅ | 62+ tests with coverage |
| 15 | Full Documentation | ✅ | Complete setup & API docs |

### 📰 Core Features

✅ **Content Management**
- Article workflow: Draft → Pending Review → Published
- Rich content editor with featured images
- SEO-friendly slugs and metadata
- Related articles discovery
- Reading time estimation

✅ **User System**
- Role-based access (Reader, Author, Editor, Admin)
- User profiles with avatars and bio
- Follow authors for notifications
- Social media links

✅ **Community**
- Comments with approval workflow
- Spam protection and rate limiting
- Comment notifications
- Like system with atomic counters

✅ **Organization**
- Categories with descriptions
- Tags with auto-suggestions
- Hierarchical browsing
- Search with autocomplete

✅ **Frontend Excellence**
- Responsive Tailwind CSS design
- Dark/light mode toggle
- HTMX for real-time interactions
- Mobile-first approach
- Reading progress indicator
- Social share buttons

✅ **SEO & Performance**
- Meta tags and Open Graph
- XML sitemap and robots.txt
- Database query optimization
- Full-text search indexing
- Caching ready

---

## 🚀 Quick Start (5 minutes)

### Prerequisites
- **Python 3.11+**
- **Git**
- **PostgreSQL** (optional, SQLite for dev)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourrepo/newshub.git
cd newshub

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env for your settings

# 5. Setup database
python manage.py migrate

# 6. Seed example data (optional)
python manage.py seed_data

# 7. Run development server
python manage.py runserver
```

Visit **http://localhost:8000**

### 🔑 Test Credentials

```
Admin:   admin / admin123
Editor:  editor / editor123
Author:  author / author123
```

---

## 📊 Project Structure

```
newshub/
├── config/                    # Django settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                      # Django applications
│   ├── accounts/              # User auth & profiles
│   ├── articles/              # Article CRUD & workflow
│   ├── comments/              # Comments system
│   ├── categories/            # Article categories
│   ├── tags/                  # Article tags
│   ├── ai/                    # AI services (NEW)
│   ├── analytics/             # Trending & recommendations (NEW)
│   ├── notifications/         # User notifications (NEW)
│   ├── newsletter/            # Newsletter system (NEW)
│   └── search/                # Advanced search (NEW)
│
├── templates/                 # HTML templates (Tailwind + HTMX)
│   ├── base.html
│   ├── home.html
│   ├── articles/
│   ├── accounts/
│   ├── partials/              # Reusable components
│   └── newsletter/
│
├── static/                    # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                     # User uploads
│
├── tests/                     # Test suite (62+ tests)
│
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```env
# Core
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
SITE_NAME=NewsHub
SITE_URL=http://localhost:8000

# Database (leave blank for SQLite)
DATABASE_URL=

# AI Services (Optional)
OPENAI_API_KEY=sk_test_...
OPENAI_MODEL=gpt-3.5-turbo

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cache (Optional)
CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
```

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb newshub

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/newshub

# Run migrations
python manage.py migrate
```

---

## 🤖 AI Features Guide

### 1. AI Article Summarization

Auto-generate article summaries when published:

```bash
# Set environment variable
export OPENAI_API_KEY=sk_test_...

# Summarization happens automatically on publish
# Or manually in admin: Actions → Generate AI Summary
```

### 2. AI Tag Recommendations

Get intelligent tag suggestions:

```python
from apps.ai.tag_service import AITagRecommendationService

service = AITagRecommendationService()
tags = service.get_tag_recommendations(article, limit=10)
service.apply_recommendations(article)  # Create suggested tags
```

### 3. AI Headline Generator

Generate SEO-optimized headlines:

```python
from apps.ai.headline_service import AIHeadlineService

service = AIHeadlineService()
headlines = service.generate_headlines(article)
# Returns: full headline, short headline, social headline
```

### 4. Trending Algorithm

Auto-calculate trending scores daily:

```bash
# Manual calculation
python manage.py recalculate_trending

# Schedule with cron:
# 0 2 * * * python manage.py recalculate_trending
```

Formula: `(views × 0.5) + (likes × 2) + (comments × 1.5) - recency_decay`

### 5. Personalized Recommendations

Get recommendations based on user history:

```python
from apps.analytics.recommendation_service import RecommendationService

# Get personalized recommendations
recommendations = RecommendationService.get_recommendations(user, limit=10)

# Track user interactions
RecommendationService.track_interaction(user, article, "view")
RecommendationService.track_interaction(user, article, "like")
```

### 6. Notifications

Automatically notify users:

- ✅ Article approved/rejected
- ✅ Comment replies
- ✅ New article from followed author
- ✅ Article liked

### 7. Advanced Search

Full-text search with ranking:

```bash
# Search articles via API
curl http://localhost:8000/api/search/search/?q=django

# Autocomplete suggestions
curl http://localhost:8000/api/search/autocomplete/?q=pyt
```

### 8. Newsletter

Subscribe users and send digests:

```bash
# Send newsletter digest
python manage.py send_newsletter_digest

# Schedule with cron:
# 0 9 * * 0 python manage.py send_newsletter_digest
```

---

## 🌐 REST API

Base URL: `/api/`

### Recommendations

```http
GET /api/recommendations/recommended_for_me/?limit=10
GET /api/recommendations/similar/?article=slug&limit=5
```

### Search

```http
GET /api/search/search/?q=django&limit=20
GET /api/search/autocomplete/?q=pyt&limit=10
```

### Notifications

```http
GET /api/notifications/list_notifications/?limit=10
POST /api/notifications/mark_as_read/
GET /api/notifications/unread_count/
```

### Authentication

- **Recommendations**: `IsAuthenticated`
- **Search**: `AllowAny`
- **Notifications**: `IsAuthenticated`

---

## 🧪 Testing

Run the full test suite:

```bash
# All tests
python manage.py test tests --verbosity=2

# Specific tests
python manage.py test tests.test_ai_services
python manage.py test tests.test_analytics
python manage.py test tests.test_search

# With coverage
pip install coverage
coverage run --source='.' manage.py test tests
coverage report
```

**Test Coverage**: 62+ tests covering models, views, services, and workflows.

---

## 📦 Technologies

### Backend
- **Django 5.1** - Web framework
- **Django REST Framework** - REST API
- **PostgreSQL** - Database (SQLite for dev)
- **Celery** - Task queue (ready for integration)

### Frontend
- **Tailwind CSS** - Styling
- **HTMX** - Real-time interactions
- **Vanilla JavaScript** - No heavy dependencies
- **Alpine.js** - Reactive components

### AI & ML
- **OpenAI** - AI services (summarization, headlines, tags)
- **PostgreSQL FTS** - Full-text search
- **Django ORM** - Database queries

### DevOps
- **Docker** - Containerization ready
- **Gunicorn** - Production WSGI server
- **Redis** - Caching (optional)

---

## 🚀 Deployment

### Pre-Deployment Checklist

```bash
# Generate secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Run security checks
python manage.py check --deploy

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Run tests
python manage.py test tests
```

### Production Settings

Update `.env`:

```env
DEBUG=False
SECRET_KEY=your-generated-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@db-host:5432/newshub
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Docker Deployment

```bash
docker build -t newshub .
docker run -p 8000:8000 newshub
```

### Platforms

Ready for deployment on:
- ✅ Heroku
- ✅ DigitalOcean
- ✅ AWS
- ✅ Google Cloud
- ✅ Azure
- ✅ Railway
- ✅ Render

---

## 📚 Documentation

- **[AI Features Guide](AI_FEATURES_DOCUMENTATION.md)** - Complete AI feature documentation
- **[Implementation Summary](AI_IMPLEMENTATION_SUMMARY.txt)** - Architecture and statistics
- **[Integration Guide](QUICK_INTEGRATION_GUIDE.py)** - Code examples and integration points
- **[Cleanup Report](CLEANUP_VERIFICATION.txt)** - Project optimization status

---

## 🎯 Use Cases

### Content Creator
- Write articles and submit for review
- Get AI headline suggestions
- Track article performance
- Receive notifications on reader interactions

### Editor
- Review and approve articles
- Generate AI summaries and tags
- Monitor trending content
- Manage categories and tags

### Reader
- Browse articles by category/tag
- Get personalized recommendations
- Search with full-text search
- Subscribe to newsletter
- Like and comment on articles

### Admin
- Manage all content and users
- View analytics dashboard
- Configure AI services
- Manage notifications and settings

---

## 🔒 Security

- ✅ CSRF protection on all forms
- ✅ SQL injection prevention (ORM)
- ✅ XSS protection (template escaping)
- ✅ Password hashing (PBKDF2)
- ✅ Rate limiting on comments
- ✅ Spam detection
- ✅ Role-based access control
- ✅ Secure headers ready

---

## 📈 Performance

- ✅ Database indexes on critical fields
- ✅ Query optimization (select_related, prefetch_related)
- ✅ Full-text search indexing
- ✅ Caching framework ready
- ✅ Atomic counter operations
- ✅ Pagination on all lists

**Stats:**
- 15 models with optimized indexes
- 8 service layers
- 12 REST API endpoints
- 62+ comprehensive tests
- Zero unused code

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/yourrepo/newshub/issues)
- Check [Documentation](AI_FEATURES_DOCUMENTATION.md)
- Review [Test Cases](tests/) for usage examples

---

## 🎉 Acknowledgments

Built with ❤️ using Django, HTMX, and Tailwind CSS.

Inspired by modern news platforms and AI-powered personalization.

---

**Happy Blogging! 📰✨**

Last Updated: March 12, 2026
Version: 1.0.0

