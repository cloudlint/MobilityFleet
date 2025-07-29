# ScootDR Scooter Rental Management System

## Overview
ScootDR is a comprehensive Django-based web application for managing scooter rental operations. The system provides both customer-facing features for browsing and renting scooters, and a staff dashboard for managing inventory, rentals, customers, and analytics.

## Recent Changes (July 22, 2025)
- ✅ Set up Django environment with all requirements from requirements.txt and PostgreSQL database
- ✅ Applied Django migrations successfully for all applications  
- ✅ Changed all dashboard color codes from #333333 to white (#ffffff) in both static/css/style.css and staticfiles/css/style.css
- ✅ Applied changes to improve text visibility on dashboard templates
- ✅ Created downloadable zip archive (scootdr-project.zip) of the complete project
- ✅ Changed font color to white for all page titles (h1 elements): Dashboard, Scooter Inventory, Parts Inventory, Store Locations, Stock Transfers, Purchase Invoices, Service Job Cards, Customers, Rental Management, Analytics Dashboard, Inventory Alerts, and service job card detail pages
- ✅ Updated landing page element colors: Changed h5 and h3 headings (Filters, Popular Products, Scooter Buying Guide, How Rental Works, Our Restoration Process, Request a Restoration Quote, Department Contacts) to color #2c3f52
- ✅ Changed product price element color to #1c8755 in product detail pages
- ✅ Enhanced rental category management in Django Admin:
  - Added image preview functionality in admin list view
  - Improved fieldset organization with dedicated "Card Image" section
  - Added helpful descriptions for image field management
  - Created sample rental categories for demonstration
  - Enabled full CRUD operations for rental category cards on Rent page
- ✅ Fixed cart functionality error:
  - Resolved AttributeError when clicking "Add to Cart" on Products and Buy pages
  - Fixed 'str' object has no attribute 'url' error in cart/views.py
  - Updated cart_add function to use product.get_image_url() method
  - Created sample products, categories, and brands for testing
  - Cart now works properly without image-related errors
- ✅ Updated cart templates with new color styling:
  - Changed h5 headings color to #2c3f52 in cart_detail.html: "Cart Items", "Order Summary", "Shipping & Returns"
  - Changed h5 headings color to #2c3f52 in checkout.html: "Billing & Shipping Information", "Order Summary", "Need Help?"
- ✅ Added authentication requirement for checkout process:
  - Added @login_required decorator to checkout view in cart/views.py
  - Updated Django settings to redirect to customer login (/login/) instead of staff login
  - Configured LOGIN_URL = '/login/' and LOGIN_REDIRECT_URL = '/account/' for customer authentication
  - Users must now login to their account before proceeding to checkout
- ✅ Fixed NoReverseMatch login error:
  - Fixed empty URL pattern error in landing/views.py login_view function
  - Updated login redirect logic to properly handle next_url parameter
  - Added missing model imports (RentalCategory, RestorationGallery) to prevent import errors
  - Django server now starts successfully without URL reversal errors
- ✅ Implemented login requirement and styling updates:
  - Verified checkout process properly redirects unauthenticated users to login page
  - After successful login, users are automatically redirected back to checkout page
  - Updated Account Navigation h5 element color to #2c3f52 in account.html template
  - Cart "Proceed to Checkout" button correctly triggers login flow when user not authenticated
- ✅ Implemented order persistence and My Orders functionality:
  - Created Order and OrderItem models with complete order tracking
  - Updated checkout process to save orders to database with user details
  - Added order history display in My Account under "My Orders" tab
  - Created order detail page to view individual order information
  - Orders now persist after checkout completion and display in user account
  - Added Django admin interface for order management
- ✅ Fixed staff dashboard login redirect issue:
  - Updated login_view to check user.is_staff and redirect appropriately
  - Staff users now redirect to dashboard:index after login
  - Regular customers continue to redirect to landing:account
  - Registration and authentication logic updated for proper role-based redirects

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Django 5.2** - Main web framework providing MVC architecture
- **Python 3.x** - Programming language
- **PostgreSQL** - Primary database (configured but may need to be added)
- **WSGI** - Web Server Gateway Interface for production deployment via main.py

### Frontend Architecture
- **Bootstrap 5** - Responsive CSS framework for UI components
- **Django Templates** - Server-side template rendering
- **Font Awesome** - Icon library for visual elements
- **Select2** - Enhanced select dropdowns for better UX
- **jQuery/JavaScript** - Client-side interactivity and AJAX operations

## Key Components

### Django Applications Structure
The system is organized into 8 main Django applications:

1. **Landing** - Public-facing website with product catalog and rental booking
   - Handles homepage, product listings, category management
   - Contains models for Product, Category, Brand, RentalCategory

2. **Dashboard** - Staff dashboard with analytics and overview
   - Main entry point for staff users
   - Aggregates data from other applications

3. **Inventory** - Scooter and parts inventory management
   - Manages scooters, parts, stores, stock transfers
   - Handles supplier relationships and purchase orders

4. **Customers** - Customer and rental management
   - Customer profiles with contact information and licensing
   - Rental transactions with pricing and status tracking

5. **Service** - Service job cards and maintenance tracking
   - Job card management for repairs and maintenance
   - Parts usage tracking and service checklists

6. **Analytics** - Reporting and business intelligence
   - Automated report scheduling and generation
   - Dashboard widgets and custom analytics

7. **Users** - User profiles and store-based access control
   - Staff user management with store assignments

8. **Cart** - Shopping cart functionality
   - Session-based cart management for product purchases

### Core Data Models

#### Inventory Management
- **Scooter** - Individual scooter units with categories (A-D), status tracking, and rental rates
- **Parts** - Spare parts inventory with stock levels and reorder points
- **Store** - Physical locations for inventory distribution
- **StockTransfer** - Inter-store inventory transfers
- **Supplier** - Vendor management for purchases

#### Customer & Rental Management
- **Customer** - Customer profiles with licensing and contact details
- **Rental** - Rental transactions with dates, pricing, and status
- **Payment** - Payment processing and transaction tracking

#### Service Management
- **JobCard** - Service requests and work orders
- **JobCardItem** - Parts used in service jobs
- **ServiceChecklist** - Maintenance task tracking

## Data Flow

### Customer Journey
1. Customers browse products on the landing page
2. Featured products are dynamically loaded from database
3. Categories are managed through Django admin
4. Cart functionality manages session-based shopping
5. Rental bookings create customer and rental records

### Staff Operations
1. Staff login through dedicated dashboard
2. Store-based access control filters data
3. Inventory management tracks scooters and parts
4. Service management creates job cards
5. Analytics provides reporting and alerts

### System Integration
- Models use foreign key relationships for data integrity
- Django admin provides content management interface
- Template inheritance ensures consistent UI
- Session management handles cart and user state

## External Dependencies

### Python Packages
- **Django 5.2** - Web framework
- **psycopg2-binary** - PostgreSQL database adapter
- **Pillow** - Image processing
- **django-widget-tweaks** - Form rendering enhancements
- **gunicorn** - WSGI HTTP Server for production

### Frontend Libraries
- **Bootstrap 5** - CSS framework
- **Font Awesome 6.4.0** - Icon library
- **Select2** - Enhanced select controls
- **jQuery** - JavaScript utilities

### Development Tools
- **python-dotenv** - Environment variable management
- **django-crispy-forms** - Form styling

## Deployment Strategy

### Development Setup
- Uses Django development server
- Environment variables loaded from .env file
- Debug mode enabled for development
- Static files served directly by Django

### Production Configuration
- WSGI application configured in main.py
- Gunicorn specified for production server
- Static and media file handling configured
- Database URL configuration via environment variables

### Database Strategy
- Models configured for PostgreSQL
- Django migrations handle schema changes
- Admin interface provides data management
- Store-based data filtering for multi-location support

### Security Considerations
- CSRF protection enabled
- Staff-only access decorators for admin functions
- Session-based authentication
- Environment-based secret key management