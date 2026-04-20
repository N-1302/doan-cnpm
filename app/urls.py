from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('trang-chu/', views.home, name='trangchu'),

    # Trang sản phẩm / danh mục / tìm kiếm
    path('san-pham/', views.san_pham, name='san_pham'),
    path('san-pham/<int:maloai>/', views.san_pham_theo_loai, name='san_pham_theo_loai'),
    path('chi-tiet/<int:mabanh>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('danh-muc/', views.category, name='category'),
    path('new-collection/', views.new_collection, name='new_collection'),

    # Tài khoản
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('quen-mat-khau/', views.quen_mat_khau, name='quen_mat_khau'),
    path('dat-lai-mat-khau/', views.dat_lai_mat_khau, name='dat_lai_mat_khau'),

    # Giỏ hàng / thanh toán
    path('gio-hang/', views.gio_hang, name='gio_hang'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('don-hang-cua-toi/', views.don_hang_cua_toi, name='don_hang_cua_toi'),
    path('chi-tiet-don-hang/<int:ma_don_hang>/', views.chi_tiet_don_hang, name='chi_tiet_don_hang'),

    # API giỏ hàng
    path('api/cart/', views.api_cart, name='api_cart'),
    path('api/cart/add/', views.them_vao_gio, name='them_vao_gio'),
    path('api/cart/update/', views.api_cart_update, name='api_cart_update'),
    path('api/cart/remove/', views.api_cart_remove, name='api_cart_remove'),
    path('api/dat-hang/', views.dat_hang, name='dat_hang'),
    path('api/kiem-tra-khuyen-mai/', views.api_kiem_tra_khuyen_mai, name='api_kiem_tra_khuyen_mai'),
    path('api/danh-sach-khuyen-mai/', views.api_danh_sach_khuyen_mai, name='api_danh_sach_khuyen_mai'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('quan-ly-banh/', views.quan_ly_banh, name='quan_ly_banh'),
    path('them-banh/', views.them_banh, name='them_banh'),
    path('sua-banh/<int:mabanh>/', views.sua_banh, name='sua_banh'),
    path('xoa-banh/<int:mabanh>/', views.xoa_banh, name='xoa_banh'),
    path('quan-ly-don-hang/', views.quan_ly_don_hang, name='quan_ly_don_hang'),
    path('cap-nhat-don-hang/<int:madonhang>/', views.cap_nhat_don_hang, name='cap_nhat_don_hang'),
    path('quan-ly-khuyen-mai/', views.quan_ly_khuyen_mai, name='quan_ly_khuyen_mai'),
    path('them-khuyen-mai/', views.them_khuyen_mai, name='them_khuyen_mai'),
    path('xoa-khuyen-mai/<int:makhuyenmai>/', views.xoa_khuyen_mai, name='xoa_khuyen_mai'),
    path('quan-ly-khach-hang/', views.quan_ly_khach_hang, name='quan_ly_khach_hang'),
    path('khoa-tai-khoan/<int:mataikhoan>/', views.khoa_tai_khoan, name='khoa_tai_khoan'),
    path('mo-tai-khoan/<int:mataikhoan>/', views.mo_tai_khoan, name='mo_tai_khoan'),
    path('thong-ke/', views.thong_ke, name='thong_ke'),
    path('quan-ly-lien-he/', views.quan_ly_lien_he, name='quan_ly_lien_he'),
    path('cap-nhat-lien-he/<int:malienhe>/', views.cap_nhat_trang_thai_lien_he, name='cap_nhat_trang_thai_lien_he'),
    path('phan-hoi-lien-he/<int:malienhe>/', views.phan_hoi_lien_he, name='phan_hoi_lien_he'),
    

    # Chi tiết đơn hàng admin - KHÔNG dùng tiền tố /admin/
    path('quan-tri/chi-tiet-don-hang/<int:ma_don_hang>/', views.chi_tiet_don_hang_admin, name='chi_tiet_don_hang_admin'),

    # Quản lý đánh giá
    path('quan-tri/danh-gia/', views.quan_ly_danh_gia, name='quan_ly_danh_gia'),
    path('quan-tri/danh-gia/xoa/<int:madanhgia>/', views.xoa_danh_gia, name='xoa_danh_gia'),

    # Các trang tĩnh
    path('lien-he/', views.lien_he, name='lien_he'),
    path('tin-tuc/', views.tin_tuc, name='tin_tuc'),
    path('chinh-sach-giao-hang/', views.chinh_sach_giao_hang, name='chinh_sach_giao_hang'),
    path('gioi-thieu/', views.gioi_thieu, name='gioi_thieu'),
    path('bao-mat-thong-tin/', views.bao_mat_thong_tin, name='bao_mat_thong_tin'),
    path('dieu-khoan-su-dung/', views.dieu_khoan_su_dung, name='dieu_khoan_su_dung'),
]