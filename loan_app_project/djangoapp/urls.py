from django.urls import path
from . import views

urlpatterns = [
    path("register", views.registerCustomer),
    path("getcustomer/<str:pk>", views.getCustomer),
    path("loanid/<str:pk>", views.getLoanByLoanId),
    path("loancustomer/<str:pk>", views.getLoanByCustomer),
    path("checkeligibility", views.checkLoanEligibility),
    path("create-loan", views.createLoan),
]
