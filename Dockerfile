FROM python:3.11-slim

WORKDIR /app/src

COPY requirements/prod.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]
