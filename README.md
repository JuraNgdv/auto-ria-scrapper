# AutoRia Scraper

AutoRia Scraper is a powerful and configurable web scraping tool for extracting car listings from [auto.ria.com](https://auto.ria.com/uk/car/used/). It supports both PostgreSQL and SQLite databases, Dockerized deployment, logging, and periodic scraping with optional proxy support.

---

## 🚀 Getting Started

Follow the steps below to get the project up and running locally or on your server.

### 1. Clone the Repository

```bash
git clone https://github.com/JuraNgdv/auto-ria-scrapper.git
cd auto-ria-scrapper
```
### Configure Environment Variables
Copy the example environment file and modify it according to your setup:
```bash
cp .env.dist .env
```
Then edit .env and set your desired configuration:
```env
# Use SQLite instead of PostgreSQL (set to True or False)
DEV_MODE=False

# Enable detailed logs
DEBUG=True

# PostgreSQL settings (used if DEV_MODE=False)
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
DB_HOST=database
DB_PORT=5432

# SQLite file (used if DEV_MODE=True)
SQLITE_PATH=dev_database.db

# Start page for scraping
START_URL=https://auto.ria.com/uk/car/used/

# Daily dump time (HH:MM)
DUMP_TIME=12:00

# Delay before restarting the scraper (in minutes)
SCRAPE_REPEAT_AFTER_MINUTES=30

# Optional: List of proxies
# PROXIES=http://user:password@proxy.example.com:8080
```

## 🐳 Running with Docker
Make sure you have Docker and Docker Compose installed.

### 1. Build and Start Services
```bash
docker compose up -d --build
```
### 2. Run Database Migrations
```bash
docker compose exec app alembic revision --autogenerate -m "Initial message"
docker compose exec app alembic upgrade head
```

## 🧾 Logs
To view the live logs of the scraper:

```bash
docker compose logs -f app
```
Press Ctrl + C to detach from logs.

___

## 🧠 How It Works
The AutoRia scraper is designed with modularity, scalability, and fault-tolerance in mind.

### ✅ Main Flow
 - Entry Point: src/main.py
   - Initializes the database (depending on DEV_MODE)
   - Starts a periodic dump task at DUMP_TIME
   - Launches the scraping task with a restart delay

### 🧠 Core Components
 - AutoRiaScraper (src/scraper.py):
   - Orchestrates the scraping process using concurrent workers.
   - Scrapes multiple pages in parallel using different proxies.
   - Each worker fetches a page, parses car URLs, and scrapes car details.
   - Data is saved to the DB using SQLAlchemy (SQLite or PostgreSQL).

 - AutoRiaParser (src/parsers/parser.py):
     - Handles HTML parsing using BeautifulSoup.
     - Parses:
         - Links to individual car listings
         - Car details like title, VIN, odometer, price, contact info, etc.
      - Has retry logic and error handling for robust scraping.
 - Field Parsers (src/parsers/fields/):
    - Each field (price, VIN, phone number, etc.) has a dedicated parser class.
    - Handles various page formats and fallback strategies.
 - Database Models (src/database/models.py):
    - Defines the Car SQLAlchemy model.
    - Supports upsert via PostgreSQL ON CONFLICT or SQLite OR REPLACE.
 - Scheduler (src/scheduler/):
    - delayed_repeat_task: Re-runs the scraper every X minutes.
    - daily_task: Triggers daily database dump at scheduled time.

### 🔒 Robust Features
 - Proxy rotation support.
 - Retries and error logging on failed HTTP requests.
 - Handles edge cases like deleted listings or temporary blocks (HTTP 429).
 - Displays parsing statistics (speed, page count, total parsed).

___

## 🛠️ Technologies Used
 - Python 3
 - SQLAlchemy + Alembic
 - BeautifulSoup
 - Requests
 - Docker & Docker Compose
 - PostgreSQL / SQLite