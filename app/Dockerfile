FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    vim \
    curl \
    wget \
    git \
    htop \
    net-tools \
    iputils-ping

RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY .secrets /app/.secrets

RUN cat /app/.secrets

COPY . /app

RUN pip3 install -r requirements.txt --break-system-packages

RUN rm -f /app/.secrets

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
