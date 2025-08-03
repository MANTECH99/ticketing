FROM python:3.12

WORKDIR /app

# Installer les dépendances système nécessaires à mysqlclient et WeasyPrint
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    libffi-dev \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    zlib1g-dev \
    libglib2.0-0 \
    libgobject-2.0-0 \
    curl \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer l’environnement virtuel et installer les dépendances Python
COPY requirements.txt .
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Copier le reste du code
COPY . .

# Collecte des fichiers statiques et migrations
RUN . /opt/venv/bin/activate && python manage.py collectstatic --noinput && python manage.py migrate

# Commande de démarrage

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ticketing.wsgi:application"]
