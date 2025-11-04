from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.paginator import Paginator
from elasticsearch import Elasticsearch
from .models import Category, Product
from django.http import JsonResponse
import json

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
User = get_user_model()
es = Elasticsearch("http://localhost:9200")

# --------------------------------------------
# Authentication + basic views
# --------------------------------------------


#Authentication services
def signup_page(request):
    return render(request, 'accounts/signup.html')

def login_page(request):
    return render(request, 'accounts/login.html')


def redirect_to_signup(request):
    return redirect('signup_page')

def home_view(request):
    return redirect('ecommerce_home')

@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not all([username, email, password]):
                return JsonResponse({'error': 'Missing fields'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already taken'}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # 👇 Redirect to login page after successful signup
            return JsonResponse({
                'message': 'User created successfully',
                'redirect_url': '/login/'
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            response = JsonResponse({
                'message': 'Login successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
            return response
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    response = redirect('signup')

    # Delete cookies (expire tokens)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token), 'message': 'Login successful'})
    return Response({'error': 'Invalid username or password'}, status=400)

# --------------------------------------------
# Ecommerce main pages
# --------------------------------------------
def ecommerce_home(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'accounts/ecommerce_home.html', {'page_obj': page_obj})

def all_products_view(request):
    products = Product.objects.all().order_by('id')
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)
    return render(request, 'accounts/all_products.html', {'products': products_page})

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    return render(request, 'accounts/category_products.html', {'category': category, 'products': products})

# --------------------------------------------
# 🧭 Elasticsearch-based Search
# --------------------------------------------
def extract_price_from_query(query):
    """Extract numeric price directly from text (no regex)."""
    for word in query.lower().split():
        try:
            return float(word.replace("₹", "").replace(",", ""))
        except ValueError:
            continue
    return None

from django.shortcuts import render
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

def search_products(request):
    query = request.GET.get("q", "").strip().lower()
    words = query.split()

    price_filter = None
    range_type = "lte"

    # Detect "under / below / less than"
    if "under" in words or "below" in words or ("less", "lesser" in words and "than" in words):
        for word in words:
            if word.replace("₹", "").replace(",", "").isdigit():
                price_filter = float(word)
                break
        range_type = "lte"

    # Detect "above / over / greater than
    elif "above" in words or "over" in words or ("greater" in words and "than" in words):
        for word in words:
            if word.replace("₹", "").replace(",", "").isdigit():
                price_filter = float(word)
                break
        range_type = "gte"

    # Remove these keywords and numbers from search text
    cleaned_words = [
        w for w in words if w not in ["under", "below", "less", "than", "above", "over", "greater"]
        and not w.replace("₹", "").replace(",", "").isdigit()
    ]
    cleaned_query = " ".join(cleaned_words).strip()

    # Build Elasticsearch query
    search_body = {
        "query": {
            "bool": {
                "must": [
                    {"multi_match": {
                        "query": cleaned_query or "*",
                        "fields": ["name", "product_name", "category", "category.name", "description"],
                        "fuzziness":1
                    }}
                ],
                "filter": []
            }
        }
    }

    # Apply price filter if found
    if price_filter is not None:
        search_body["query"]["bool"]["filter"].append({
            "range": {"price": {range_type: price_filter}}
        })

    # Execute search in Elasticsearch
    results = es.search(index="products", body=search_body)
    hits = results["hits"]["hits"]
    products = [hit["_source"] for hit in hits]

    return render(request, "accounts/search_results.html", {
        "products": products,
        "query": request.GET.get("q", "")
    })
