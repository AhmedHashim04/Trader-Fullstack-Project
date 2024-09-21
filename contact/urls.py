from .views import SendEmailView
from django.urls import path 

app_name = 'contact' 


urlpatterns = [
    
    path( '' , SendEmailView.as_view() , name= 'contact' ),

]

