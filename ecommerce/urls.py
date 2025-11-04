from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from accounts import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Default redirect
    path('', views.redirect_to_signup, name='redirect_to_signup'),

    # 👇 Page routes (for HTML templates)
    path('signup/', views.signup_page, name='signup_page'),
    path('login/', views.login_page, name='login_page'),

    # 👇 API routes (for backend requests)
    path('api/signup/', views.signup_view, name='signup_api'),
    path('api/login/', views.login_view, name='login_api'),

    # Ecommerce routes
    path('home/', views.ecommerce_home, name='ecommerce_home'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('all-products/', views.all_products_view, name='all_products'),
    path("search/", views.search_products, name="search"), 
    path('logout/', views.logout_view, name='logout'),

    # JWT Token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
