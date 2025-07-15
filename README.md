# ScootDR Scooter Rental Management System

## Overview
ScootDR is a comprehensive Django-based web application for managing scooter rental operations. The system provides both customer-facing features for browsing and renting scooters, and a staff dashboard for managing inventory, services, customers, and analytics.

## System Architecture

### Backend Framework
- **Django 5.2** - Main web framework providing MVC architecture
- **Python 3.x** - Programming language
- **PostgreSQL** - Primary database (via psycopg2-binary)
- **WSGI** - Web Server Gateway Interface for production deployment

### Frontend Architecture
- **Bootstrap 5** - Responsive CSS framework
- **Django Templates** - Server-side template rendering
- **Font Awesome** - Icon library
- **Select2** - Enhanced select dropdowns
- **JavaScript/jQuery** - Client-side interactivity

## Key Components

### Django Applications
1. **Landing** - Public-facing website with product catalog and rental booking
2. **Dashboard** - Staff dashboard with analytics and overview
3. **Inventory** - Scooter and parts inventory management
4. **Customers** - Customer and rental management
5. **Service** - Service job cards and maintenance tracking
6. **Analytics** - Reporting and business intelligence
7. **Users** - User profiles and store-based access control
8. **Cart** - Shopping cart functionality

### Core Models

#### Inventory Management
- **Scooter** - Individual scooter units with categories (A-D), status tracking, and rental rates
- **Parts** - Spare parts inventory with stock levels and reorder points
- **Store** - Physical locations for inventory distribution
- **StockTransfer** - Inter-store inventory transfers
- **Supplier** - Vendor management for purchases

#### Customer & Rental Management
- **Customer** - Customer profiles with contact information and licensing
- **Rental** - Rental transactions with pricing, dates, and status
- **Payment** - Payment processing and tracking
- **PaymentMethod** - Customer payment method storage

#### Service Management
- **JobCard** - Service requests and work orders
- **JobCardItem** - Parts used in service jobs
- **ServiceChecklist** - Quality control checklists

### Authentication & Authorization
- **Django User Model** - Built-in user authentication
- **UserProfile** - Extended user information with store assignments
- **Store-based Access Control** - Users restricted to specific store locations
- **Role-based Permissions** - Staff vs. customer access levels

## Data Flow

### Customer Journey
1. Customer browses scooter categories on landing page
2. Selects rental dates and scooter category
3. Completes booking with personal information
4. Payment processing and confirmation
5. Rental tracking and completion

### Staff Operations
1. Staff login to dashboard with store-specific access
2. Manage inventory, customers, and rentals within assigned store
3. Create service job cards for maintenance
4. Generate reports and analytics
5. Transfer stock between stores

### Inventory Alerts
- Automatic low stock alerts based on reorder levels
- Maintenance due alerts based on mileage/time
- Dashboard notifications for critical items

## External Dependencies

### Python Packages
- **Django 5.2** - Web framework
- **psycopg2-binary** - PostgreSQL adapter
- **gunicorn** - WSGI HTTP Server for production
- **Pillow** - Image processing
- **django-bootstrap4** - Bootstrap integration
- **requests** - HTTP library for external API calls
- **python-dotenv** - Environment variable management

### Frontend Libraries
- **Bootstrap 5** - UI framework
- **Font Awesome 6** - Icons
- **Select2** - Enhanced dropdowns
- **Chart.js** (implied) - Data visualization

### Development Tools
- **selenium** - Browser automation for testing
- **pdfkit** - PDF generation
- **openpyxl** - Excel file handling

## Deployment Strategy

### Development Environment
- Django development server
- SQLite database (fallback)
- Debug mode enabled
- Static file serving via Django

### Production Environment
- **Gunicorn** WSGI server
- **PostgreSQL** database
- Static file serving via web server (Nginx/Apache)
- Environment variable configuration via .env file
- Debug mode disabled

### Configuration Management
- Environment-specific settings via environment variables
- Secret key management through DJANGO_SECRET_KEY
- Database configuration via environment variables
- Debug toggle via environment settings

### Database Migrations
- Django ORM with automatic migration generation
- Schema versioning through migration files
- Data migration support for complex schema changes

## Changelog
- July 02, 2025. Initial setup
- July 02, 2025. Added VAT and Discount functionality to Purchase and JobCard models, forms, and templates

## Recent Changes
✓ Added VAT and Discount fields to Purchase model (subtotal, discount_percent, discount_amount, vat_percent, vat_amount)
✓ Added VAT and Discount fields to JobCard model (subtotal, discount_percent, discount_amount, vat_percent, vat_amount) 
✓ Updated forms to include new VAT and Discount fields with proper widgets and validation
✓ Modified templates for both Purchase and JobCard forms to display VAT and Discount sections
✓ Created database migrations for the new fields
✓ Added JavaScript for automatic VAT/discount calculations in purchase forms
✓ Enhanced purchase detail template with clear VAT and discount display
✓ Added comprehensive search, filtering, and sorting to purchase list view
✓ Created sample purchase data for testing functionality
✓ Setup complete Django application with PostgreSQL database (July 02, 2025)
✓ Verified VAT and discount calculations work correctly: 40% discount applied to subtotal, then 15% VAT applied to discounted amount
✓ Created test data: admin user (admin/admin123), stores, suppliers, parts, and sample purchase
✓ Fixed purchase form JavaScript calculations for dynamic rows using event delegation (July 02, 2025)
✓ Fixed parts export to Excel to respect store filter selections
✓ Added widget_tweaks to INSTALLED_APPS to fix supplier form template error
✓ Fixed Purchase model total amount calculations with proper save method (July 02, 2025)
✓ Updated purchase create/update views to use calculated totals instead of manual assignment
✓ Enhanced scooter export to include License No. and added store filter functionality (July 02, 2025)
✓ Added store filter dropdown to scooter list page with proper filtering and export integration

## User Preferences
Preferred communication style: Simple, everyday language.# MobilityFleet
# MobilityFleet
