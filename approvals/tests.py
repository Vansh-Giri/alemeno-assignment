from datetime import date, timedelta
from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Customer, Loan

class BaseTestCase(APITestCase):
    def create_customer(self, **kwargs):
        return Customer.objects.create(
            customer_id=kwargs.get("customer_id", 101),
            first_name=kwargs.get("first_name", "Test"),
            last_name=kwargs.get("last_name", "User"),
            age=kwargs.get("age", 30),
            phone_number=kwargs.get("phone_number", "9999999999"),
            monthly_income=kwargs.get("monthly_income", 100000),
            approved_limit=kwargs.get("approved_limit", 500000),
            current_debt=kwargs.get("current_debt", 0),
        )

    def create_loan(self, customer, **kwargs):
        return Loan.objects.create(
            customer=customer,
            loan_amount=kwargs.get("loan_amount", 100000),
            tenure=kwargs.get("tenure", 12),
            interest_rate=kwargs.get("interest_rate", 10),
            emi=kwargs.get("emi", 8791.59),
            emis_paid_on_time=kwargs.get("emis_paid_on_time", 0),
            start_date=kwargs.get("start_date", date.today() - timedelta(days=365)),
            end_date=kwargs.get("end_date", date.today() + timedelta(days=365)),
        )


class TestRegisterCustomer(BaseTestCase):
    def test_register_success(self):
        url = reverse('register')
        data = {
            "first_name": "Vansh",
            "last_name": "Giri",
            "age": 24,
            "monthly_income": 90000,
            "phone_number": "9810227517"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn("customer_id", response.data)
        self.assertEqual(response.data["name"], "Vansh Giri")

    def test_register_missing_fields(self):
        url = reverse('register')
        response = self.client.post(url, {"first_name": "Only"}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("last_name", response.data)


class TestCheckEligibility(BaseTestCase):
    @patch("approvals.utils.calculate_emi", return_value=5000)
    def test_eligibility_approved(self, mock_emi):
        customer = self.create_customer()
        url = reverse('check-eligibility')
        data = {
            "customer_id": customer.customer_id,
            "loan_amount": 50000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn("approval", response.data)

    def test_eligibility_customer_not_found(self):
        url = reverse('check-eligibility')
        data = {
            "customer_id": 9999,
            "loan_amount": 10000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)

class TestCreateLoan(BaseTestCase):
    @patch("approvals.views.calculate_emi", return_value=2600)
    def test_create_loan_success(self, mock_emi):
        customer = self.create_customer()
        # Add a previous loan to increase credit score
        self.create_loan(customer, emis_paid_on_time=5, loan_amount=20000)

        url = reverse('create-loan')
        data = {
            "customer_id": customer.customer_id,
            "loan_amount": 30000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [200, 201])
        self.assertTrue(response.data.get("loan_approved", False))

    def test_create_loan_customer_not_found(self):
        url = reverse('create-loan')
        data = {
            "customer_id": 9999,
            "loan_amount": 20000,
            "interest_rate": 10,
            "tenure": 12
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)



class TestViewLoan(BaseTestCase):
    def test_view_loan_success(self):
        customer = self.create_customer()
        loan = self.create_loan(customer)
        url = reverse('view-loan', args=[loan.loan_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["loan_id"], loan.loan_id)
        self.assertEqual(response.data["customer"]["id"], customer.customer_id)

    def test_view_loan_not_found(self):
        url = reverse('view-loan', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TestViewLoansByCustomer(BaseTestCase):
    def test_view_loans_success(self):
        customer = self.create_customer(customer_id=8)
        self.create_loan(customer)
        self.create_loan(customer, loan_amount=120000)
        url = reverse('view-loans-by-customer', args=[8])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_view_loans_not_found(self):
        url = reverse('view-loans-by-customer', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.data)
