# 🍽️ Smart Canteen — Management System

> **TYCS Major Project** — a complete, production-style food-ordering platform for a college canteen.
> Students browse the menu, order online, receive a **daily digital token (A001, A002 …)** and track
> their order live — while an admin panel runs the kitchen: orders, inventory, students, reports.

---

## ✨ Features

### Student module
- Registration · login/logout · secure password hashing (Werkzeug PBKDF2) · profile & password management
- Browse menu with **search, category filter, price filter, sorting** (popular / price / name / newest) and pagination
- Food categories — Breakfast, Snacks, Main Course, Fast Food, Beverages, Desserts
- Food details with photo, description, prep time, **live stock display** & availability
- Today's menu · today's specials · popular food · recently-ordered ("order it again")
- **Cart**: add / update / remove / clear, quantity limits, **server-side price & stock validation**
- **Checkout**: student details, itemised summary, order notes, pickup info, server-side totals
- 13-step atomic checkout → **unique daily digital token** → order confirmation page
- **Live order tracking** (visual stepper): Order Placed → Confirmed → Preparing → Ready for Pickup → Completed
- Order history, order details, cancellation within the grace window (stock auto-restored)
- In-app **notifications** for every status change + unread badge with polling

### Admin module (role-protected)
- **Dashboard**: students/orders/revenue stats, order-status doughnut, 7-day revenue line,
  popular-food bar, recent orders, recent activity, low-stock alerts
- **Orders**: professional table (ID, token, student, items, total, time, status) with
  filtered/searched views and kitchen actions (Confirm / Prepare / Ready / Complete / Cancel)
  — **invalid status transitions are rejected by the state machine**
- **Food management**: full CRUD, image upload, price, description, category, prep time, stock,
  availability toggle, specials flag, soft delete
- **Categories**: create / edit / activate / deactivate
- **Students**: search, details, order stats, activate / deactivate accounts
- **Inventory**: stock levels, low-stock thresholds, status badges (In / Low / Out of stock),
  non-negative stock enforcement, auto-disable at zero & auto-enable on restock
- **Reports**: daily / weekly / monthly orders & revenue, popular items, category performance,
  completed/cancelled counts, **date filtering + CSV export** + JS charts
- **Notifications** (new orders, low stock) · **Settings** (canteen name, pickup info, cancel window)

### Security
| Concern | Implementation |
|---|---|
| Password storage | Salted PBKDF2 hashes — never plain text |
| Sessions | Signed, HTTP-only, SameSite=Lax cookies |
| CSRF | Flask-WTF tokens on **every** form + AJAX |
| XSS | Jinja2 autoescaping + CSP / X-Frame-Options / nosniff headers |
| SQL injection | 100% SQLAlchemy ORM (parameterised) |
| Authorization | Role decorators + admin blueprint guard → 403 page |
| Validation | WTForms (server-side) — client values never trusted |
| Secrets | `.env` only (`SECRET_KEY`); production refuses to boot without one |
| Stock integrity | Conditional `UPDATE … WHERE stock >= qty` + DB CHECK constraint |
| Money totals | Always recomputed from DB prices on the server |
| Auditability | `activity_logs` + `order_status_history` tables |

---

## 🏗️ Architecture — Three-Tier

```
┌────────────────────────────────────────────────────────────┐
│  Presentation   HTML5 + CSS3 + JavaScript + Jinja2          │
│                 app/templates · app/static                  │
├────────────────────────────────────────────────────────────┤
│  Application    Flask routes · services · forms · utils     │
│                 app/routes · app/services · app/forms       │
├────────────────────────────────────────────────────────────┤
│  Data           SQLAlchemy ORM → SQLite                     │
│                 app/models · instance/canteen.db            │
└────────────────────────────────────────────────────────────┘
   User → HTML/CSS/JS → Flask → SQLAlchemy → SQLite
```

Every important calculation (totals, stock, tokens, status transitions) happens **server-side**.

---

## 📁 Project structure

```text
smart_canteen/
│
├── app/
│   ├── __init__.py          # Application factory, security headers, error pages
│   ├── models/              # SQLAlchemy models (database layer)
│   │   ├── user.py          # users
│   │   ├── category.py      # categories
│   │   ├── food.py          # food_items
│   │   ├── cart.py          # cart, cart_items
│   │   ├── order.py         # orders, order_items, order_status_history
│   │   ├── token.py         # tokens (A001, A002 …)
│   │   ├── notification.py  # notifications
│   │   ├── activity.py      # activity_logs
│   │   └── setting.py       # settings
│   ├── routes/              # HTTP endpoints (application layer)
│   │   ├── auth.py          # register / login / logout / profile
│   │   ├── main.py          # home, dashboard, categories
│   │   ├── menu.py          # browse, search, filter, sort, details
│   │   ├── cart.py          # cart page + AJAX API (JSON & form)
│   │   ├── checkout.py      # checkout page + place order
│   │   ├── orders.py        # history, tracking, confirmation, cancel
│   │   ├── notifications.py # inbox + unread-count API
│   │   └── admin/           # secure admin blueprint
│   │       ├── dashboard.py # stats, charts, settings, notifications
│   │       ├── order_mgmt.py# kitchen workflow
│   │       ├── food_mgmt.py # food & category CRUD
│   │       ├── students.py  # student management
│   │       ├── inventory.py # stock management
│   │       └── reports.py   # analytics + CSV export
│   ├── services/            # business logic (transactional)
│   │   ├── order_service.py # 13-step checkout, state machine, cancellation
│   │   ├── cart_service.py  # cart ops + validation
│   │   ├── token_service.py # daily sequential tokens
│   │   ├── inventory_service.py # non-negative stock, auto availability
│   │   ├── notification_service.py
│   │   ├── report_service.py# aggregations + CSV
│   │   ├── menu_service.py  # shared menu queries
│   │   └── settings_service.py
│   ├── forms/               # WTForms (validation + CSRF)
│   ├── utils/               # decorators, validators, helpers
│   ├── templates/           # Jinja2 (student + admin + errors + partials)
│   └── static/
│       ├── css/styles.css   # design system + student UI
│       ├── css/admin.css    # admin panel skin
│       ├── js/main.js       # toasts, modals, AJAX cart, polling
│       ├── js/charts.js     # dependency-free canvas charts
│       ├── images/          # generated food photography
│       └── uploads/foods/   # admin image uploads
│
├── instance/                # SQLite database (auto-created)
├── tests/                   # 83 pytest tests
├── seed.py                  # realistic demo data
├── config.py                # env-driven configuration
├── run.py                   # entry point
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Setup & run

```bash
# 1. (optional) virtual environment
python -m venv .venv && source .venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. configure environment
cp .env.example .env          # then set SECRET_KEY (see comment inside)

# 4. create schema + demo data
python seed.py

# 5. run the development server
python run.py
# → http://127.0.0.1:5000
```

### 🧪 Tests

```bash
python -m pytest tests/ -v
```

83 tests cover registration, login/logout, authorization, food & category CRUD, cart,
checkout, stock validation, token generation, order creation, the status state machine,
cancellation, notifications and admin access.

---

## 🔑 Demo accounts (development only)

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@canteen.edu` | `Admin@123` |
| Student | `student@college.edu` | `Student@123` |

More seeded students: `aarav.sharma@college.edu`, `sneha.iyer@college.edu`,
`meera.nair@college.edu` (all `Student@123`) and one deactivated account
(`rohan.verma@college.edu`) to demo admin deactivation.

> Change or delete these before any real deployment.

---

## 🎟️ Digital token system

- Format: **`A001`, `A002`, …** — unique per business day (IST), one token per order
- Generated **inside the checkout transaction** together with the order
- Unique constraint `(token_number, token_date)` guarantees no duplicates
- Shown on the confirmation page, order tracking, student dashboard and admin tables

## 📦 Order status model

```
Order Placed → Confirmed → Preparing → Ready for Pickup → Completed
      └────────────┴────────────┴─→ Cancelled   (before Preparing)
```

* Every change is recorded in `order_status_history` with timestamps & actor
* Admin actions and student cancellation both go through `OrderService.change_status`
  which **rejects illegal transitions**
* Cancelling restores reserved stock and re-enables items that were auto-disabled

## 🗄️ Database tables

`users` · `categories` · `food_items` · `cart` · `cart_items` · `orders` · `order_items` ·
`order_status_history` · `tokens` · `notifications` · `activity_logs` · `settings`

All with primary keys, foreign keys, unique & NOT NULL constraints, indexes and timestamps.

## ⚡ Performance

* Pagination on every list (menu, orders, students, inventory, notifications)
* Targeted indexes (`orders(user_id, created_at)`, `notifications(user_id, is_read)`, …)
* Single-query cart counts and report aggregations
* Lazy-loaded images (`loading="lazy"`), compact generated photos
* Static assets served by Flask's static pipeline (use a CDN/webserver in production)

## 🧑‍💻 Tech stack

Frontend **HTML5 · CSS3 · vanilla JavaScript** (responsive, mobile-first) · Backend **Python Flask**
· ORM **SQLAlchemy** · Database **SQLite** · Templates **Jinja2** · Forms/CSRF **Flask-WTF** ·
Auth **Flask-Login** · Tests **pytest**
