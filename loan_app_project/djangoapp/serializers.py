from rest_framework import serializers
from .models import User, Customer, Loan


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"


class LoanSerializer2(serializers.ModelSerializer):
    customer_details = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = [
            "loan_id",
            "customer_number",
            "customer_details",
            "loan_amount",
            "tenure",
            "interest_rate",
            "monthly_payment",
            "emis_paid_on_time",
            "start_date",
            "end_date",
        ]

    def get_customer_details(self, obj):
        try:
            customer = Customer.objects.get(customer_id=obj.customer_number)
            return CustomerSerializer(customer).data
        except Customer.DoesNotExist:
            return None
