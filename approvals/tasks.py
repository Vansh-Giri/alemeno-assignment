from celery import shared_task
import pandas as pd
from .models import Customer, Loan
from django.core.exceptions import ObjectDoesNotExist
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

@shared_task
def ingest_customer_data(file_path):
    logger.info(f"Starting ingestion of customer data from {file_path}")
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        Customer.objects.create(
            customer_id=row['Customer ID'],
            first_name=row['First Name'],
            last_name=row['Last Name'],
            age=row['Age'],  # Only if your model has 'age'
            phone_number=row['Phone Number'],
            monthly_income=row['Monthly Salary'],
            approved_limit=row['Approved Limit'],
            current_debt=0  # If not in Excel, set to 0 or as per assignment
        )
    logger.info("Finished ingestion of customer data")





@shared_task
def ingest_loan_data(file_path):
    logger.info(f"Starting ingestion of loan data from {file_path}")
    df = pd.read_excel(file_path)
    logger.info(f"Loaded {len(df)} rows from {file_path}")

    for idx, row in df.iterrows():
        try:
            customer = Customer.objects.get(customer_id=row['Customer ID'])
            loan, created = Loan.objects.update_or_create(
                loan_id=row['Loan ID'],
                defaults={
                    'customer': customer,
                    'loan_amount': row['Loan Amount'],
                    'tenure': row['Tenure'],
                    'interest_rate': row['Interest Rate'],
                    'emi': row['Monthly payment'],
                    'emis_paid_on_time': row['EMIs paid on Time'],
                    'start_date': row['Date of Approval'],
                    'end_date': row['End Date']
                }
            )
            if created:
                logger.info(f"Created new loan: {row['Loan ID']} for customer {row['Customer ID']}")
            else:
                logger.info(f"Updated existing loan: {row['Loan ID']} for customer {row['Customer ID']}")
        except ObjectDoesNotExist:
            logger.error(f"Customer {row['Customer ID']} not found for loan {row['Loan ID']}")
        except Exception as e:
            logger.error(f"Error processing loan {row['Loan ID']}: {str(e)}")

    logger.info("Finished ingestion of loan data")