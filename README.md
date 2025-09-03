# Inventory Management System

A full-featured inventory platform with desktop (Tkinter) and web (Flask) interfaces backed by SQLite.

## Features
- Product/catalog CRUD with categories and suppliers
- Real-time stock tracking with alerts (low/critical/out-of-stock)
- Sales processing with automatic stock deductions and audit trail
- Dashboard and reports (inventory value, sales trends, top products)
- Web interface with login (demo: admin/admin)

## Quick Start
1. Create and activate a virtual environment
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```
2. Install dependencies (for the web app)
   ```bash
   pip install -r requirements.txt
   ```
3. Run the launcher
   ```bash
   python run_app.py
   ```
4. Choose one:
   - Desktop (Tkinter) — no extra packages needed
   - Web (Flask) — open http://127.0.0.1:5000 (login: admin/admin)

## Notes
- Database `inventory.db` is created and seeded automatically on first run
- Templates are in `templates/`

## Tech
- Python, Tkinter, Flask, SQLite, Jinja2

## License
MIT