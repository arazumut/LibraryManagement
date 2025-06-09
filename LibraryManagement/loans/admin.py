from django.contrib import admin
from .models import Loan

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'borrower', 'lender', 'start_date', 'due_date', 'returned_date', 'is_overdue')
    list_filter = ('start_date', 'due_date', 'returned_date')
    search_fields = ('book__title', 'borrower__username', 'lender__username', 'notes')
    date_hierarchy = 'start_date'
    readonly_fields = ('is_overdue',)
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Gecikmiş'
