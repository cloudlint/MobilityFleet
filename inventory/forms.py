from django import forms
from django.forms import inlineformset_factory
from .models import Scooter, Parts, Store, StockTransfer, StockTransferItem, ScooterMaintenanceHistory, Supplier, Purchase, PurchaseItem

class ScooterForm(forms.ModelForm):
    class Meta:
        model = Scooter
        fields = '__all__'
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'last_maintenance': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'category': 'Select the scooter category for pricing: A (Sym Orbit 125cc), B (Jet 14 200cc), C (Citycom 300cc), or D (Vespa 150/300cc)',
            'daily_rate': 'Base daily rate. Category-based pricing will override this for daily rentals based on rental duration.'
        }

class PartsForm(forms.ModelForm):
    class Meta:
        model = Parts
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'current_stock': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e.g. 5 or 0.75 for liquids'}),
            'reorder_level': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e.g. 2 or 0.5 for liquids'}),
        }
        help_texts = {
            'current_stock': 'For liquids like oils, you can use decimal values (e.g., 0.75 for 750ml)',
            'reorder_level': 'Set the minimum level before reordering is needed',
        }

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'

class StockTransferForm(forms.ModelForm):
    class Meta:
        model = StockTransfer
        fields = ['source_store', 'destination_store', 'transfer_date', 'status', 'notes']
        widgets = {
            'transfer_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'source_store': 'Store where the parts are currently located',
            'destination_store': 'Store where the parts will be transferred to',
        }

class StockTransferItemForm(forms.ModelForm):
    class Meta:
        model = StockTransferItem
        fields = ['part', 'quantity']
        widgets = {
            'part': forms.Select(attrs={
                'class': 'form-control select2-searchable part-select',
                'placeholder': 'Type Part Number or Name to search...',
                'data-search-field': 'true'
            }),
            'quantity': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01', 'class': 'part-quantity'}),
        }
        help_texts = {
            'quantity': 'Enter decimal values (e.g., 1.5) for items like oil measured in liters',
            'part': 'Type Part Number or Name to search',
        }
    
    def __init__(self, *args, store=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter parts by store if provided and has stock available
        if store:
            self.fields['part'].queryset = Parts.objects.filter(store=store, current_stock__gt=0)
        else:
            # Only show parts that have stock available if no store specified
            self.fields['part'].queryset = Parts.objects.filter(current_stock__gt=0)

# Create formset for multiple transfer items (like JobCardItem formset)
StockTransferItemFormSet = inlineformset_factory(
    StockTransfer, 
    StockTransferItem, 
    form=StockTransferItemForm,
    extra=1,
    can_delete=True,
    fields=['part', 'quantity']
)

class MaintenanceHistoryForm(forms.ModelForm):
    class Meta:
        model = ScooterMaintenanceHistory
        fields = ['scooter', 'maintenance_date', 'description', 'cost', 'performed_by', 'mileage_at_service']
        widgets = {
            'maintenance_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['invoice_number', 'supplier', 'store', 'invoice_date', 'due_date', 'status', 
                 'subtotal', 'discount_percent', 'discount_amount', 'vat_percent', 'vat_amount', 
                 'total_amount', 'amount_paid', 'notes']
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'store': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'subtotal': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'readonly': 'readonly'}),
            'discount_percent': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100', 'class': 'form-control discount-percent'}),
            'discount_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control discount-amount'}),
            'vat_percent': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'max': '100', 'class': 'form-control vat-percent'}),
            'vat_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control vat-amount'}),
            'total_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control', 'readonly': 'readonly'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['store'].help_text = "Select the store where all purchased items will be added to inventory"
        # Make amount_paid optional and set default to 0
        self.fields['amount_paid'].required = False
        self.fields['amount_paid'].initial = 0
        # Set initial values for VAT and discount
        self.fields['subtotal'].initial = 0
        self.fields['discount_percent'].initial = 0
        self.fields['discount_amount'].initial = 0
        self.fields['vat_percent'].initial = 0
        self.fields['vat_amount'].initial = 0

class PurchaseItemForm(forms.ModelForm):
    total_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        widget=forms.NumberInput(attrs={
            'step': '0.01', 
            'readonly': 'readonly', 
            'class': 'form-control total-price-field',
            'tabindex': '-1'
        })
    )
    
    class Meta:
        model = PurchaseItem
        fields = ['store', 'part', 'description', 'quantity', 'unit_price', 'total_price']
        widgets = {
            'store': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'part': forms.Select(attrs={
                'class': 'form-control part-select select2-searchable',
                'placeholder': 'Start typing part name or code...',
                'data-search-field': 'true'
            }),
            'description': forms.TextInput(attrs={'placeholder': 'Item description', 'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0', 'class': 'form-control'}),
        }
        
    def __init__(self, *args, store=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Make scooter field hidden
        if 'scooter' in self.fields:
            self.fields.pop('scooter')
        
        # Make description field optional in the form
        self.fields['description'].required = False
        
        # Filter parts by store if provided
        if store:
            self.fields['part'].queryset = Parts.objects.filter(store=store)
            self.fields['part'].help_text = f"Parts from {store.name}"
        else:
            # Show all parts if no store specified
            self.fields['part'].queryset = Parts.objects.all()
            self.fields['part'].help_text = "Start typing Part Number or Part Name to search"
    
    def clean(self):
        cleaned_data = super().clean()
        part = cleaned_data.get('part')
        description = cleaned_data.get('description')
        
        # Auto-populate description from part if not provided
        if part and not description:
            cleaned_data['description'] = f"{part.name} - {part.part_number}"
        elif not part and not description:
            cleaned_data['description'] = "General Purchase Item"
            
        return cleaned_data

# Create a formset for purchase items
PurchaseItemFormSet = inlineformset_factory(
    Purchase,
    PurchaseItem,
    form=PurchaseItemForm,
    extra=1,
    min_num=1,
    validate_min=True,
    can_delete=True
)
