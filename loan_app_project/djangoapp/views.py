from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User, Customer, Loan
from .serializers import (
    UserSerializer,
    CustomerSerializer,
    LoanSerializer,
    LoanSerializer2,
)
from django.http import Http404
import requests
import datetime
import json
import logging


# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


# get all users
@api_view(["GET"])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# get single user
@api_view(["GET"])
def getUser(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


# add user
@api_view(["POST"])
def addUser(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


# update user
@api_view(["PUT"])
def updateUser(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(instance=user, data=request.data)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


# delete user
@api_view(["DELETE"])
def deleteUser(request, pk):
    user = User.objects.get(id=pk)
    user.delete()

    return Response("Item successfully deleted!")


# register customer
@api_view(["POST"])
def registerCustomer(request):
    data = request.data
    monthly_salary = data["monthly_salary"]
    approved_limit = round(36 * monthly_salary, -5)  # Round to nearest lakh

    customer = Customer.objects.create(
        first_name=data["first_name"],
        last_name=data["last_name"],
        age=data["age"],
        phone_number=data["phone_number"],
        monthly_salary=monthly_salary,
        approved_limit=approved_limit,
    )

    serializer = CustomerSerializer(customer, many=False)
    return Response(serializer.data)


# get customer detail by cutomer id
@api_view(["GET"])
def getCustomer(request, pk):
    customer = Customer.objects.get(customer_id=pk)
    serializer = CustomerSerializer(customer, many=False)
    return Response(serializer.data)


# view loan by loan id
@api_view(["GET"])
def getLoanByLoanId(request, pk):
    try:
        loan = Loan.objects.get(loan_id=pk)
    except Loan.DoesNotExist:
        raise Http404("Loan does not exist")

    serializer = LoanSerializer2(loan)
    return Response(serializer.data)


# view loan by customer id
@api_view(["GET"])
def getLoanByCustomer(request, pk):
    loan = Loan.objects.filter(customer_number=pk)
    serializer = LoanSerializer(loan, many=True)
    return Response(serializer.data)


def getLoanCustomer(customer_id):
    url = f"http://localhost:8000/users/loancustomer/{customer_id}"
    response = requests.get(url)
    data = response.json()
    return data


def getCustomerDetails(customer_id):
    url = f"http://localhost:8000/users/getcustomer/{customer_id}"
    response = requests.get(url)
    data = response.json()
    return data


def calculate_parameters(loans, customer_details):
    PLPT = sum([loan.emis_paid_on_time / loan.tenure for loan in loans]) / len(loans)
    NLTP = len(loans)
    current_year = 2023  # this should be the current year
    LACY = sum(
        [
            1
            for loan in loans
            if current_year
            in range(int(loan.start_date.year), int(loan.end_date.year) + 1)
        ]
    )
    LAV = customer_details.approved_limit
    CLAL = sum([loan.loan_amount for loan in loans]) > LAV
    EMIF = sum(
        [
            loan.monthly_payment
            for loan in loans
            if int(loan.end_date.year) > current_year
        ]
    ) > 0.5 * float(customer_details.monthly_salary)
    return PLPT, NLTP, LACY, LAV, CLAL, EMIF


def calculate_credit_score(PLPT, NLTP, LACY, LAV, CLAL, EMIF):
    if CLAL:
        return 0
    if EMIF:
        return 0
    else:
        score = (
            0.4 * float(PLPT) - 0.2 * float(NLTP) - 0.2 * float(LACY) - 0.2 * float(LAV)
        )
        return max(min(score, 100), 0)


# check eligibility
@api_view(["POST"])
def checkLoanEligibility(request):
    data = request.data
    customer_id = data["customer_id"]
    loan_amount = data["loan_amount"]
    tenure = data["tenure"]
    interest_rate = data["interest_rate"]

    # logic to check eligibility
    # Fetch loan and customer details directly from the models
    try:
        current_loan_details = Loan.objects.filter(customer_number=customer_id)
        customer_details = Customer.objects.get(customer_id=customer_id)
    except (Loan.DoesNotExist, Customer.DoesNotExist):
        return Response({"error": "Loan or Customer does not exist"}, status=404)

    PLPT, NLTP, LACY, LAV, CLAL, EMIF = calculate_parameters(
        current_loan_details, customer_details
    )
    # calculate credit score.
    score = calculate_credit_score(PLPT, NLTP, LACY, LAV, CLAL, EMIF)
    eligible = False
    approved_interest = interest_rate

    if score > 50:
        eligible = True
    if score > 30 and interest_rate > 12:
        eligible = True
    else:
        eligible = False
        approved_interest = 12
    if score > 10 and interest_rate > 16:
        eligible = True
    else:
        eligible = False
        approved_interest = 16
    if score < 10:
        eligible = False
        approved_interest = 0

    # calculating monthly payment
    if approved_interest == 0:
        emi = 0
    else:
        r = approved_interest / (12 * 100)
        emi = (loan_amount * r * (1 + r) ** tenure) / ((1 + r) ** tenure - 1)

    monthly_payment = round(emi, 2)

    # return customer_id, eligible as approval, interest_rate, approved_interest as corrected_interest_rate, tenure
    return Response(
        {
            "customer_id": customer_id,
            "approval": eligible,
            "interest_rate": interest_rate,
            "corrected_interest_rate": approved_interest,
            "tenure": tenure,
            "monthly_payment": monthly_payment,
        }
    )


# creating a new loan
@api_view(["POST"])
def createLoan(request):
    data = request.data
    customer_id = data["customer_id"]
    loan_amount = data["loan_amount"]
    tenure = data["tenure"]
    interest_rate = data["interest_rate"]

    # logic to create loan
    try:
        customer = Customer.objects.get(customer_id=customer_id)
    except Customer.DoesNotExist:
        return Response({"error": "Customer does not exist"}, status=404)

    # Check eligibility for the above loan
    response = requests.post("http://localhost:8000/users/checkeligibility", json=data)

    # Check for a successful response
    if response.status_code != 200:
        return Response(
            {
                "error": "Error checking eligibility: received status code {}".format(
                    response.status_code
                )
            },
            status=400,
        )

    # Try to parse the response as JSON
    try:
        response_data = response.json()
    except json.JSONDecodeError:
        return Response(
            {"error": "Error checking eligibility: could not parse response as JSON"},
            status=500,
        )

    # Check for the "approval" key in the response data
    if "approval" not in response_data:
        return Response(
            {
                "error": "Error checking eligibility: response does not include 'approval' key"
            },
            logger.info("Error in API %s", response_data),
            status=500,
        )

    # Check the value of the "approval" key
    if not response_data["approval"]:
        return Response({"error": "Customer is not eligible for the loan"}, status=400)

    # ...

    loan = Loan.objects.create(
        customer_number=customer_id,
        loan_amount=loan_amount,
        tenure=tenure,
        interest_rate=interest_rate,
        monthly_payment=response.data["monthly_payment"],
        emis_paid_on_time=0,
        start_date=datetime.date.today(),
        end_date=datetime.date.today() + datetime.timedelta(months=tenure),
    )

    serializer = LoanSerializer(loan, many=False)
    return Response(serializer.data)
