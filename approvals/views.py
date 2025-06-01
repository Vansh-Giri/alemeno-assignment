from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerRegistrationSerializer
from .models import Customer, Loan
from .utils import calculate_emi
from datetime import datetime
from datetime import date
from decimal import Decimal


class RegisterCustomer(APIView):
    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save() 
            return Response({
                'customer_id': customer.customer_id,
                'name': f"{customer.first_name} {customer.last_name}",
                'age': customer.age,
                'monthly_income': float(customer.monthly_income),
                'approved_limit': float(customer.approved_limit),
                'phone_number': customer.phone_number
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckEligibility(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')

        # Validate customer
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=404)

        # Gather loan history
        loans = Loan.objects.filter(customer=customer)
        paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
        num_loans = loans.count()
        current_year = datetime.now().year
        current_year_loans = loans.filter(start_date__year=current_year).count()
        loan_volume = sum(loan.loan_amount for loan in loans)

        # Credit score calculation
        if customer.current_debt > customer.approved_limit:
            credit_score = 0
        else:
            credit_score = (
                paid_on_time * Decimal('0.35') +
                num_loans * Decimal('0.15') +
                current_year_loans * Decimal('0.20') +
                loan_volume * Decimal('0.30')
            )
            credit_score = min(100, int(credit_score))

        # EMI calculations
        existing_emi = sum(loan.emi for loan in loans if loan.end_date >= datetime.now().date())
        requested_emi = calculate_emi(Decimal(str(loan_amount)), Decimal(str(interest_rate)), int(tenure))
        if (existing_emi + requested_emi) > (Decimal("0.5") * customer.monthly_income):
            return Response({
                'customer_id': customer.customer_id,
                'approval': False,
                'interest_rate': interest_rate,
                'corrected_interest_rate': None,
                'tenure': tenure,
                'monthly_installment': round(float(requested_emi), 2),
                'reason': 'Total EMI exceeds 50% of monthly income'
            }, status=200)

        # Approval logic as per assignment
        approval = False
        corrected_interest_rate = None
        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approval = True
            else:
                corrected_interest_rate = 12
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approval = True
            else:
                corrected_interest_rate = 16
        else:
            approval = False

        response = {
            'customer_id': customer.customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': round(float(requested_emi), 2)
        }
        return Response(response, status=200)

    
class CreateLoan(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')

        # Convert inputs properly
        loan_amount_decimal = Decimal(str(loan_amount))
        interest_rate_decimal = Decimal(str(interest_rate))
        tenure_int = int(tenure)

        # Validate customer
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=404)

        # Gather loan history
        loans = Loan.objects.filter(customer=customer)
        paid_on_time = sum(loan.emis_paid_on_time for loan in loans)
        num_loans = loans.count()
        current_year = datetime.now().year
        current_year_loans = loans.filter(start_date__year=current_year).count()
        loan_volume = sum(loan.loan_amount for loan in loans)

        # Credit score calculation
        if customer.current_debt > customer.approved_limit:
            credit_score = 0
        else:
            credit_score = (
                paid_on_time * Decimal('0.35') +
                num_loans * Decimal('0.15') +
                current_year_loans * Decimal('0.20') +
                loan_volume * Decimal('0.30')
            )
            credit_score = min(100, int(credit_score))

        # EMI calculations
        existing_emi = sum(loan.emi for loan in loans if loan.end_date >= datetime.now().date())
        requested_emi = calculate_emi(loan_amount_decimal, interest_rate_decimal, tenure_int)

        # EMI limit check
        if (existing_emi + requested_emi) > (Decimal("0.5") * customer.monthly_income):
            return Response({
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": "Loan rejected: Total EMI exceeds 50% of monthly income",
                "monthly_installment": round(float(requested_emi), 2)
            }, status=200)

        # Approval logic as per assignment
        loan_approved = False
        corrected_interest_rate = None
        message = "Loan rejected: Not eligible as per credit policy"

        if credit_score > 50:
            loan_approved = True
        elif 30 < credit_score <= 50:
            if interest_rate_decimal > Decimal('12'):
                loan_approved = True
            else:
                corrected_interest_rate = Decimal('12')
                message = "Loan approved at corrected interest rate"
        elif 10 < credit_score <= 30:
            if interest_rate_decimal > Decimal('16'):
                loan_approved = True
            else:
                corrected_interest_rate = Decimal('16')
                message = "Loan approved at corrected interest rate"
        else:
            loan_approved = False
            message = "Loan rejected: Credit score too low"

        # If interest rate was corrected, recalculate EMI
        final_interest_rate = corrected_interest_rate if corrected_interest_rate is not None else interest_rate_decimal
        final_emi = calculate_emi(loan_amount_decimal, final_interest_rate, tenure_int)

        # If approved, create the loan
        if loan_approved or corrected_interest_rate:
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount_decimal,
                tenure=tenure_int,
                interest_rate=final_interest_rate,
                emi=final_emi,
                emis_paid_on_time=0,
                start_date=date.today(),
                end_date=date.today().replace(year=date.today().year + tenure_int // 12)
            )
            # Add to current_debt properly with Decimal
            customer.current_debt += loan_amount_decimal
            customer.save()
            loan_id = loan.loan_id
            if not message.startswith("Loan approved"):
                message = "Loan approved"
            response_status = status.HTTP_201_CREATED
        else:
            loan_id = None
            response_status = status.HTTP_200_OK

        return Response({
            "loan_id": loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": bool(loan_id),
            "message": message,
            "monthly_installment": round(float(final_emi), 2)
        }, status=response_status)


class ViewLoan(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return Response({'error': 'Loan not found'}, status=404)
        
        customer = loan.customer  # This is the Customer object

        response_data = {
            "loan_id": loan.loan_id,
            "customer": {
                "id": customer.customer_id,  # This is the customer's ID
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone_number": customer.phone_number,
                "age": customer.age,
            },
            "loan_amount": float(loan.loan_amount),
            "interest_rate": float(loan.interest_rate),
            "monthly_installment": float(loan.emi),
            "tenure": int(loan.tenure)
        }
        return Response(response_data, status=200)

    
class ViewLoansByCustomer(APIView):
    def get(self, request, customer_id):
        loans = Loan.objects.filter(customer__customer_id=customer_id)
        if not loans.exists():
            return Response({'error': 'No loans found for this customer'}, status=404)
        loans_list = []
        for loan in loans:
            repayments_left = int(loan.tenure) - int(loan.emis_paid_on_time)
            loans_list.append({
                "loan_id": loan.loan_id,
                "loan_amount": float(loan.loan_amount),
                "interest_rate": float(loan.interest_rate),
                "monthly_installment": float(loan.emi),
                "repayments_left": repayments_left
            })
        return Response(loans_list, status=200)
