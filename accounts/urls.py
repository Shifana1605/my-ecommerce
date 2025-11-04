from django.urls import path
from .import views

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # when user visits /accounts/, redirect to signup page
    path('', views.redirect_to_signup, name='redirect_to_signup'),

    path('signup/', views.signup_page, name='signup_page'),
    path('api/signup/', views.signup_view, name='signup_view'),
    path('accounts/signup/', views.signup_view, name='signup_api'),
    path('login/', views.login_view, name='login_page'),
    path('accounts/login/', views.login_view, name='login_api'),
    path('accounts/home/', views.ecommerce_home, name='ecommerce_home'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('all-products/', views.all_products_view, name='all_products'),
    path("search/", views.search_products, name="search"), 
    path('logout/', views.logout_view, name='logout'),
    # API token views
    path('accounts/api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
