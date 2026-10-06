# 🌙 The Little Witch

**The Little Witch** is a browser-based sandbox game built with **FastAPI** and **SQLAlchemy**.

The project combines game mechanics with a structured backend: REST API endpoints, business logic separated into services, database models and migrations, server-rendered pages, automated tests and CI.

The game is built around a small magical garden where the player grows plants, collects resources, brews potions and develops their character.

## ✨ Features

* 🌱 **Garden**

  * Plant and care for magical plants
  * 6 growth stages from seed to maturity
  * Multi-stage harvesting
  * Plant quality and level mechanics

* 🎒 **Inventory**

  * Items grouped by type
  * Item quality and levels
  * Resources obtained from plant care and harvesting

* 🧪 **Potion Brewing**

  * Multiple recipes
  * Ingredient-based crafting
  * Quality-dependent brewing results

* 🏪 **Shop**

  * Sell harvested resources and crafted potions
  * In-game currency

* 📊 **Character Progression**

  * Experience and levels
  * Perks and level rewards
  * Character statistics

* 🌙 **Lunar Calendar**

  * Moon phases are calculated by the backend
  * Lunar phases affect plant mechanics

* 📜 **Care History**

  * Plant actions are recorded
  * History can be viewed for individual plants

* 🛠 **Admin panel**

  * SQLAdmin-based administration interface

## 🏗 Architecture

The backend follows a layered structure:

```text
HTTP request
    ↓
Router
    ↓
Dependencies / validation
    ↓
Service layer
    ↓
SQLAlchemy models
    ↓
PostgreSQL
```

Game-specific business logic is concentrated in services rather than being implemented directly inside route handlers.

The project also separates pure game calculations from database-dependent operations. For example, formulas and lunar phase calculations can be tested independently from the application layer.

## 🛠 Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy 2
* Pydantic
* Jinja2
* SQLAdmin

### Database

* PostgreSQL
* Alembic

### Testing

* pytest
* Unit tests
* Integration tests
* Coverage tracking

### CI

* GitHub Actions
* Automated test runs on pushes and pull requests

### Frontend

* Jinja2 templates
* HTML
* CSS
* JavaScript

### Development

* Git
* Environment-based configuration

## 🧪 Testing

The project currently contains **130+ tests** covering both isolated game logic and API-level behaviour.

```text
Unit tests          → game formulas, services, utilities
Integration tests   → API and database interaction
```

Current test coverage is approximately **88%**.

Run the test suite with:

```bash
pytest tests/ -v
```

## 📁 Project Structure

```text
TheLittleWitch/
├── app/
│   ├── admin/                  # SQLAdmin configuration
│   ├── core/                   # Configuration, database, constants, exceptions
│   ├── game/
│   │   ├── services/           # Game business logic
│   │   │   ├── garden/
│   │   │   ├── inventory/
│   │   │   ├── brewing/
│   │   │   └── profile/
│   │   ├── router.py           # Main game endpoints
│   │   ├── inventory_router.py
│   │   ├── shop_router.py
│   │   ├── brew_router.py
│   │   ├── formulas.py         # Pure game calculations
│   │   ├── moon.py             # Lunar phase calculations
│   │   └── schemas.py          # Pydantic schemas
│   ├── models/                 # SQLAlchemy models
│   ├── templates/              # Jinja2 templates
│   └── main.py                 # FastAPI application
│
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
│
├── alembic/                    # Database migrations
├── .github/workflows/          # GitHub Actions
├── requirements.txt
├── pyproject.toml
└── alembic.ini
```

## 🚀 Getting Started

### Requirements

* Python 3.11+
* PostgreSQL
* Git

### Installation

Clone the repository:

```bash
git clone https://github.com/Kobatoha/TheLittleWitch.git
cd TheLittleWitch
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Database

Configure the PostgreSQL connection through the `DATABASE_URL` environment variable.

For example:

```text
DATABASE_URL=postgresql://user:password@localhost:5432/tlw
```

Apply migrations:

```bash
alembic upgrade head
```

Populate the development database using the included seed scripts.

### Run

Start the development server:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://127.0.0.1:8000
```

## 🎨 About the Project

The project started as a game development experiment and gradually became a practical backend project.

The main goal is not only to implement game mechanics, but also to explore how to structure a growing FastAPI application:

* separating business logic from HTTP handlers
* working with relational data and SQLAlchemy
* managing schema changes with Alembic
* writing unit and integration tests
* maintaining test coverage
* automating checks with CI
* keeping game calculations independent from infrastructure

Game illustrations were created with generative image tools and are used as part of the game's visual layer.

## 📌 Current State

The project is actively developed as a personal backend portfolio project.

The codebase contains implemented gameplay mechanics, database migrations, API endpoints, a service layer, automated tests and CI.

Authentication and some gameplay mechanics are intentionally left for further development.

## 📄 License

This project is a personal portfolio project.

The code is available for study and experimentation.
