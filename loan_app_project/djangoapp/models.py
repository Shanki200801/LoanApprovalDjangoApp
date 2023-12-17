from django.db import models
from django.db.models import Max


# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)


def get_next_customer_id():
    return (Customer.objects.aggregate(Max("customer_id"))["customer_id__max"] or 0) + 1


class Customer(models.Model):
    customer_id = models.IntegerField(default=get_next_customer_id, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


def get_next_loan_id():
    return (Loan.objects.aggregate(Max("loan_id"))["loan_id__max"] or 0) + 1


class Loan(models.Model):
    customer_number = models.IntegerField()
    loan_id = models.IntegerField(default=get_next_loan_id)
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Loan {self.loan_id} for {self.customer.first_name} {self.customer.last_name}"
