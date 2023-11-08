from django.urls import path
from .views import LoginView

app_name = 'auth'

urlpatterns = [
    # POST : Login with raw email/password
    path('login/', LoginView.as_view()),
]
