from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages

# Create your views here.
def category(request):
    categories = Category.objects.filter(is_sub=False)
    # category = Category.objects.filter(is_sub=True) này sẽ chuyển thành danh mục con 
    active_category = request.GET.get('category', '')
    if active_category:
        products = Sanpham.objects.filter(category__slug = active_category)
    context = {'categories': categories, 'products': products, 'active_category': active_category}
    return render(request, 'app/category.html', context)

def search(request):
    if request.method == "POST":
       searched = request.POST['searched']
       keys = Sanpham.objects.filter(name__contains = searched)

    if request.user.is_authenticated:
        khachhang = request.user
        donhang, created = Donhang.objects.get_or_create(khachhang=khachhang, complete=False)
        items = donhang.donhangsanpham_set.all()
        cartItems = donhang.get_cart_items
    else:
        items = []
        donhang = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = donhang['get_cart_items']
    products = Sanpham.objects.all()
    return render(request, 'app/search.html', {"searched": searched, "keys": keys, 'products': products, 'cartItems': cartItems})

def register(request):
    form = CreateUserForm()
    
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
           form.save()
           return redirect('login')
    context = {'form': form}
    return render(request, 'app/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:messages.info(request, 'Sai tên đăng nhập hoặc mật khẩu')
    context = {}
    return render(request, 'app/login.html', context)

def logoutPage(request):
    logout(request)
    return redirect('login')
    

def home(request):
    if request.user.is_authenticated:
        khachhang = request.user
        donhang, created = Donhang.objects.get_or_create(khachhang=khachhang, complete=False)
        items = donhang.donhangsanpham_set.all()
        cartItems = donhang.get_cart_items
        user_not_login = "hidden"
        user_login = "visible"
    else:
        items = []
        donhang = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = donhang['get_cart_items']
        user_not_login = "visible"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub=False)
    products = Sanpham.objects.all()
    context ={'categories': categories, 'products': products, 'cartItems': cartItems, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/trangchu.html', context)

def cart(request):
    if request.user.is_authenticated:
        khachhang = request.user
        donhang, created = Donhang.objects.get_or_create(khachhang=khachhang, complete=False)
        items = donhang.donhangsanpham_set.all()
        user_not_login = "hidden"
        user_login = "visible"
    else:
            items = []
            donhang = {'get_cart_total':0, 'get_cart_items':0}
            user_not_login = "visible"
            user_login = "hidden"
    categories = Category.objects.filter(is_sub=False)
    context ={'categories': categories,'items': items, 'donhang': donhang, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        khachhang = request.user
        donhang, created = Donhang.objects.get_or_create(khachhang=khachhang, complete=False)
        items = donhang.donhangsanpham_set.all()
        user_not_login = "hidden"
        user_login = "visible"
    else:
        items = []
        donhang = {'get_cart_total':0, 'get_cart_items':0}
        user_not_login = "visible"
        user_login = "hidden"
    categories = Category.objects.filter(is_sub=False)
    context ={'categories': categories,'items': items, 'donhang': donhang, 'user_not_login': user_not_login, 'user_login': user_login}
    return render(request, 'app/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    Khachhang = request.user
    sanpham = Sanpham.objects.get(id=productId)
    donhang, created = Donhang.objects.get_or_create(khachhang=Khachhang, complete=False)
    donhangsanpham, created = Donhangsanpham.objects.get_or_create(donhang=donhang, sanpham=sanpham)
    if action == 'add':
        donhangsanpham.quantity +=1
        
    elif action == 'remove':
        donhangsanpham.quantity -=1
    donhangsanpham.save()
 
    if donhangsanpham.quantity<= 0:
        donhangsanpham.delete()

    return JsonResponse('Cập nhật sản phẩm', safe=False)