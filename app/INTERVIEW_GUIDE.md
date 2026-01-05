# Interview Guide - Healthcare Django Project

This document is for **interviewers only**. It lists all intentional problems in the codebase and expected discussion points.

## How to Run

```bash
docker compose up --build -d
# Wait a few seconds for database to start, then:
docker compose exec web python3 manage.py makemigrations healthcare
docker compose exec web python3 manage.py migrate
docker compose exec web python3 manage.py loaddata fixtures/sample_data.json
```

Access at: http://localhost:8000

To stop: `docker compose down`

---

## Problem 1: Bad Data Modeling

**File:** `healthcare/models.py`

### Issues:
- `Patient.facility_name` is a CharField instead of ForeignKey to Facility
- `Patient.doctor_name` is a CharField instead of ForeignKey to User
- `Patient.age` is stored directly instead of computing from birth_date
- `Patient.diagnoses` stores comma-separated values instead of proper M2M relationship
- `PatientNote.patient_name` is CharField instead of ForeignKey to Patient
- `PatientNote.facility_name` duplicates data that could be derived from patient
- `PatientNote.created_by` is CharField instead of ForeignKey to User

### Expected Discussion:
- Data integrity issues (facility name can change, data gets out of sync)
- Cannot enforce referential integrity
- Cannot use Django ORM relationships (no `patient.notes.all()`)
- Age needs manual updates; birth_date is immutable
- Comma-separated fields can't be queried, filtered, or validated

### Better Approach:
```python
class Patient(models.Model):
    name = models.CharField(max_length=200)
    facility = models.ForeignKey(Facility, on_delete=models.PROTECT)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    birth_date = models.DateField()
    # diagnoses via M2M to Diagnosis model

class PatientNote(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # facility derived from patient.facility
```

---

## Problem 2: Version Problems

**File:** `requirements.txt`

### Issues:
- `django==3.2` - Old LTS version (EOL April 2024)
- `psycopg2-binary` - No version pinned
- `requests`, `pillow`, `numpy` - Unpinned AND unnecessary dependencies

### Expected Discussion:
- Security vulnerabilities in old Django versions
- Unpinned dependencies cause non-reproducible builds
- Unnecessary dependencies increase attack surface and image size
- Should use `pip freeze` or poetry/pipenv for lockfiles

---

## Problem 3: Non-Conventional Syntax (PEP8 Violations)

**File:** `healthcare/views.py` (patient and note views sections)

### Issues:
- Mixed naming: `camelCase` (`noteList`, `createNote`, `PatientID`, `thePatient`) vs `snake_case`
- No spaces around operators: `request.method=='POST'`
- No spaces after commas: `def noteDetail(request,note_id)`
- Inconsistent spacing in dictionaries: `{'patient':patient}`

### Expected Discussion:
- Python style guide (PEP8) recommends snake_case
- Consistent style improves readability
- Use linters (flake8, pylint) and formatters (black)

---

## Problem 4: Long Unnecessary Comments

**File:** `healthcare/views.py` (note views section)

### Issues:
- 3-line comments explaining simple functions
- Comments describe "what" the code does instead of "why"
- Comments will get out of sync with code

### Expected Discussion:
- Good code is self-documenting
- Comments should explain "why", not "what"
- Docstrings for public APIs
- Delete comments that restate the obvious

---

## Problem 5: Long Function with Deep Nesting

**File:** `healthcare/views.py` - `create_patient()` function

### Issues:
- 5 levels of nesting with if statements
- Multiple validations nested inside each other
- Logic is hard to follow due to nesting depth

### Expected Discussion:
- Use early returns / guard clauses
- Extract validation into separate functions
- Use Django forms for validation
- Consider decorators for auth checks

### Better Approach:
```python
def create_patient(request, facility_id):
    if request.method != 'POST':
        return render(request, 'patients/create.html', {'facility_id': facility_id})

    if not request.user.is_authenticated:
        return HttpResponse('You must be logged in')

    facility = get_object_or_404(Facility, id=facility_id)

    if request.user not in facility.doctors.all():
        return HttpResponse('You do not have access')

    form = PatientForm(request.POST)
    if not form.is_valid():
        return render(request, 'patients/create.html', {'form': form, 'errors': form.errors})

    patient = form.save(commit=False)
    patient.facility = facility
    patient.doctor = request.user
    patient.save()
    return redirect('patient_detail', patient_id=patient.id)
```

---

## Problem 6: Redundant Code

**File:** `healthcare/views.py` (facility views section)

### Issues:
- `Facility.objects.all()` called 4 times in `facility_list()`
- `Facility.objects.get(id=facility_id)` called 6 times in `facility_detail()`
- Same query in loop instead of prefetching
- Both `patients` and `patient_list` contain same data

### Expected Discussion:
- Query once, reuse the result
- Use `select_related()` and `prefetch_related()` for N+1 queries
- DRY principle (Don't Repeat Yourself)

---

## Problem 7: SQL Injection Vulnerability

**File:** `healthcare/views.py` - `search_patients()` and `patient_export()` functions

### Issues:
```python
query = f"SELECT * FROM patients_patient WHERE name LIKE '%{name}%'"
patients = Patient.objects.raw(query)
```
- User input directly interpolated into SQL query
- Attacker can inject: `'; DROP TABLE patients_patient; --`

### Expected Discussion:
- NEVER use string formatting for SQL
- Use Django ORM: `Patient.objects.filter(name__icontains=name)`
- If raw SQL needed, use parameterized queries:
  ```python
  Patient.objects.raw("SELECT * FROM patients_patient WHERE name LIKE %s", [f'%{name}%'])
  ```

---

## Problem 8: Bloated Dockerfile

**File:** `Dockerfile`

### Issues:
- `FROM ubuntu:latest` - Heavy base image (~70MB vs ~50MB for python:slim)
- `latest` tag is not reproducible
- Unnecessary packages: vim, curl, wget, git, htop, net-tools, iputils-ping
- `COPY . /app` copies everything (.git, __pycache__, etc.)
- No `.dockerignore` file
- Running as root (no USER directive)
- No multi-stage build
- **Apt cache cleaned in separate layer**: Line 15 deletes `/var/lib/apt/lists/*` but apt-get ran in line 3-13, so cache is already in that layer and doesn't get removed from final image size

### Expected Discussion:
- Use `python:3.11-slim` or `python:3.11-alpine`
- Pin image versions
- Only install production dependencies
- Add `.dockerignore` for .git, __pycache__, *.pyc, etc.
- Create non-root user for security
- Multi-stage builds for smaller images
- **Clean up caches in the same RUN command**: Combine cleanup with install to avoid storing cache in layers
  ```dockerfile
  # Bad: cache stored in layer from line 3, deletion in line 15 doesn't help
  RUN apt-get update && apt-get install -y packages
  RUN rm -rf /var/lib/apt/lists/*

  # Good: cleanup in same layer
  RUN apt-get update && apt-get install -y packages \
      && rm -rf /var/lib/apt/lists/*
  ```

### Better Approach:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install packages and clean cache in same layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000
CMD ["gunicorn", "healthcare.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## Problem 9: Unreadable Algorithm with Poor Naming

**File:** `healthcare/views.py` - `calculate_patient_report()` function

### Issues:
- Single-letter variable names: `a`, `b`, `c`, `d`, `e`, `f`, `p`, `r`, `s`, `t`, `x`, `y`, `z`
- Generic names: `tmp`, `tmp2`, `n`, `i`, `j`
- One monolithic function doing 5 different things
- Comments marking sections that should be separate functions:
  - SECTION 1: Calculate age statistics
  - SECTION 2: Process diagnosis data
  - SECTION 3: Calculate risk scores
  - SECTION 4: Sort and format results
  - SECTION 5: Generate summary
- Manual bubble sort instead of using built-in functions
- Nested loops and conditional logic
- Multiple iterations over the same data
- Hard to understand what the function does without reading all the code

### Expected Discussion:
- Meaningful variable names: `patients`, `total_age`, `max_age`, `min_age`, `diagnosis_counts`
- Extract each section into its own function:
  - `calculate_age_statistics(patients)`
  - `count_diagnoses(patients)`
  - `calculate_risk_scores(patients)`
  - `sort_by_risk_score(patients)`
  - `generate_summary_report(stats)`
- Use Python built-ins: `max()`, `min()`, `sum()`, `sorted()`, `collections.Counter`
- Follow Single Responsibility Principle
- Make code self-documenting through good naming

### Better Approach:
```python
def calculate_patient_report(request, facility_id):
    facility = Facility.objects.get(id=facility_id)
    patients = Patient.objects.filter(facility_name=facility.name)

    age_stats = calculate_age_statistics(patients)
    diagnosis_counts = count_diagnoses(patients)
    risk_scores = calculate_risk_scores(patients)
    high_risk_patients = get_top_risk_patients(risk_scores, limit=3)

    return JsonResponse({
        'average_age': age_stats['average'],
        'max_age': age_stats['max'],
        'min_age': age_stats['min'],
        'diagnoses': diagnosis_counts,
        'high_risk': high_risk_patients,
        'total_patients': len(patients)
    })
```

---

## Problem 10: Secrets in Docker Layers

**Files:** `Dockerfile`, `.secrets`

### Issues:
- `.secrets` file contains sensitive credentials (AWS keys, API tokens, passwords)
- File is `COPY`'d into the image at line 17: `COPY .secrets /app/.secrets`
- File is displayed with `RUN cat /app/.secrets` at line 19 (secrets printed to build logs!)
- File is deleted in a later layer at line 25: `RUN rm -f /app/.secrets`
- **Critical mistake**: Deleting files in later Docker layers doesn't remove them from earlier layers
- Secrets remain accessible in the image using `docker history` or by extracting layers
- Anyone with access to the image can retrieve the secrets

### Expected Discussion:
- Docker layers are immutable - deleting in a later layer doesn't remove from earlier layers
- Secrets should NEVER be copied into Docker images
- Build logs may expose secrets if printed
- Use BuildKit secrets or multi-stage builds
- Use environment variables passed at runtime
- Use secrets management systems (Vault, AWS Secrets Manager, etc.)

### How to Extract Secrets from the Image:
```bash
# View image history
docker history interview-web --no-trunc

# Extract a specific layer
docker save interview-web -o image.tar
tar -xf image.tar
# Find the layer with .secrets and extract it

# Or use dive tool to inspect layers
dive interview-web
```

### Better Approaches:

**Option 1: Runtime Environment Variables**
```dockerfile
# Don't copy secrets into image
# Pass at runtime instead
docker run -e AWS_ACCESS_KEY_ID=xxx -e AWS_SECRET_ACCESS_KEY=yyy myapp
```

**Option 2: Docker BuildKit Secrets**
```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Mount secret during build, never copied to image
RUN --mount=type=secret,id=secrets \
    cat /run/secrets/secrets > config.txt

# Build with:
# docker buildx build --secret id=secrets,src=.secrets .
```

**Option 3: Multi-stage Build (if secrets only needed during build)**
```dockerfile
FROM python:3.11 AS builder
RUN --mount=type=secret,id=pip_config \
    pip install -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Secrets never make it to final image
```

---

## Additional Discussion Points

### Missing from this project (good topics to ask about):
- No tests
- No `.gitignore`
- No environment variables for secrets
- No logging
- No API documentation
- No input validation (Django forms)
- DEBUG=True in production settings
- SECRET_KEY hardcoded
- ALLOWED_HOSTS = ['*']

### Architecture questions:
- How would you add authentication/authorization?
- How would you handle the patient search at scale?
- How would you implement audit logging for HIPAA compliance?
- How would you add an API (DRF)?

---

## Scoring Rubric (Example)

| Problem | Junior | Mid | Senior |
|---------|--------|-----|--------|
| Data Modeling | May not notice | Identifies FK issues | Discusses normalization, performance |
| SQL Injection | May not notice | Identifies risk | Explains exploitation, mitigation |
| Docker | May not notice | Identifies size issues | Discusses security, multi-stage |
| Code Quality | Notices style issues | Suggests fixes | Discusses tooling, CI/CD |
