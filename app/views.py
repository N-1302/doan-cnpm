from django.db import connection, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from datetime import timedelta, datetime
from math import ceil
import random
import json

from .models import (
    TaiKhoan, LoaiBanh, Banh, DonHang, KhuyenMai,
    ChiTietDonHang, GioHang, ChiTietGioHang, ThanhToan
)


def get_common_data(request):
    categories = LoaiBanh.objects.all()
    products = Banh.objects.all()

    ma_tai_khoan = request.session.get('ma_tai_khoan')
    ten_dang_nhap = request.session.get('ten_dang_nhap')
    ma_quyen = request.session.get('ma_quyen')

    cart_items = 0
    if ma_tai_khoan:
        gio_hang = GioHang.objects.filter(
            ma_tai_khoan_id=ma_tai_khoan,
            trang_thai_gio_hang='Đang chọn'
        ).first()

        if gio_hang:
            tong = ChiTietGioHang.objects.filter(ma_gio_hang=gio_hang).aggregate(
                tong_so_luong=Sum('so_luong')
            )
            cart_items = tong['tong_so_luong'] or 0

    return {
        'categories': categories,
        'products': products,
        'cartItems': cart_items,
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


def new_collection(request):
    ds_banh_moi = Banh.objects.all().order_by('-ma_banh')[:8]
    return render(request, 'app/newcollection.html', {
        'new_collection': ds_banh_moi
    })


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
            SELECT MaBanh, TenBanh, HinhAnh, Gia, SoLuongTon, MoTa, TrangThai, MaLoaiBanh
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
            'TrangThai': row[6],
            'MaLoaiBanh': row[7],
        })

    return render(request, 'app/SanPham.html', {
        'products': products,
        'active_category': 'Tất cả sản phẩm'
    })


def san_pham_theo_loai(request, maloai):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaBanh, TenBanh, HinhAnh, Gia, SoLuongTon, MoTa, TrangThai, MaLoaiBanh
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
            'TrangThai': row[6],
            'MaLoaiBanh': row[7],
        })

    active_category = 'Danh mục sản phẩm'

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT TenLoaiBanh
            FROM loaibanh
            WHERE MaLoaiBanh = %s
        """, [maloai])
        category_row = cursor.fetchone()

    if category_row:
        active_category = category_row[0]

    return render(request, 'app/SanPham.html', {
        'products': products,
        'active_category': active_category
    })


def product_detail(request, mabanh):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaBanh, TenBanh, HinhAnh, Gia, SoLuongTon, MoTa, TrangThai, MaLoaiBanh
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
        'TrangThai': row[6],
        'MaLoaiBanh': row[7],
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

    keys = Banh.objects.filter(ten_banh__icontains=searched) if searched else Banh.objects.all()

    context['searched'] = searched
    context['keys'] = keys
    context['products'] = keys
    return render(request, 'app/search.html', context)


def register(request):
    if request.method == 'POST':
        ho_ten = request.POST.get('ho_ten', '').strip()
        ten_dang_nhap = request.POST.get('username', '').strip()
        mat_khau = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        email = request.POST.get('email', '').strip()
        sdt = request.POST.get('sdt', '').strip()
        gioi_tinh = request.POST.get('gioi_tinh', '').strip()

        if not ho_ten or not ten_dang_nhap or not mat_khau or not email:
            return render(request, 'app/DangKy.html', {
                'loi': 'Vui lòng nhập đầy đủ thông tin bắt buộc'
            })

        if mat_khau != confirm_password:
            return render(request, 'app/DangKy.html', {
                'loi': 'Mật khẩu xác nhận không khớp'
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


# =========================
# GIỎ HÀNG
# =========================

def lay_gio_hang(request):
    ma_tai_khoan = request.session.get('ma_tai_khoan')
    if not ma_tai_khoan:
        return None

    gio_hang = GioHang.objects.filter(
        ma_tai_khoan_id=ma_tai_khoan,
        trang_thai_gio_hang='Đang chọn'
    ).first()

    if not gio_hang:
        gio_hang = GioHang.objects.create(
            ma_tai_khoan_id=ma_tai_khoan,
            trang_thai_gio_hang='Đang chọn'
        )

    return gio_hang


def api_cart(request):
    gio_hang = lay_gio_hang(request)

    if not gio_hang:
        return JsonResponse({
            'success': True,
            'items': [],
            'total_items': 0,
            'subtotal': 0
        })

    chi_tiet = ChiTietGioHang.objects.filter(
        ma_gio_hang=gio_hang
    ).select_related('ma_banh')

    items = []
    total_items = 0
    subtotal = 0

    for ct in chi_tiet:
        banh = ct.ma_banh
        thanh_tien = ct.thanh_tien if ct.thanh_tien is not None else (ct.don_gia * ct.so_luong)

        total_items += ct.so_luong
        subtotal += thanh_tien

        hinh = ''
        if banh.hinh_anh:
            if str(banh.hinh_anh).startswith('http'):
                hinh = banh.hinh_anh
            elif str(banh.hinh_anh).startswith('/media/') or str(banh.hinh_anh).startswith('/static/'):
                hinh = banh.hinh_anh
            else:
                hinh = f"/media/{banh.hinh_anh}"

        items.append({
            'ma_banh': banh.ma_banh,
            'ten_banh': banh.ten_banh,
            'hinh_anh': hinh if hinh else '/static/app/images/no-image.png',
            'so_luong': ct.so_luong,
            'don_gia': float(ct.don_gia),
            'thanh_tien': float(thanh_tien),
            'mo_ta_ngan': 'Thêm nội dung đặt bánh' if 'B-' in banh.ten_banh.upper() else ''
        })

    return JsonResponse({
        'success': True,
        'items': items,
        'total_items': total_items,
        'subtotal': float(subtotal)
    })


def api_cart_update(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ'})

    try:
        data = json.loads(request.body)
        ma_banh = data.get('ma_banh')
        action = data.get('action')

        gio_hang = lay_gio_hang(request)
        if not gio_hang:
            return JsonResponse({'success': False, 'message': 'Không tìm thấy giỏ hàng'})

        item = ChiTietGioHang.objects.filter(
            ma_gio_hang=gio_hang,
            ma_banh_id=ma_banh
        ).first()

        if not item:
            return JsonResponse({'success': False, 'message': 'Không tìm thấy sản phẩm trong giỏ'})

        if action == 'plus':
            if item.so_luong >= item.ma_banh.so_luong_ton:
                return JsonResponse({'success': False, 'message': 'Số lượng vượt quá tồn kho'})
            item.so_luong += 1
        elif action == 'minus':
            item.so_luong -= 1
            if item.so_luong <= 0:
                item.delete()
                return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'message': 'Hành động không hợp lệ'})

        item.thanh_tien = item.so_luong * item.don_gia
        item.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def api_cart_remove(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ'})

    try:
        data = json.loads(request.body)
        ma_banh = data.get('ma_banh')

        gio_hang = lay_gio_hang(request)
        if not gio_hang:
            return JsonResponse({'success': False, 'message': 'Không tìm thấy giỏ hàng'})

        ChiTietGioHang.objects.filter(
            ma_gio_hang=gio_hang,
            ma_banh_id=ma_banh
        ).delete()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def them_vao_gio(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ'})

    ma_tai_khoan = request.session.get('ma_tai_khoan')
    if not ma_tai_khoan:
        return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập để thêm vào giỏ hàng'})

    try:
        data = json.loads(request.body)
        ma_banh = data.get('ma_banh')
        so_luong = int(data.get('so_luong', 1))

        banh = Banh.objects.filter(ma_banh=ma_banh).first()
        if not banh:
            return JsonResponse({'success': False, 'message': 'Không tìm thấy sản phẩm'})

        if so_luong <= 0:
            so_luong = 1

        gio_hang = lay_gio_hang(request)

        item = ChiTietGioHang.objects.filter(
            ma_gio_hang=gio_hang,
            ma_banh=banh
        ).first()

        if item:
            tong_so_luong_moi = item.so_luong + so_luong
            if tong_so_luong_moi > banh.so_luong_ton:
                return JsonResponse({'success': False, 'message': 'Số lượng vượt quá tồn kho'})

            item.so_luong = tong_so_luong_moi
            item.thanh_tien = item.so_luong * item.don_gia
            item.save()
        else:
            if so_luong > banh.so_luong_ton:
                return JsonResponse({'success': False, 'message': 'Số lượng vượt quá tồn kho'})

            ChiTietGioHang.objects.create(
                ma_gio_hang=gio_hang,
                ma_banh=banh,
                so_luong=so_luong,
                don_gia=banh.gia,
                thanh_tien=banh.gia * so_luong
            )

        return JsonResponse({'success': True, 'message': 'Đã thêm vào giỏ hàng'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def gio_hang(request):
    context = get_common_data(request)
    return render(request, 'app/GioHang.html', context)


def cart(request):
    return redirect('gio_hang')


def checkout(request):
    ma_tai_khoan = request.session.get('ma_tai_khoan')
    if not ma_tai_khoan:
        return redirect('login')

    context = get_common_data(request)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT gh.MaGioHang
            FROM giohang gh
            WHERE gh.MaTaiKhoan = %s
              AND gh.TrangThaiGioHang = 'Đang chọn'
            LIMIT 1
        """, [ma_tai_khoan])
        gio_hang_row = cursor.fetchone()

        items = []
        tong_tien = 0
        tong_so_luong = 0

        if gio_hang_row:
            ma_gio_hang = gio_hang_row[0]

            cursor.execute("""
                SELECT 
                    ct.MaBanh,
                    b.TenBanh,
                    b.HinhAnh,
                    ct.SoLuong,
                    ct.DonGia,
                    ct.ThanhTien
                FROM chitietgiohang ct
                INNER JOIN banh b ON ct.MaBanh = b.MaBanh
                WHERE ct.MaGioHang = %s
            """, [ma_gio_hang])

            rows = cursor.fetchall()

            for row in rows:
                items.append({
                    'ma_banh': row[0],
                    'ten_banh': row[1],
                    'hinh_anh': row[2],
                    'so_luong': row[3],
                    'don_gia': float(row[4]),
                    'thanh_tien': float(row[5]),
                })
                tong_so_luong += row[3]
                tong_tien += float(row[5])

    phi_van_chuyen = tinh_phi_ship(tong_tien)
    tong_thanh_toan = tong_tien + phi_van_chuyen

    context.update({
        'checkout_items': items,
        'tong_so_luong': tong_so_luong,
        'tong_tien': tong_tien,
        'phi_van_chuyen': phi_van_chuyen,
        'tong_thanh_toan': tong_thanh_toan,
    })

    return render(request, 'app/ThanhToan.html', context)


# =========================
# KHUYẾN MÃI
# =========================

def tinh_phi_ship(tong):
    if tong <= 0:
        return 0
    elif tong < 800000:
        return 30000
    return 15000


def ap_dung_khuyen_mai(tong, ma):
    if not ma:
        return {'success': False, 'message': 'Chưa nhập mã'}

    km = KhuyenMai.objects.filter(ma_giam_gia__iexact=ma).first()
    if not km:
        return {'success': False, 'message': 'Mã không tồn tại'}

    if km.so_luong is not None and km.so_luong <= 0:
        return {'success': False, 'message': 'Mã đã hết lượt'}

    if km.trang_thai and str(km.trang_thai).strip().lower() not in ['còn', 'con', 'đang áp dụng', 'dang ap dung', 'active']:
        return {'success': False, 'message': 'Mã không khả dụng'}

    giam = tong * float(km.phan_tram_giam or 0) / 100

    return {
        'success': True,
        'khuyen_mai': km,
        'tien_giam': giam,
        'phan_tram_giam': float(km.phan_tram_giam or 0),
        'ma_giam_gia': km.ma_giam_gia
    }


def api_kiem_tra_khuyen_mai(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    try:
        data = json.loads(request.body or '{}')
        ma = data.get('ma_giam_gia')
        tong = float(data.get('tam_tinh', 0))

        kq = ap_dung_khuyen_mai(tong, ma)
        if not kq['success']:
            return JsonResponse(kq)

        phi = tinh_phi_ship(tong)
        tong_tt = tong - kq['tien_giam'] + phi

        return JsonResponse({
            'success': True,
            'ma_giam_gia': kq['ma_giam_gia'],
            'phan_tram_giam': kq['phan_tram_giam'],
            'tien_giam': kq['tien_giam'],
            'tong_thanh_toan': tong_tt
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def api_danh_sach_khuyen_mai(request):
    try:
        ds = KhuyenMai.objects.filter(so_luong__gt=0).order_by('-ma_khuyen_mai')

        data = []
        for km in ds:
            if km.trang_thai and str(km.trang_thai).strip().lower() not in ['còn', 'con', 'đang áp dụng', 'dang ap dung', 'active']:
                continue

            data.append({
                'ma_giam_gia': km.ma_giam_gia,
                'ten_khuyen_mai': km.ten_khuyen_mai,
                'phan_tram_giam': float(km.phan_tram_giam or 0),
                'dieu_kien_ap_dung': km.dieu_kien_ap_dung or '',
                'so_luong': km.so_luong or 0,
                'trang_thai': km.trang_thai or ''
            })

        return JsonResponse({
            'success': True,
            'items': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


# =========================
# ĐẶT HÀNG (CHECKOUT)
# =========================

def dat_hang(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Phương thức không hợp lệ'})

    ma_tai_khoan = request.session.get('ma_tai_khoan')
    if not ma_tai_khoan:
        return JsonResponse({'success': False, 'message': 'Vui lòng đăng nhập để đặt hàng'})

    try:
        if request.content_type and 'application/json' in request.content_type:
            data = json.loads(request.body or '{}')
        else:
            data = request.POST

        dia_chi = str(data.get('dia_chi', '')).strip()
        phuong_thuc_thanh_toan = str(data.get('phuong_thuc_thanh_toan', 'COD')).strip()
        vi_dien_tu = str(data.get('vi_dien_tu', '')).strip()
        ma_giam_gia = str(data.get('ma_giam_gia', '')).strip()
        cart = data.get('cart', [])

        if not dia_chi:
            return JsonResponse({'success': False, 'message': 'Vui lòng nhập địa chỉ giao hàng'})

        if not isinstance(cart, list) or len(cart) == 0:
            return JsonResponse({'success': False, 'message': 'Giỏ hàng đang trống'})

        tong_tam_tinh = 0
        chi_tiet_hop_le = []

        for item in cart:
            ma_banh = item.get('ma_banh')
            so_luong = item.get('so_luong', 1)

            try:
                ma_banh = int(ma_banh)
                so_luong = int(so_luong)
            except (TypeError, ValueError):
                return JsonResponse({'success': False, 'message': 'Dữ liệu sản phẩm không hợp lệ'})

            banh = Banh.objects.filter(ma_banh=ma_banh).first()
            if not banh:
                return JsonResponse({'success': False, 'message': f'Không tìm thấy sản phẩm mã {ma_banh}'})

            if so_luong <= 0:
                return JsonResponse({'success': False, 'message': f'Số lượng sản phẩm "{banh.ten_banh}" không hợp lệ'})

            if so_luong > banh.so_luong_ton:
                return JsonResponse({
                    'success': False,
                    'message': f'Sản phẩm "{banh.ten_banh}" không đủ tồn kho'
                })

            don_gia = float(banh.gia)
            thanh_tien = don_gia * so_luong
            tong_tam_tinh += thanh_tien

            chi_tiet_hop_le.append({
                'ma_banh': ma_banh,
                'so_luong': so_luong,
                'don_gia': don_gia,
                'thanh_tien': thanh_tien,
                'banh_obj': banh
            })

        phi_ship = tinh_phi_ship(tong_tam_tinh)

        khuyen_mai = None
        tien_giam = 0

        if ma_giam_gia:
            ket_qua_km = ap_dung_khuyen_mai(tong_tam_tinh, ma_giam_gia)
            if not ket_qua_km['success']:
                return JsonResponse(ket_qua_km)

            khuyen_mai = ket_qua_km['khuyen_mai']
            tien_giam = ket_qua_km['tien_giam']

        tong_tien = tong_tam_tinh - tien_giam + phi_ship
        if tong_tien < 0:
            tong_tien = 0

        with transaction.atomic():
            don_hang = DonHang.objects.create(
                ma_tai_khoan_id=ma_tai_khoan,
                ma_khuyen_mai=khuyen_mai,
                ngay_dat=timezone.now(),
                tong_tien=tong_tien,
                dia_chi_giao_hang=dia_chi,
                trang_thai_don_hang='Chờ xử lý'
            )

            for item in chi_tiet_hop_le:
                ChiTietDonHang.objects.create(
                    ma_don_hang=don_hang,
                    ma_banh_id=item['ma_banh'],
                    so_luong=item['so_luong'],
                    don_gia=item['don_gia'],
                    thanh_tien=item['thanh_tien']
                )

                banh = item['banh_obj']
                banh.so_luong_ton -= item['so_luong']
                banh.save(update_fields=['so_luong_ton'])

            if phuong_thuc_thanh_toan == 'COD':
                phuong_thuc_luu = 'COD'
                trang_thai_thanh_toan = 'Chưa thanh toán'
            elif phuong_thuc_thanh_toan == 'Chuyển khoản':
                phuong_thuc_luu = 'Chuyển khoản'
                trang_thai_thanh_toan = 'Chờ thanh toán'
            elif phuong_thuc_thanh_toan == 'Ví điện tử':
                if vi_dien_tu == 'MoMo':
                    phuong_thuc_luu = 'MoMo'
                elif vi_dien_tu == 'ZaloPay':
                    phuong_thuc_luu = 'ZaloPay'
                else:
                    phuong_thuc_luu = 'Ví điện tử'
                trang_thai_thanh_toan = 'Chờ thanh toán'
            else:
                phuong_thuc_luu = 'COD'
                trang_thai_thanh_toan = 'Chưa thanh toán'

            ThanhToan.objects.create(
                ma_don_hang=don_hang,
                phuong_thuc=phuong_thuc_luu,
                trang_thai=trang_thai_thanh_toan
            )

            if khuyen_mai and khuyen_mai.so_luong is not None:
                khuyen_mai.so_luong -= 1
                khuyen_mai.save(update_fields=['so_luong'])

        return JsonResponse({
            'success': True,
            'message': 'Đặt hàng thành công',
            'ma_don_hang': don_hang.ma_don_hang,
            'tam_tinh': tong_tam_tinh,
            'phi_ship': phi_ship,
            'tien_giam': tien_giam,
            'tong_tien': tong_tien,
            'ma_giam_gia': ma_giam_gia
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


def admin_dashboard(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)
    context['tong_tai_khoan'] = TaiKhoan.objects.count()
    context['tong_banh'] = Banh.objects.count()
    context['tong_loai_banh'] = LoaiBanh.objects.count()
    context['tong_don_hang'] = DonHang.objects.count()

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

    context = {
        'posts': posts,
        'categories': categories,
        'current_category': category,
        'current_page': page,
        'total_pages': total_pages,
        'page_numbers': range(1, total_pages + 1),
    }
    return render(request, 'app/TinTuc.html', context)


# =========================
# ADMIN - BÁNH
# =========================

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


def thong_ke(request):
    filter_type = request.GET.get('filter_type', 'day')
    selected_date = request.GET.get('selected_date', '')
    selected_month = request.GET.get('selected_month', '')

    don_hang_qs = DonHang.objects.select_related('ma_tai_khoan').all().order_by('-ngay_dat')

    chart_labels = []
    chart_data = []
    now = timezone.now()

    if filter_type == 'month':
        if selected_month:
            year, month = map(int, selected_month.split('-'))
        else:
            year = now.year
            month = now.month
            selected_month = f"{year}-{month:02d}"

        ds_don_hang = don_hang_qs.filter(
            ngay_dat__year=year,
            ngay_dat__month=month
        )

        tong_doanh_thu = ds_don_hang.aggregate(total=Sum('tong_tien'))['total'] or 0
        tong_don_hang = ds_don_hang.count()
        don_hoan_thanh = ds_don_hang.filter(trang_thai_don_hang='Hoàn thành').count()
        don_cho_xu_ly = ds_don_hang.filter(trang_thai_don_hang='Chờ xử lý').count()

        doanh_thu_theo_thang = (
            DonHang.objects
            .filter(ngay_dat__year=year)
            .annotate(thang=TruncMonth('ngay_dat'))
            .values('thang')
            .annotate(tong=Sum('tong_tien'))
            .order_by('thang')
        )

        for item in doanh_thu_theo_thang:
            if item['thang']:
                chart_labels.append(item['thang'].strftime('%m/%Y'))
                chart_data.append(float(item['tong'] or 0))
    else:
        filter_type = 'day'

        if selected_date:
            target_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        else:
            target_date = now.date()
            selected_date = target_date.strftime('%Y-%m-%d')

        ds_don_hang = don_hang_qs.filter(ngay_dat__date=target_date)

        tong_doanh_thu = ds_don_hang.aggregate(total=Sum('tong_tien'))['total'] or 0
        tong_don_hang = ds_don_hang.count()
        don_hoan_thanh = ds_don_hang.filter(trang_thai_don_hang='Hoàn thành').count()
        don_cho_xu_ly = ds_don_hang.filter(trang_thai_don_hang='Chờ xử lý').count()

        doanh_thu_theo_ngay = (
            DonHang.objects
            .filter(
                ngay_dat__year=target_date.year,
                ngay_dat__month=target_date.month
            )
            .annotate(ngay=TruncDay('ngay_dat'))
            .values('ngay')
            .annotate(tong=Sum('tong_tien'))
            .order_by('ngay')
        )

        for item in doanh_thu_theo_ngay:
            if item['ngay']:
                chart_labels.append(item['ngay'].strftime('%d/%m'))
                chart_data.append(float(item['tong'] or 0))

    context = {
        'filter_type': filter_type,
        'selected_date': selected_date,
        'selected_month': selected_month,
        'tong_doanh_thu': tong_doanh_thu,
        'tong_don_hang': tong_don_hang,
        'don_hoan_thanh': don_hoan_thanh,
        'don_cho_xu_ly': don_cho_xu_ly,
        'ds_don_hang': ds_don_hang,
        'chart_labels': json.dumps(chart_labels, ensure_ascii=False),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'app/ThongKe.html', context)


def chi_tiet_don_hang_admin(request, ma_don_hang):
    don_hang = get_object_or_404(
        DonHang.objects.select_related('ma_tai_khoan'),
        ma_don_hang=ma_don_hang
    )

    chi_tiet_don = (
        ChiTietDonHang.objects
        .filter(ma_don_hang=don_hang)
        .select_related('ma_banh')
    )

    context = {
        'don_hang': don_hang,
        'chi_tiet_don': chi_tiet_don,
    }
    return render(request, 'app/ChiTietDonHangAdmin.html', context)