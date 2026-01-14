FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY flatex_scraper.py /app/flatex_scraper.py

# Default: headless. JSON optional nach /out/flatex.json
ENV HEADLESS=true
ENV OUTPUT_JSON_PATH=/out/flatex.json

CMD ["python", "/app/flatex_scraper.py"]
