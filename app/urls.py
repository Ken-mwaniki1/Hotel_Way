from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
   # path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('', views.index, name="home"),
    path('menu/', views.menu, name="menu"),
    
    path('login/', views.login_view, name='login'),
    path('accounts/login/', views.login_view, name='login'),
    
    
    path('create_account/', views.create_account, name='create_account'),

    path('order/<str:room_number>/', views.order, name='order'),  # Use room_number for reservation
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('reception/', include(('app.reception_urls', 'reception'), namespace='reception')),
    path('manager/', include(('app.manager_urls', 'manager'), namespace='manager')),
    path('main/', include(('app.main_urls', 'main'), namespace='main')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
