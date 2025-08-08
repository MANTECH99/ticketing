FROM python:3.12

WORKDIR /app

# Installer les dépendances système nécessaires pour mysqlclient ET xhtml2pdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    fontconfig \
    default-libmysqlclient-dev \
    build-essential \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpango1.0-0 \
    libgdk-pixbuf2.0-0 \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements.txt et installer les dépendances Python
COPY requirements.txt .
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Copier le reste de l'application
COPY . .

# Commande pour lancer l'application avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "baol_distributions.wsgi:application"]
