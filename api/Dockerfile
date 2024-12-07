FROM python:3.9.6-slim-bullseye

WORKDIR /api

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["fastapi", "run", "main.py"]