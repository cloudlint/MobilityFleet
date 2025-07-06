from django.db import models
from django.core.validators import MinValueValidator

class Store(models.Model):
    """Model representing a physical store location that holds inventory"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Supplier(models.Model):
    """Model representing a supplier for scooters and parts"""
    name = models.CharField(max_length=100)
    address = models.TextField()
    contact_person = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    payment_terms = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class Scooter(models.Model):
    """Model representing a scooter in inventory"""
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('rented', 'Rented Out'),
        ('maintenance', 'Under Maintenance'),
        ('damaged', 'Damaged'),
        ('retired', 'Retired'),
    )
    
    CATEGORY_CHOICES = (
        ('A', 'Category A - Sym Orbit 125cc'),
        ('B', 'Category B - Jet 14 200cc'),
        ('C', 'Category C - Citycom 300cc'),
        ('D', 'Category D - Vespa 150/300cc'),
    )
    
    vin = models.CharField(max_length=100, unique=True, verbose_name="VIN/Serial Number")
    license_number = models.CharField(max_length=100, unique=True, verbose_name="License Number", blank=True, null=True)
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    color = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='A')
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='scooters')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='scooters')
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    mileage = models.PositiveIntegerField(default=0)
    last_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.vin}) - {self.get_category_display()}"
        
    def get_rate_for_days(self, days):
        """
        Calculate the appropriate daily rate based on the scooter category and rental duration
        """
        if self.category == 'A':
            if days == 1:
                return 400
            elif 2 <= days <= 10:
                return 300
            elif 11 <= days <= 29:
                return 225
            else:  # 30+ days
                return 120
        elif self.category == 'B':
            if days == 1:
                return 450
            elif 2 <= days <= 10:
                return 350
            elif 11 <= days <= 29:
                return 255
            else:  # 30+ days
                return 150
        elif self.category == 'C':
            if days == 1:
                return 550
            elif 2 <= days <= 10:
                return 500
            elif 11 <= days <= 29:
                return 350
            else:  # 30+ days
                return 250
        elif self.category == 'D':
            if days == 1:
                return 850
            elif 2 <= days <= 10:
                return 600
            elif 11 <= days <= 29:
                return 400
            else:  # 30+ days
                return 250
        return self.daily_rate  # Default fallback

class Parts(models.Model):
    """Model representing parts inventory"""
    part_number = models.CharField(max_length=100)  # Removed unique=True
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='parts')
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=5, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    category = models.CharField(max_length=100)
    location_in_store = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.part_number} - {self.name}"
    
    class Meta:
        verbose_name = "Part"
        verbose_name_plural = "Parts"
        # Make part number unique only within a store
        unique_together = ['part_number', 'store']

class StockTransfer(models.Model):
    """Model representing transfers of parts between stores"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    transfer_number = models.CharField(max_length=100, unique=True)
    source_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='outgoing_transfers')
    destination_store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='incoming_transfers')
    transfer_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.transfer_number:
            # Generate a unique transfer number
            import datetime
            from django.db import transaction
            
            today = datetime.date.today()
            prefix = f"ST{today.strftime('%Y%m%d')}"
            
            with transaction.atomic():
                # Get the highest existing number for today
                existing_transfers = StockTransfer.objects.filter(
                    transfer_number__startswith=prefix
                ).order_by('-transfer_number')
                
                if existing_transfers.exists():
                    last_number = existing_transfers.first().transfer_number
                    # Extract the sequence number from the last transfer
                    try:
                        sequence = int(last_number.split(prefix)[1]) + 1
                    except (IndexError, ValueError):
                        sequence = 1
                else:
                    sequence = 1
                
                self.transfer_number = f"{prefix}{sequence:03d}"
                
                # Ensure uniqueness (safety check)
                while StockTransfer.objects.filter(transfer_number=self.transfer_number).exists():
                    sequence += 1
                    self.transfer_number = f"{prefix}{sequence:03d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Transfer #{self.transfer_number} - {self.source_store.name} → {self.destination_store.name}"
    
    def get_total_items(self):
        """Get total number of different parts in this transfer"""
        return self.transfer_items.count()
    
    def get_total_quantity(self):
        """Get total quantity of all parts in this transfer"""
        return sum(item.quantity for item in self.transfer_items.all())

class StockTransferItem(models.Model):
    """Model representing individual parts in a stock transfer"""
    stock_transfer = models.ForeignKey(StockTransfer, on_delete=models.CASCADE, related_name='transfer_items')
    part = models.ForeignKey(Parts, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x {self.part.name} for {self.stock_transfer}"
    
    class Meta:
        unique_together = ['stock_transfer', 'part']  # Prevent duplicate parts in same transfer

class Purchase(models.Model):
    """Model representing purchases from suppliers (invoices)"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    
    invoice_number = models.CharField(max_length=100, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchases', null=True, blank=True, help_text="Default store for all purchase items")
    invoice_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], 
                                 help_text="Total before VAT and discount")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)], 
                                         help_text="Discount percentage (0-100)")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], 
                                        help_text="Discount amount in currency")
    vat_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)], 
                                    help_text="VAT percentage (0-100)")
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], 
                                   help_text="VAT amount in currency")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.supplier.name}"
    
    def calculate_subtotal(self):
        """Calculate subtotal from all purchase items"""
        return sum(item.item_total for item in self.items.all())
    
    def calculate_discount_amount(self):
        """Calculate discount amount based on percentage or fixed amount"""
        if self.discount_percent > 0:
            return (self.subtotal * self.discount_percent) / 100
        return self.discount_amount
    
    def calculate_vat_amount(self):
        """Calculate VAT amount based on percentage"""
        if self.vat_percent > 0:
            amount_after_discount = self.subtotal - self.calculate_discount_amount()
            return (amount_after_discount * self.vat_percent) / 100
        return self.vat_amount
    
    def calculate_total_amount(self):
        """Calculate total amount including VAT and after discount"""
        subtotal = self.subtotal
        discount = self.calculate_discount_amount()
        vat = self.calculate_vat_amount()
        return subtotal - discount + vat
    
    @property
    def balance_due(self):
        return self.total_amount - self.amount_paid
    
    @property
    def payment_status_percent(self):
        if self.total_amount == 0:
            return 100
        return int((self.amount_paid / self.total_amount) * 100)
    
    def save(self, *args, **kwargs):
        """Override save to calculate values automatically"""
        # Calculate and set discount amount if percentage is provided
        if self.discount_percent > 0:
            self.discount_amount = self.calculate_discount_amount()
        
        # Calculate and set VAT amount if percentage is provided
        if self.vat_percent > 0:
            self.vat_amount = self.calculate_vat_amount()
        
        # Calculate and set total amount
        self.total_amount = self.calculate_total_amount()
        
        super().save(*args, **kwargs)

class PurchaseItem(models.Model):
    """Model representing items in a purchase invoice"""
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='purchase_items', null=True, blank=True)
    part = models.ForeignKey(Parts, on_delete=models.SET_NULL, null=True, blank=True)
    scooter = models.ForeignKey(Scooter, on_delete=models.SET_NULL, null=True, blank=True)  # Keeping for DB compatibility
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    def __str__(self):
        return f"{self.quantity} x {self.description}"
    
    @property
    def item_total(self):
        return self.quantity * self.unit_price

class ScooterMaintenanceHistory(models.Model):
    """Model representing maintenance history for scooters"""
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE, related_name='maintenance_history')
    maintenance_date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    performed_by = models.CharField(max_length=100)
    mileage_at_service = models.PositiveIntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Maintenance for {self.scooter} on {self.maintenance_date}"
    
    class Meta:
        verbose_name_plural = "Scooter maintenance histories"

class InventoryAlert(models.Model):
    """Model representing inventory alerts for low stock and other issues"""
    ALERT_TYPES = (
        ('low_stock', 'Low Stock'),
        ('overdue_rental', 'Overdue Rental'),
        ('maintenance_due', 'Maintenance Due'),
        ('expiring_item', 'Expiring Item'),
        ('price_change', 'Price Change')
    )
    
    SEVERITY_LEVELS = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    )
    
    STATUS_CHOICES = (
        ('new', 'New'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed')
    )
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='new')
    
    # Related objects - one of these will be set depending on alert type
    part = models.ForeignKey(Parts, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    scooter = models.ForeignKey(Scooter, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True, related_name='alerts')
    
    # Contextual information
    threshold_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Notification metadata
    email_sent = models.BooleanField(default=False)
    dashboard_notification = models.BooleanField(default=True)
    
    # Audit fields
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='created_alerts')
    acknowledged_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    resolved_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_alerts')
    
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_acknowledged = models.DateTimeField(null=True, blank=True)
    date_resolved = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.title}"
    
    class Meta:
        ordering = ['-severity', '-date_created']
