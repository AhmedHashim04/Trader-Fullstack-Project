"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail import urls as wagtail_urls

urlpatterns = [
    path('cms/', wagtailadmin_urls),
    path('documents/', wagtaildocs_urls),
    
    path('admin/'   , admin.site.urls),
    path('account/' ,include('account.urls',namespace='account')),
    path(''         ,include('home.urls',namespace='home')),
    path('products/',include('product.urls',namespace='product')),
    path('brands/'  ,include('settings.urls',namespace='settings')),
    path('cart/'    ,include('cart.urls',namespace='cart')),
    path('order/'   ,include('order.urls',namespace='order')),
    path('contact/' ,include('contact.urls',namespace='contact')),
    path('payment/' ,include('payment.urls',namespace='payment')),
    path('coupons/' ,include('coupons.urls',namespace='coupon')),

    path("", include(wagtail_urls)),  # ده آخر سطر
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# handler404 = 'home.views.handler404'
# handler500 = 'home.views.handler500'