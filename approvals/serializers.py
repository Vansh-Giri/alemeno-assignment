from rest_framework import serializers
from .models import Customer
from .models import Loan
from random import randint

class LoanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = [
            'customer_id', 'loan_id', 'loan_amount', 'tenure', 'interest_rate',
            'emi', 'emis_paid_on_time', 'start_date', 'end_date'
        ]
        read_only_fields = ['loan_id', 'emi', 'emis_paid_on_time', 'start_date', 'end_date']

class LoanDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'



class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age', 'monthly_income', 'phone_number']

    def create(self, validated_data):
        monthly_income = validated_data['monthly_income']
        approved_limit = round((36 * monthly_income) / 100000) * 100000

        # Generate unique customer_id
        while True:
            customer_id = randint(100000, 999999)
            if not Customer.objects.filter(customer_id=customer_id).exists():
                break

        return Customer.objects.create(
            customer_id=customer_id,
            approved_limit=approved_limit,
            current_debt=0,
            **validated_data
        )