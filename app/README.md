# Healthcare Interview Project

A Django project with intentional code problems for technical interviews. Candidates discuss problems without fixing them.

## Quick Start

```bash
docker compose up --build -d
sleep 5
docker compose exec web python3 manage.py makemigrations healthcare
docker compose exec web python3 manage.py migrate
docker compose exec web python3 manage.py loaddata fixtures/sample_data.json
```

Visit: http://localhost:8000

## Project Structure

```
interview/
├── Dockerfile               # Bloated Docker setup
├── docker-compose.yml       # Docker configuration
├── requirements.txt         # Version problems
├── manage.py
├── INTERVIEW_GUIDE.md      # Full problem list & solutions
├── healthcare/             # Main app (all code consolidated)
│   ├── settings.py         # Django settings
│   ├── urls.py             # All URL routes
│   ├── models.py           # All models (Facility, Patient, PatientNote)
│   ├── views.py            # All views (facilities, patients, notes)
│   ├── wsgi.py
│   └── migrations/         # Single migration
├── templates/              # Basic HTML templates
└── fixtures/               # Sample data
```

