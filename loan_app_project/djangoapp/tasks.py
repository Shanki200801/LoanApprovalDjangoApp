# tasks.py in djangoapp
import pandas as pd
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def ingest_excel_data(
    file_path=["./djangoapp/customer_data.xlsx", "./djangoapp/loan_data.xlsx"]
):
    from djangoapp.models import User, Customer, Loan

    loan_df = pd.read_excel(file_path[1])
    customer_df = pd.read_excel(file_path[0])
    print("Ingesting data from Excel file...")
    for index, row in customer_df.iterrows():
        # Assuming the Excel file has columns that match your model fields
        if not Customer.objects.filter(customer_id=row["Customer ID"]).exists():
            Customer.objects.create(
                customer_id=row["Customer ID"],
                first_name=row["First Name"],
                last_name=row["Last Name"],
                age=row["Age"],
                phone_number=row["Phone Number"],
                monthly_salary=row["Monthly Salary"],
                approved_limit=row["Approved Limit"],
            )

    for index, row in loan_df.iterrows():
        if not Loan.objects.filter(loan_id=row["Loan ID"]).exists():
            Loan.objects.create(
                customer_number=row["Customer ID"],
                loan_id=row["Loan ID"],
                loan_amount=row["Loan Amount"],
                tenure=row["Tenure"],
                interest_rate=row["Interest Rate"],
                monthly_payment=row["Monthly payment"],
                emis_paid_on_time=row["EMIs paid on Time"],
                start_date=row["Date of Approval"],
                end_date=row["End Date"],
            )
