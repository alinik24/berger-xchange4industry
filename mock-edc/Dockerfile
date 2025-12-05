FROM python:3.9-slim

WORKDIR /app

RUN pip install fastapi uvicorn

COPY main.py .

EXPOSE 8080

CMD ["python", "main.py"]
