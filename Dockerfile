FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# neu: kompletten src-Ordner kopieren
COPY src/ /app/src/

# optional: Output-Verzeichnis
RUN mkdir -p /out

# Wichtig: als Modul starten
CMD ["python", "-m", "src.flatex_scraper"]
