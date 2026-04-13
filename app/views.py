from django.db import connection
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.db.models import Sum
from .models import TaiKhoan, LoaiBanh, Banh, PhanQuyen, DonHang, KhuyenMai, ChiTietDonHang
import random

from math import ceil

def get_common_data(request):
    categories = LoaiBanh.objects.all()
    products = Banh.objects.all()

    ma_tai_khoan = request.session.get('ma_tai_khoan')
    ten_dang_nhap = request.session.get('ten_dang_nhap')
    ma_quyen = request.session.get('ma_quyen')

    return {
        'categories': categories,
        'products': products,
        'cartItems': 0,
        'ten_dang_nhap': ten_dang_nhap,
        'ma_tai_khoan': ma_tai_khoan,
        'ma_quyen': ma_quyen,
        'da_dang_nhap': ma_tai_khoan is not None,
    }


def home(request):
    context = get_common_data(request)
    return render(request, 'app/trangchu.html', context)


def category(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                lb.MaLoaiBanh,
                lb.TenLoaiBanh,
                lb.MoTa,
                lb.HinhAnh,
                COUNT(b.MaBanh) AS so_luong_san_pham
            FROM loaibanh lb
            LEFT JOIN banh b ON lb.MaLoaiBanh = b.MaLoaiBanh
            GROUP BY lb.MaLoaiBanh, lb.TenLoaiBanh, lb.MoTa, lb.HinhAnh
            ORDER BY lb.MaLoaiBanh ASC
        """)
        rows = cursor.fetchall()

    categories = []
    for row in rows:
        categories.append({
            'MaLoaiBanh': row[0],
            'TenLoaiBanh': row[1],
            'MoTa': row[2],
            'HinhAnh': row[3],
            'so_luong_san_pham': row[4],
        })

    return render(request, 'app/category.html', {'categories': categories})

def dat_lai_mat_khau(request):
    ma_tai_khoan = request.session.get('reset_ma_tai_khoan')

    if not ma_tai_khoan:
        return redirect('quen_mat_khau')

    tai_khoan = TaiKhoan.objects.filter(ma_tai_khoan=ma_tai_khoan).first()

    if tai_khoan is None:
        request.session.pop('reset_ma_tai_khoan', None)
        return redirect('quen_mat_khau')

    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not otp or not new_password or not confirm_password:
            return render(request, 'app/DatLaiMatKhau.html', {
                'loi': 'Vui lòng nhập đầy đủ thông tin'
            })

        if new_password != confirm_password:
            return render(request, 'app/DatLaiMatKhau.html', {
                'loi': 'Mật khẩu xác nhận không khớp'
            })

        if not tai_khoan.otp or not tai_khoan.otp_date_send:
            return render(request, 'app/DatLaiMatKhau.html', {
                'loi': 'OTP không hợp lệ hoặc chưa được gửi'
            })

        han_otp = tai_khoan.otp_date_send + timedelta(minutes=5)
        if timezone.now() > han_otp:
            return render(request, 'app/DatLaiMatKhau.html', {
                'loi': 'OTP đã hết hạn'
            })

        if otp != tai_khoan.otp:
            return render(request, 'app/DatLaiMatKhau.html', {
                'loi': 'OTP không đúng'
            })

        tai_khoan.mat_khau = make_password(new_password)
        tai_khoan.otp = None
        tai_khoan.otp_date_send = None
        tai_khoan.save(update_fields=['mat_khau', 'otp', 'otp_date_send'])

        request.session.pop('reset_ma_tai_khoan', None)

        return render(request, 'app/DangNhap.html', {
            'thanhcong': 'Đặt lại mật khẩu thành công. Vui lòng đăng nhập lại'
        })

    return render(request, 'app/DatLaiMatKhau.html')

def quen_mat_khau(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()

        if not username_or_email:
            return render(request, 'app/QuenMatKhau.html', {
                'loi': 'Vui lòng nhập tên đăng nhập hoặc email'
            })

        tai_khoan = TaiKhoan.objects.filter(ten_dang_nhap=username_or_email).first()

        if tai_khoan is None:
            tai_khoan = TaiKhoan.objects.filter(email=username_or_email).first()

        if tai_khoan is None:
            return render(request, 'app/QuenMatKhau.html', {
                'loi': 'Không tìm thấy tài khoản'
            })

        otp = str(random.randint(100000, 999999))
        tai_khoan.otp = otp
        tai_khoan.otp_date_send = timezone.now()
        tai_khoan.save(update_fields=['otp', 'otp_date_send'])

        try:
            send_mail(
                subject='Mã OTP đặt lại mật khẩu',
                message=f'Mã OTP của bạn là: {otp}. OTP có hiệu lực trong 5 phút.',
                from_email=None,
                recipient_list=[tai_khoan.email],
                fail_silently=False,
            )
        except Exception:
            return render(request, 'app/QuenMatKhau.html', {
                'loi': 'Không gửi được email OTP. Kiểm tra lại cấu hình email trong settings.py'
            })

        request.session['reset_ma_tai_khoan'] = tai_khoan.ma_tai_khoan

        return redirect('dat_lai_mat_khau')

    return render(request, 'app/QuenMatKhau.html')

def san_pham(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaBanh, TenBanh, HinhAnh, Gia, SoLuongTon, MoTa
            FROM banh
            ORDER BY MaBanh ASC
        """)
        rows = cursor.fetchall()

    products = []
    for row in rows:
        products.append({
            'MaBanh': row[0],
            'TenBanh': row[1],
            'HinhAnh': row[2],
            'Gia': row[3],
            'SoLuongTon': row[4],
            'MoTa': row[5],
        })

    return render(request, 'app/SanPham.html', {
        'products': products,
        'active_category': 'Tất cả sản phẩm'
    })


def san_pham_theo_loai(request, maloai):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaBanh, TenBanh, HinhAnh, Gia, SoLuongTon, MoTa
            FROM banh
            WHERE MaLoaiBanh = %s
            ORDER BY MaBanh ASC
        """, [maloai])
        rows = cursor.fetchall()

    products = []
    for row in rows:
        products.append({
            'MaBanh': row[0],
            'TenBanh': row[1],
            'HinhAnh': row[2],
            'Gia': row[3],
            'SoLuongTon': row[4],
            'MoTa': row[5],
        })

    active_category = ''
    with connection.cursor() as cursor:
        cursor.execute("SELECT TenLoaiBanh FROM loaibanh WHERE MaLoaiBanh = %s", [maloai])
        category_row = cursor.fetchone()
        if category_row:
            active_category = category_row[0]

    return render(request, 'app/sanpham.html', {
        'products': products,
        'active_category': active_category
    })


def product_detail(request, mabanh):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaBanh, TenBanh, HinhAnh, Gia, SoLuongTon, MoTa, MaLoaiBanh
            FROM banh
            WHERE MaBanh = %s
        """, [mabanh])
        row = cursor.fetchone()

    if not row:
        return render(request, 'app/ChiTietSanPham.html', {
            'product': None,
            'related_products': []
        })

    product = {
        'MaBanh': row[0],
        'TenBanh': row[1],
        'HinhAnh': row[2],
        'Gia': row[3],
        'SoLuongTon': row[4],
        'MoTa': row[5],
        'MaLoaiBanh': row[6],
    }

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaBanh, TenBanh, HinhAnh, Gia
            FROM banh
            WHERE MaLoaiBanh = %s AND MaBanh != %s
            ORDER BY MaBanh ASC
            LIMIT 4
        """, [product['MaLoaiBanh'], product['MaBanh']])
        related_rows = cursor.fetchall()

    if not related_rows:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT MaBanh, TenBanh, HinhAnh, Gia
                FROM banh
                WHERE MaBanh != %s
                ORDER BY MaBanh ASC
                LIMIT 4
            """, [product['MaBanh']])
            related_rows = cursor.fetchall()

    related_products = []
    for item in related_rows:
        related_products.append({
            'MaBanh': item[0],
            'TenBanh': item[1],
            'HinhAnh': item[2],
            'Gia': item[3],
        })

    return render(request, 'app/ChiTietSanPham.html', {
        'product': product,
        'related_products': related_products
    })


def search(request):
    context = get_common_data(request)
    searched = ''

    if request.method == 'POST':
        searched = request.POST.get('searched', '').strip()

    if searched:
        keys = Banh.objects.filter(ten_banh__icontains=searched)
    else:
        keys = Banh.objects.all()

    context['searched'] = searched
    context['keys'] = keys
    context['products'] = keys
    return render(request, 'app/search.html', context)


def register(request):
    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten', '').strip()
        ten_dang_nhap = request.POST.get('username', '').strip()
        mat_khau = request.POST.get('password', '').strip()
        email = request.POST.get('email', '').strip()
        sdt = request.POST.get('sdt', '').strip()
        gioi_tinh = request.POST.get('gioi_tinh', '').strip()

        if not ho_ten or not ten_dang_nhap or not mat_khau or not email:
            return render(request, 'app/DangKy.html', {
                'loi': 'Vui lòng nhập đầy đủ thông tin bắt buộc'
            })

        if TaiKhoan.objects.filter(ten_dang_nhap=ten_dang_nhap).exists():
            return render(request, 'app/DangKy.html', {
                'loi': 'Tên đăng nhập đã tồn tại'
            })

        if TaiKhoan.objects.filter(email=email).exists():
            return render(request, 'app/DangKy.html', {
                'loi': 'Email đã tồn tại'
            })

        if sdt and TaiKhoan.objects.filter(sdt=sdt).exists():
            return render(request, 'app/DangKy.html', {
                'loi': 'Số điện thoại đã tồn tại'
            })

        TaiKhoan.objects.create(
            ho_ten=ho_ten,
            ten_dang_nhap=ten_dang_nhap,
            mat_khau=make_password(mat_khau),
            email=email,
            sdt=sdt if sdt else None,
            gioi_tinh=gioi_tinh if gioi_tinh else None,
            ma_quyen_id=2
        )

        confirm_password = request.POST.get('confirm_password', '').strip()
        if mat_khau != confirm_password:
            return render(request, 'app/DangKy.html', {
                'loi': 'Mật khẩu xác nhận không khớp'
                })

        return render(request, 'app/DangNhap.html', {
            'thanhcong': 'Đăng ký thành công, vui lòng đăng nhập'
        })

    return render(request, 'app/DangKy.html')


def loginPage(request):
    if request.session.get('ma_tai_khoan'):
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            return render(request, 'app/DangNhap.html', {
                'loi': 'Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu'
            })

        tai_khoan = TaiKhoan.objects.filter(ten_dang_nhap=username).first()

        if tai_khoan is None:
            tai_khoan = TaiKhoan.objects.filter(email=username).first()

        if tai_khoan and check_password(password, tai_khoan.mat_khau):
            request.session['ma_tai_khoan'] = tai_khoan.ma_tai_khoan
            request.session['ten_dang_nhap'] = tai_khoan.ten_dang_nhap
            request.session['ma_quyen'] = tai_khoan.ma_quyen_id if tai_khoan.ma_quyen else None

            if tai_khoan.ma_quyen_id == 1:
                return redirect('admin_dashboard')
            return redirect('home')

        return render(request, 'app/DangNhap.html', {
            'loi': 'Sai tên đăng nhập/email hoặc mật khẩu'
        })

    return render(request, 'app/DangNhap.html')


def logoutPage(request):
    request.session.flush()
    return redirect('login')


def cart(request):
    context = get_common_data(request)
    context['items'] = []
    context['donhang'] = {'get_cart_total': 0, 'get_cart_items': 0}
    return render(request, 'app/cart.html', context)


def checkout(request):
    context = get_common_data(request)
    context['items'] = []
    context['donhang'] = {'get_cart_total': 0, 'get_cart_items': 0}
    return render(request, 'app/checkout.html', context)


def updateItem(request):
    return JsonResponse('Chức năng giỏ hàng đang được cập nhật theo MySQL', safe=False)


def admin_dashboard(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)
    context['tong_tai_khoan'] = TaiKhoan.objects.count()
    context['tong_banh'] = Banh.objects.count()
    context['tong_loai_banh'] = LoaiBanh.objects.count()

    try:
        from .models import DonHang
        context['tong_don_hang'] = DonHang.objects.count()
    except:
        context['tong_don_hang'] = 0

    return render(request, 'app/admin_dashboard.html', context)


def lien_he(request):
    return render(request, 'app/LienHe.html')


def chinh_sach_giao_hang(request):
    return render(request, 'app/ChinhSachGiaoHang.html')


def gioi_thieu(request):
    return render(request, 'app/GioiThieu.html')


def bao_mat_thong_tin(request):
    return render(request, 'app/BaoMatThongTin.html')


def dieu_khoan_su_dung(request):
    return render(request, 'app/ĐieuKhoanSuDung.html')


def tin_tuc(request):
    category = request.GET.get('category', 'tat-ca')
    page = int(request.GET.get('page', 1))

    all_posts = [
        {
            'id': 1,
            'title': 'Giảm 20% bánh kem sinh nhật cho đơn đặt trước tại SPRINTTEAM',
            'category': 'khuyen-mai',
            'category_name': 'Tin khuyến mãi',
            'date': '08/04/2026',
            'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Chương trình ưu đãi dành cho khách đặt bánh trước 24 giờ. Nhiều mẫu bánh đẹp, phù hợp cho sinh nhật và họp mặt gia đình.',
            'buy_now': False,
        },
    ]

    categories = [
        {'slug': 'tat-ca', 'name': 'Tất cả'},
        {'slug': 'khuyen-mai', 'name': 'Tin khuyến mãi'},
        {'slug': 'san-pham-moi', 'name': 'Sản phẩm mới'},
        {'slug': 'kien-thuc-banh', 'name': 'Kiến thức bánh'},
        {'slug': 'feedback', 'name': 'Feedback'},
    ]

    if category == 'tat-ca':
        filtered_posts = all_posts
    else:
        filtered_posts = [post for post in all_posts if post['category'] == category]

    per_page = 4
    total_posts = len(filtered_posts)
    total_pages = ceil(total_posts / per_page) if total_posts > 0 else 1

    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    posts = filtered_posts[start:end]

    page_numbers = range(1, total_pages + 1)

    context = {
        'posts': posts,
        'categories': categories,
        'current_category': category,
        'current_page': page,
        'total_pages': total_pages,
        'page_numbers': page_numbers,
    }
    return render(request, 'app/TinTuc.html', context)

#Admin - Quản lý bánh
def quan_ly_banh(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)
    context['ds_banh'] = Banh.objects.select_related('ma_loai_banh').all().order_by('-ma_banh')
    context['ds_loai_banh'] = LoaiBanh.objects.all().order_by('ten_loai_banh')
    return render(request, 'app/QuanLyBanh.html', context)


def them_banh(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    if request.method == 'POST':
        ten_banh = request.POST.get('ten_banh', '').strip()
        ma_loai_banh = request.POST.get('ma_loai_banh')
        gia = request.POST.get('gia', 0)
        so_luong_ton = request.POST.get('so_luong_ton', 0)
        hinh_anh = request.POST.get('hinh_anh', '').strip()
        mo_ta = request.POST.get('mo_ta', '').strip()
        trang_thai = request.POST.get('trang_thai', 'Đang bán').strip()

        if ten_banh and ma_loai_banh:
            Banh.objects.create(
                ten_banh=ten_banh,
                ma_loai_banh_id=ma_loai_banh,
                gia=gia,
                so_luong_ton=so_luong_ton,
                hinh_anh=hinh_anh if hinh_anh else None,
                mo_ta=mo_ta if mo_ta else None,
                trang_thai=trang_thai
            )

    return redirect('quan_ly_banh')


def sua_banh(request, mabanh):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    banh = Banh.objects.filter(ma_banh=mabanh).first()
    if not banh:
        return redirect('quan_ly_banh')

    if request.method == 'POST':
        banh.ten_banh = request.POST.get('ten_banh', banh.ten_banh).strip()
        banh.ma_loai_banh_id = request.POST.get('ma_loai_banh', banh.ma_loai_banh_id)
        banh.gia = request.POST.get('gia', banh.gia)
        banh.so_luong_ton = request.POST.get('so_luong_ton', banh.so_luong_ton)
        banh.hinh_anh = request.POST.get('hinh_anh', '').strip()
        banh.mo_ta = request.POST.get('mo_ta', '').strip()
        banh.trang_thai = request.POST.get('trang_thai', banh.trang_thai)
        banh.save()
        return redirect('quan_ly_banh')

    context = get_common_data(request)
    context['banh'] = banh
    context['ds_loai_banh'] = LoaiBanh.objects.all().order_by('ten_loai_banh')
    return render(request, 'app/SuaBanh.html', context)


def xoa_banh(request, mabanh):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    banh = Banh.objects.filter(ma_banh=mabanh).first()
    if banh:
        banh.delete()

    return redirect('quan_ly_banh')

def quan_ly_don_hang(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)
    context['ds_don_hang'] = DonHang.objects.select_related('ma_tai_khoan').all().order_by('-ma_don_hang')
    return render(request, 'app/QuanLyDonHang.html', context)


def cap_nhat_don_hang(request, madonhang):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    don_hang = DonHang.objects.filter(ma_don_hang=madonhang).first()
    if don_hang and request.method == 'POST':
        don_hang.trang_thai_don_hang = request.POST.get('trang_thai_don_hang', don_hang.trang_thai_don_hang)
        don_hang.save()

    return redirect('quan_ly_don_hang')


def quan_ly_khuyen_mai(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)
    context['ds_khuyen_mai'] = KhuyenMai.objects.all().order_by('-ma_khuyen_mai')
    return render(request, 'app/QuanLyKhuyenMai.html', context)


def them_khuyen_mai(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    if request.method == 'POST':
        KhuyenMai.objects.create(
            ten_khuyen_mai=request.POST.get('ten_khuyen_mai', '').strip(),
            ma_giam_gia=request.POST.get('ma_giam_gia', '').strip() or None,
            phan_tram_giam=request.POST.get('phan_tram_giam') or None,
            so_luong=request.POST.get('so_luong') or None,
            ngay_bat_dau=request.POST.get('ngay_bat_dau') or None,
            ngay_ket_thuc=request.POST.get('ngay_ket_thuc') or None,
            dieu_kien_ap_dung=request.POST.get('dieu_kien_ap_dung', '').strip() or None,
            trang_thai=request.POST.get('trang_thai', 'Đang áp dụng').strip()
        )

    return redirect('quan_ly_khuyen_mai')


def xoa_khuyen_mai(request, makhuyenmai):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    km = KhuyenMai.objects.filter(ma_khuyen_mai=makhuyenmai).first()
    if km:
        km.delete()

    return redirect('quan_ly_khuyen_mai')


def thong_ke(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)
    context['tong_tai_khoan'] = TaiKhoan.objects.count()
    context['tong_banh'] = Banh.objects.count()
    context['tong_don_hang'] = DonHang.objects.count()
    context['tong_doanh_thu'] = DonHang.objects.filter(trang_thai_don_hang='Hoàn thành').aggregate(
        tong=Sum('tong_tien')
    )['tong'] or 0

    context['don_hoan_thanh'] = DonHang.objects.filter(trang_thai_don_hang='Hoàn thành').count()
    context['don_cho_xu_ly'] = DonHang.objects.filter(trang_thai_don_hang='Chờ xử lý').count()
    context['don_dang_giao'] = DonHang.objects.filter(trang_thai_don_hang='Đang giao').count()
    context['don_da_huy'] = DonHang.objects.filter(trang_thai_don_hang='Đã hủy').count()

    san_pham_ban_chay = (
        ChiTietDonHang.objects
        .select_related('ma_banh')
        .values('ma_banh__ten_banh')
        .annotate(tong_ban=Sum('so_luong'))
        .order_by('-tong_ban')[:5]
    )

    context['san_pham_ban_chay'] = [
        {
            'ten_banh': item['ma_banh__ten_banh'],
            'tong_ban': item['tong_ban']
        }
        for item in san_pham_ban_chay
    ]

    return render(request, 'app/ThongKe.html', context)

def quan_ly_khach_hang(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)
    context['ds_tai_khoan'] = TaiKhoan.objects.select_related('ma_quyen').all().order_by('-ma_tai_khoan')
    return render(request, 'app/QuanLyKhachHang.html', context)


def khoa_tai_khoan(request, mataikhoan):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    tai_khoan = TaiKhoan.objects.filter(ma_tai_khoan=mataikhoan).first()
    if tai_khoan:
        tai_khoan.random_key = "LOCKED"
        tai_khoan.save()

    return redirect('quan_ly_khach_hang')


def mo_tai_khoan(request, mataikhoan):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    tai_khoan = TaiKhoan.objects.filter(ma_tai_khoan=mataikhoan).first()
    if tai_khoan:
        tai_khoan.random_key = None
        tai_khoan.save()

    return redirect('quan_ly_khach_hang')