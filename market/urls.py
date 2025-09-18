from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('onboard/', views.project_onboard, name='project_onboard'),
    path('register/', views.buyer_register, name='buyer_register'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/success/<int:txn_id>/', views.payment_success, name='payment_success'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('certificate/<int:txn_id>/', views.certificate_view, name='certificate'),
]
