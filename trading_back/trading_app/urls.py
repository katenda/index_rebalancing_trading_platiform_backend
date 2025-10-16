from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'holdings', views.HoldingViewSet, basename='holding')
router.register(r'portfolio', views.PortfolioViewSet, basename='portfolio')

urlpatterns = [
    path('', include(router.urls)),
]
