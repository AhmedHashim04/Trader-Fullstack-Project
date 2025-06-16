
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import NewsletterSubscriber

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
    def clean_email(self):
        email = self.cleaned_data['email']
        if NewsletterSubscriber.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already subscribed.")
        return email
    def post(self, request, *args, **kwargs):
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            # Optionally, add a success message here
            return HttpResponseRedirect(request.path_info)
        # If not valid, re-render the page with errors
        context = self.get_context_data()
        context['newsletter_form'] = form
        return self.render_to_response(context)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the newsletter form to context
        context['newsletter_form'] = NewsletterForm()
        return context
