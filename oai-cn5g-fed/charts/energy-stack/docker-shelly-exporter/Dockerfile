FROM python:3.12-slim

WORKDIR /app
COPY shelly-exporter.py /app/shelly-exporter.py

RUN pip install requests prometheus_client

EXPOSE 9100

CMD ["python", "shelly-exporter.py"]
