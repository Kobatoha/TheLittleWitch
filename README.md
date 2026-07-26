# 🌙 The Little Witch

A browser-based sandbox game about growing magical plants, brewing potions, and becoming the best witch on the server.

## ✨ Features

- 🌱 **Garden** — plant seeds, water, clean, and bathe plants in moonlight. 6 growth stages from Seed to Maturity.
- 🧪 **Potion Brewing** — combine ingredients to craft potions with quality-based success chances.
- 🏪 **Shop** — sell harvested items and crafted potions for coins.
- 🌙 **Lunar Calendar** — real moon phases affect plant essence gain.
- 📊 **Progression** — gain experience by using potions, level up, unlock perks.
- 🎒 **Inventory** — items grouped by type with quality indicators.
- 📜 **Care History** — log of all actions performed on each plant.

## 🛠 Tech Stack

- **Backend:** Python 3.14, FastAPI, SQLAlchemy, Jinja2
- **Database:** SQLite
- **Testing:** 110+ tests (pytest), CI/CD via GitHub Actions
- **AI Art:** Stable Diffusion (Fooocus) for game illustrations

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Git

### Installation

```bash
git clone https://github.com/Kobatoha/TheLittleWitch.git
cd TheLittleWitch
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database Setup

```bash
alembic upgrade head
python seed.py
python seed_items.py
python seed_recipes.py
python create_test_data.py
```

### Run

```bash
uvicorn app.main:app --reload
```

### Open

```bash
http://127.0.0.1:8000/api/game/garden/page
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```
![Tests](https://github.com/Kobatoha/TheLittleWitch/actions/workflows/tests.yml/badge.svg)

## 📁 Project Structure

```text
TLW/
├── app/
│   ├── admin/              # SQLAdmin admin panel
│   ├── core/               # Config, database, exceptions, constants
│   ├── game/
│   │   ├── services/       # Business logic (garden, inventory, brewing, profile)
│   │   ├── router.py       # Garden & profile endpoints
│   │   ├── inventory_router.py
│   │   ├── shop_router.py
│   │   ├── brew_router.py
│   │   ├── formulas.py     # Pure calculation functions
│   │   ├── moon.py         # Lunar phase calculator
│   │   └── schemas.py      # Pydantic models
│   ├── models/             # SQLAlchemy models
│   └── templates/          # Jinja2 HTML templates
├── tests/
│   ├── unit/               # Unit tests
│   └── integration/        # API integration tests
├── alembic/                # Database migrations
└── .github/workflows/      # CI/CD
```

## 📄 License

This project is a personal portfolio piece. Feel free to explore the code and reuse ideas.
