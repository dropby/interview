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

## 10 Problems to Discuss

1. **Bad Data Modeling** - Strings instead of ForeignKeys
2. **Version Problems** - Old Django, unpinned dependencies
3. **PEP8 Violations** - Mixed naming conventions
4. **Long Comments** - Unnecessary explanations
5. **Deep Nesting** - Multiple nested if statements
6. **Redundant Code** - Same query repeated 6x
7. **SQL Injection** - Unsanitized user input
8. **Bloated Docker** - Unnecessary packages
9. **Unreadable Algorithm** - Single-letter variables, monolithic function
10. **Secrets in Docker Layers** - Credentials copied and "deleted" but still in layers

See `INTERVIEW_GUIDE.md` for full details.
