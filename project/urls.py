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
 
urlpatterns = [
    # ... المسارات الأخرى ...
    path('admin/'  , admin.site.urls),
    path('',         include('home.urls',namespace='home')),
    # path('about/',   include('home.urls', namespace='about')),  # إضافة صفحة "من نحن"
    path('products/',include('product.urls',namespace='products')),
    path('accounts/',include('accounts.urls',namespace='account')),
    path('cart/',    include('cart.urls',namespace='cart')),
    path('order/',   include('order.urls',namespace='order')),
    path('contact/', include('contact.urls',namespace='contact')),
    path('payment/', include('payment.urls',namespace='payment')),
    path('compare/', include('product.urls',namespace='compare')),  # إضافة رابط للمقارنة
]
 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
