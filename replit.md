# ScootDR Scooter Rental Management System

## Overview

ScootDR is a full-featured Django web application for managing scooter rental operations. It serves two distinct user groups:

1. **Customers** - Public-facing website for browsing scooters, making purchases, booking rentals, and viewing restoration/service info.
2. **Staff** - Internal dashboard for managing inventory, rentals, service job cards, analytics, and customer records.

The system is built around a core Django backend with PostgreSQL as the database, server-side rendered templates using Bootstrap 5, and a modular app structure separating concerns across inventory, customers, service, analytics, cart, and landing pages.

---

## User Preferences

Preferred communication style: Simple, everyday language.

---

## System Architecture

### Backend Framework
- **Django 5.2** with Python 3.x handles all routing, business logic, and template rendering.
- The project is organized as a standard Django monorepo with multiple apps under the root directory.
- The main Django project package is `scooterrentals/` (settings, urls, wsgi, asgi).
- The app runs on port 5000 via `python manage.py runserver 0.0.0.0:5000` (defined in `package.json`).

### Django App Structure
Each app is self-contained with its own `models.py`, `views.py`, `urls.py`, `forms.py`, and `admin.py`:

| App | Purpose |
|-----|---------|
| `landing` | Public website: home, buy, rent, restore, service, contact pages. Manages Products, Categories, Brands, RentalCategories, RestorationGallery. |
| `dashboard` | Staff overview dashboard aggregating data from all other apps. No dedicated models. |
| `inventory` | Scooters, Parts, Stores, StockTransfers, Suppliers, Purchases, InventoryAlerts. |
| `customers` | Customer profiles, Rentals, Payments, PaymentMethods. |
| `service` | JobCards, JobCardItems, ServiceChecklists for maintenance tracking. |
| `analytics` | ReportSchedules, SavedReports, Dashboards, DashboardWidgets. |
| `cart` | Session-based shopping cart with Orders and OrderItems for product purchases. |
| `users` | User profiles and store-based access control. |

### URL Routing
- `/` → `landing` app (public pages)
- `/dashboard/` → `dashboard` app (staff dashboard, login-required + staff-only)
- `/inventory/`, `/service/`, `/customers/`, `/analytics/` → internal management apps
- `/cart/` → cart/checkout flow
- `/users/` → user management
- `/staff-login/` → dedicated staff login page
- `/admin/` → Django admin

### Authentication & Authorization
- Uses Django's built-in auth system (`django.contrib.auth`).
- Staff-only areas protected by a custom `@staff_required` decorator that checks `request.user.is_staff`.
- Public landing pages have no auth requirement; account/order pages use `@login_required`.
- Separate login flows for public customers (`/login/`) and staff (`/staff-login/`).
- Store-based access control via `users` app utilities (`filter_by_user_store`), allowing staff to be scoped to specific store locations.
- Customer profile management: `/account/update-profile/` (profile update) and `/account/change-password/` (password change).
- Password reset with token-based email: `/password-reset/` sends email, `/password-reset-confirm/<uid>/<token>/` sets new password.
- `UserProfile` model extended with `address`, `city`, `postal_code`, `email_notifications`, `low_stock_alerts`, `rental_reminders`, `items_per_page` fields.
- Staff dashboard profile (`/profile/`) and settings (`/settings/`) pages are fully functional with working forms backed by `users/views.py`.

### Frontend Architecture
- **Bootstrap 5** for responsive layout and components.
- **Django Templates** for server-side rendering; templates are in `templates/` at the root level with subdirectories per app.
- **Font Awesome** (local vendor files for offline support) for icons.
- **Select2** (local vendor files) for searchable dropdowns.
- **Google Fonts** (Montserrat, Playfair Display, JetBrains Mono).
- Static files served from `static/` with CSS organized into `css/style.css` (dashboard), `css/landing.css` (public site), `css/mobile.css`, `css/print.css`, `css/icon-colors.css`, and `vendor/` subdirectories.
- **Landing site theme**: Premium navy/gold/cream color palette (`--brand-dark: #1a1a2e`, `--brand-gold: #c9a84c`, `--brand-cream: #faf8f5`). Glass-effect navbar, rounded cards, pill-shaped buttons, refined footer with gold accents.
- **Dashboard theme**: Clean dark theme (`--metallic-dark: #0f1117`), minimal borders, subtle badges with colored backgrounds, no heavy gradients. Refined sidebar with blue active states.
- Dark mode is default (`data-bs-theme="dark"` on body for dashboard).

### Data Models (Key Relationships)
- `Scooter` belongs to a `Store`, has categories (A–D mapped to real scooter models).
- `Rental` links `Customer` → `Scooter`, tracks dates, rates, status, payments.
- `JobCard` links `Scooter` → `technician (User)`, tracks service status, parts used, costs.
- `Parts` belong to a `Store`, have stock levels and reorder thresholds.
- `Product` (landing) has `is_featured` flag for homepage display, belongs to `Category` and `Brand`.
- `RentalCategory` manages fleet cards shown on the public rent page.
- `Order` and `OrderItem` (cart) link to `User` and `Product`, storing billing/shipping info. Checkout uses atomic transactions with `select_for_update` for safe stock decrement.
- `InventoryAlert` tracks low stock and maintenance alerts.

### Admin Interface
- Django admin is heavily customized per app with `list_display`, `list_filter`, `search_fields`, fieldsets, and inline models.
- Key admin customizations: `FeaturedProductFilter` for Products, `OrderItemInline` for Orders, `JobCardItemInline` + `ServiceChecklistInline` for JobCards, `StockTransferItemInline` for StockTransfers.
- Staff can manage featured products, category images, rental fleet cards, and restoration gallery entirely through the admin.

### Session-Based Cart
- The shopping cart uses Django sessions (not a database cart per user) — cart data stored in `request.session['cart']` as a dictionary keyed by product ID.
- On checkout, an `Order` record is created in the database.

### Export Utilities
- `utils/export_utils.py` provides Excel export capability (via `openpyxl`) used across inventory, service, and analytics views.

### Environment Configuration
- Settings loaded via `python-dotenv` from a `.env` file at the project root.
- `DATABASE_URL` environment variable used for database connection (also referenced in `server/db.ts` suggesting potential future Node.js integration).
- `DJANGO_SECRET_KEY` from environment with a fallback insecure default (for development only).
- `DEBUG=True` and `ALLOWED_HOSTS=['*']` — intended for development; should be restricted in production.

---

## External Dependencies

### Database
- **PostgreSQL** via `psycopg` and `psycopg-binary` (v3.x).
- `dj-database-url` for parsing `DATABASE_URL` connection strings.
- A `server/db.ts` file references `@neondatabase/serverless` and Drizzle ORM — this suggests a potential Node.js/TypeScript layer or leftover scaffold that is not currently used by the Django app.

### Python Packages
| Package | Purpose |
|---------|---------|
| `Django 5.2` | Core web framework |
| `psycopg` / `psycopg-binary` | PostgreSQL driver |
| `dj-database-url` | Database URL parsing |
| `django-widget-tweaks` | Template form field customization |
| `django-crispy-forms` | Form rendering helpers |
| `django-bootstrap4` | Bootstrap form integration |
| `pillow` | Image processing |
| `openpyxl` | Excel file export |
| `gunicorn` | WSGI production server |
| `python-dotenv` | Environment variable loading |
| `pdfkit` | PDF generation for reports/job cards |
| `Flask` + `Flask-SQLAlchemy` | Present in requirements but appears to be a legacy/parallel analyzer tool, not used in the main Django app |

### Frontend Libraries (vendored locally)
- Bootstrap 5 CSS/JS
- Font Awesome 6
- Select2 + Select2 Bootstrap 5 theme

### Third-Party Services
- **Google Fonts CDN** — Montserrat, Playfair Display, JetBrains Mono.
- No payment gateway integration is currently wired up (payment models exist but processing is not implemented).
- No email backend is explicitly configured (uses Django default; SMTP setup needed for production password reset/notifications).