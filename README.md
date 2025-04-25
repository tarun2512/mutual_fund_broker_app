# Mutual Fund Brokerage Application

This repository contains a FastAPI-based microservice for managing mutual fund investments, complete with Celery-powered scheduled tasks and a responsive frontend.

---
## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Environment Configuration](#environment-configuration)
4. [Installation](#installation)
5. [Running the Application](#running-the-application)
6. [API Endpoints](#api-endpoints)
7. [Celery Setup](#celery-setup)
11. [Stopping Services](#stopping-services)

---
## Prerequisites

- **Python 3.9+**
- **Redis** (broker & backend for Celery)
- **MongoDB** (stores user portfolios and hourly snapshots)
- **HTML & JS** (for frontend dependencies, if any)
- **Git**

---
## Project Structure

```
├── scripts/             # (optional) core python code
│   └── services        # RESP API'ss
├── static                  # CSS files
├── templates/             # (optional) static HTML/CSS/JS files
│   └── auth        # Login and dashboard pages
├── celery_app.py         # Celery configuration
├── tasks.py              # Celery tasks definitions
├── beat_schedule.py      # Celery Beat schedule
├── main.py               # FastAPI application
├── app.py               # FastAPI routers
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---
## Environment Configuration

Create a `.env` file in the project root with:

```ini
# .env
BASE_PATH=/code/data
MOUNT_DIR=/assignment
MONGO_URI=mongodb://localhost:27017/your_db_name
REDIS_URI=redis://localhost:6379/0
RAPID_API_KEY=""
```

---
## Installation

1. **Clone the repo**
    ```bash
    git clone https://github.com/yourusername/mutual-fund-brokerage.git
    cd mutual-fund-brokerage
    ```

2. **Python virtual environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install Python dependencies**
    ```bash
    pip install -r requirements.txt
    ```

---
## Running the Application

### 1. Start Redis & MongoDB

Using Docker:
```bash
docker run -d --name redis -p 6379:6379 redis
docker run -d --name mongo -p 27017:27017 mongo
```

Or start services natively.

### 2. Run FastAPI
```bash
uvicorn main:app --reload
```
- URL: `http://localhost:5112/login`
- API docs: `http://localhost:8000/docs`

---
## API Endpoints

| Method | Path                                    | Description                        |
| ------ | --------------------------------------- | ---------------------------------- |
| POST   | `/funds/add_funds`                      | Add funds to user portfolio        |
| GET    | `/funds/fetch_funds?user_id={user_id}` | Retrieve current portfolio         |
| GET    | `/funds/fetch_hourly_portfolio_data?user_id={user_id}` | Hourly portfolio data       |
| POST   | `/auth/logout`                         | Logout user                        |

---
## Celery Setup

## Scheduling Hourly Tasks

1. **Start Celery Worker**
    ```bash
    celery -A celery_app worker --loglevel=info
    ```
2. **Start Celery Beat**
    ```bash
    celery -A celery_app beat --loglevel=info
    ```

---
## Stopping Services

- **FastAPI**: `Ctrl+C` in `uvicorn` terminal
- **Celery Worker**: `Ctrl+C` in worker terminal
- **Celery Beat**: `Ctrl+C` in beat terminal

---

### Notes:
1. **Images Section**: I added the "Sample Images in the Assets(`assets/`) " section.
Let me know if you need more assistance or additional information!
