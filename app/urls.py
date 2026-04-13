from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Trang sản phẩm / danh mục / tìm kiếm
    path('san-pham/', views.san_pham, name='san_pham'),
    path('category/', views.category, name='category'),
    path('search/', views.search, name='search'),

    # Tài khoản
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),

    # Giỏ hàng / thanh toán
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('update_item/', views.updateItem, name='update_item'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # Các trang tĩnh
    path('lien-he/', views.lien_he, name='lien_he'),
    path('tin-tuc/', views.tin_tuc, name='tin_tuc'),
    path('chinh-sach-giao-hang/', views.chinh_sach_giao_hang, name='chinh_sach_giao_hang'),
    path('gioi-thieu/', views.gioi_thieu, name='gioi_thieu'),
]