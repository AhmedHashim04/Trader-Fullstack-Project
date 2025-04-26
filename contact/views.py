from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.conf import settings
from django.views.generic import  FormView
from .forms import EmailForm


class SendEmailView(FormView):
    form_class = EmailForm
    template_name = 'contact/contact.html'
    success_url = reverse_lazy('account:profile')
    send_mail = True  

    def form_valid(self, form):
        
        from_email = form.cleaned_data("from_email")
        title = form.cleaned_data("title")
        message = form.cleaned_data("message")
        
        if self.send_mail:
            
            send_mail(
                
                title,
                message,
                from_email,  
                [settings.DEFAULT_FROM_EMAIL], 
                
            )

        return super().form_valid(form)


