from django.db import models

class Customer(models.Model):
    customer_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(null=True, blank=True)  # If needed
    phone_number = models.CharField(max_length=15)  # Or BigIntegerField
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=12, decimal_places=2)
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0)

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_id = models.AutoField(primary_key=True)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.PositiveIntegerField()
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)
    emi = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
