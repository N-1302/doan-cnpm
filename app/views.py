from django.db import connection, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Sum, Q
from django.db.models.functions import TruncDay, TruncMonth
from datetime import timedelta, datetime
from math import ceil
from django.core.paginator import Paginator
from django.contrib import messages
import random
import json
import re

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

def da_mua_san_pham(ma_tai_khoan, ma_banh):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM donhang dh
            INNER JOIN chitietdonhang ctdh ON dh.MaDonHang = ctdh.MaDonHang
            WHERE dh.MaTaiKhoan = %s
              AND ctdh.MaBanh = %s
        """, [ma_tai_khoan, ma_banh])
        row = cursor.fetchone()
    return row and row[0] > 0

def product_detail(request, mabanh):
    thong_bao_danh_gia = ''
    loi_danh_gia = ''
    ma_tai_khoan = request.session.get('ma_tai_khoan')

    # =========================
    # XỬ LÝ GỬI ĐÁNH GIÁ
    # =========================
    if request.method == 'POST':
        if not ma_tai_khoan:
            loi_danh_gia = 'Vui lòng đăng nhập để đánh giá sản phẩm'
        else:
            so_sao = request.POST.get('so_sao', '').strip()
            noi_dung = request.POST.get('noi_dung', '').strip()

            try:
                so_sao = int(so_sao)
            except (TypeError, ValueError):
                so_sao = 0

            if so_sao < 1 or so_sao > 5:
                loi_danh_gia = 'Vui lòng chọn số sao từ 1 đến 5'
            elif not noi_dung:
                loi_danh_gia = 'Vui lòng nhập nội dung đánh giá'
            else:
                bat_buoc_da_mua = True

                if bat_buoc_da_mua and not da_mua_san_pham(ma_tai_khoan, mabanh):
                    loi_danh_gia = 'Bạn cần mua sản phẩm này trước khi đánh giá'
                else:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT MaDanhGia
                            FROM danhgia
                            WHERE MaTaiKhoan = %s AND MaBanh = %s
                            LIMIT 1
                        """, [ma_tai_khoan, mabanh])
                        danh_gia_cu = cursor.fetchone()

                        if danh_gia_cu:
                            cursor.execute("""
                                UPDATE danhgia
                                SET SoSao = %s, NoiDung = %s
                                WHERE MaTaiKhoan = %s AND MaBanh = %s
                            """, [so_sao, noi_dung, ma_tai_khoan, mabanh])
                            thong_bao_danh_gia = 'Bạn đã cập nhật đánh giá thành công'
                        else:
                            cursor.execute("""
                                INSERT INTO danhgia (MaTaiKhoan, MaBanh, SoSao, NoiDung)
                                VALUES (%s, %s, %s, %s)
                            """, [ma_tai_khoan, mabanh, so_sao, noi_dung])
                            thong_bao_danh_gia = 'Gửi đánh giá thành công'

    # =========================
    # LẤY THÔNG TIN SẢN PHẨM
    # =========================
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
            'related_products': [],
            'reviews': [],
            'diem_trung_binh': 0,
            'tong_luot_danh_gia': 0,
            'co_the_danh_gia': False,
            'thong_bao_danh_gia': thong_bao_danh_gia,
            'loi_danh_gia': loi_danh_gia,
            'danh_gia_cua_toi': None,
            'review_filter': '',
            'ma_tai_khoan': ma_tai_khoan,
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

    # =========================
    # SẢN PHẨM LIÊN QUAN
    # =========================
    related_products = []
    selected_ids = set()

    # 1. Lấy bánh cùng loại trước
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT MaBanh, TenBanh, HinhAnh, Gia, SoLuongTon, TrangThai
            FROM banh
            WHERE MaLoaiBanh = %s
            AND MaBanh != %s
            AND SoLuongTon > 0
            AND (TrangThai = 'Đang bán' OR TrangThai IS NULL OR TrangThai = '')
            ORDER BY MaBanh ASC
            LIMIT 4
        """, [product['MaLoaiBanh'], product['MaBanh']])
        related_rows = cursor.fetchall()

    for item in related_rows:
        related_products.append({
            'MaBanh': item[0],
            'TenBanh': item[1],
            'HinhAnh': item[2],
            'Gia': item[3],
            'SoLuongTon': item[4],
            'TrangThai': item[5],
        })
        selected_ids.add(item[0])

    # 2. Nếu chưa đủ 4 thì lấy thêm bánh khác loại để bù
    so_can_them = 4 - len(related_products)

    if so_can_them > 0:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT MaBanh, TenBanh, HinhAnh, Gia, SoLuongTon, TrangThai
                FROM banh
                WHERE MaBanh != %s
                AND SoLuongTon > 0
                AND (TrangThai = 'Đang bán' OR TrangThai IS NULL OR TrangThai = '')
                ORDER BY MaBanh ASC
            """, [product['MaBanh']])
            extra_rows = cursor.fetchall()

        for item in extra_rows:
            if item[0] not in selected_ids:
                related_products.append({
                    'MaBanh': item[0],
                    'TenBanh': item[1],
                    'HinhAnh': item[2],
                    'Gia': item[3],
                    'SoLuongTon': item[4],
                    'TrangThai': item[5],
                })
                selected_ids.add(item[0])

            if len(related_products) == 4:
                break

    # =========================
    # LỌC ĐÁNH GIÁ THEO SỐ SAO
    # =========================
    review_filter = request.GET.get('so_sao', '').strip()

    query_reviews = """
        SELECT 
            dg.MaDanhGia,
            dg.SoSao,
            dg.NoiDung,
            tk.HoTen,
            tk.TenDangNhap
        FROM danhgia dg
        INNER JOIN taikhoan tk ON dg.MaTaiKhoan = tk.MaTaiKhoan
        WHERE dg.MaBanh = %s
    """
    params_reviews = [mabanh]

    if review_filter in ['5', '4', '3', '2', '1']:
        query_reviews += " AND dg.SoSao = %s "
        params_reviews.append(int(review_filter))

    query_reviews += " ORDER BY dg.MaDanhGia DESC "

    with connection.cursor() as cursor:
        cursor.execute(query_reviews, params_reviews)
        review_rows = cursor.fetchall()

    reviews = []
    for item in review_rows:
        reviews.append({
            'MaDanhGia': item[0],
            'SoSao': item[1],
            'NoiDung': item[2],
            'HoTen': item[3],
            'TenDangNhap': item[4],
        })

    # =========================
    # ĐIỂM TRUNG BÌNH + SỐ LƯỢT
    # =========================
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ROUND(AVG(SoSao), 1), COUNT(*)
            FROM danhgia
            WHERE MaBanh = %s
        """, [mabanh])
        thong_ke_row = cursor.fetchone()

    diem_trung_binh = thong_ke_row[0] if thong_ke_row and thong_ke_row[0] is not None else 0
    tong_luot_danh_gia = thong_ke_row[1] if thong_ke_row else 0

    # =========================
    # ĐÁNH GIÁ CỦA TÔI
    # =========================
    danh_gia_cua_toi = None
    if ma_tai_khoan:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SoSao, NoiDung
                FROM danhgia
                WHERE MaTaiKhoan = %s AND MaBanh = %s
                LIMIT 1
            """, [ma_tai_khoan, mabanh])
            row_my_review = cursor.fetchone()

        if row_my_review:
            danh_gia_cua_toi = {
                'SoSao': row_my_review[0],
                'NoiDung': row_my_review[1],
            }

    # =========================
    # CÓ THỂ ĐÁNH GIÁ KHÔNG
    # =========================
    co_the_danh_gia = False
    if ma_tai_khoan:
        bat_buoc_da_mua = True
        if bat_buoc_da_mua:
            co_the_danh_gia = da_mua_san_pham(ma_tai_khoan, mabanh)
        else:
            co_the_danh_gia = True

    return render(request, 'app/ChiTietSanPham.html', {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'diem_trung_binh': diem_trung_binh,
        'tong_luot_danh_gia': tong_luot_danh_gia,
        'co_the_danh_gia': co_the_danh_gia,
        'thong_bao_danh_gia': thong_bao_danh_gia,
        'loi_danh_gia': loi_danh_gia,
        'danh_gia_cua_toi': danh_gia_cua_toi,
        'review_filter': review_filter,
        'ma_tai_khoan': ma_tai_khoan,
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
            if tai_khoan.random_key == "LOCKED":
                return render(request, 'app/DangNhap.html', {
                    'loi': 'Tài khoản của bạn đã bị khóa!'
                })

            request.session['ma_tai_khoan'] = tai_khoan.ma_tai_khoan
            request.session['ten_dang_nhap'] = tai_khoan.ten_dang_nhap
            request.session['ho_ten'] = tai_khoan.ho_ten
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
        don_gia = float(banh.gia or 0)
        thanh_tien = don_gia * ct.so_luong

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
            'don_gia': don_gia,
            'thanh_tien': thanh_tien,
            'mo_ta_ngan': 'Thêm nội dung đặt bánh' if 'B-' in banh.ten_banh.upper() else ''
        })

    return JsonResponse({
        'success': True,
        'items': items,
        'total_items': total_items,
        'subtotal': subtotal
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

        don_gia_hien_tai = banh.gia

        if item:
            tong_so_luong_moi = item.so_luong + so_luong
            if tong_so_luong_moi > banh.so_luong_ton:
                return JsonResponse({'success': False, 'message': 'Số lượng vượt quá tồn kho'})

            item.so_luong = tong_so_luong_moi
            item.don_gia = don_gia_hien_tai
            item.thanh_tien = item.so_luong * don_gia_hien_tai
            item.save()
        else:
            if so_luong > banh.so_luong_ton:
                return JsonResponse({'success': False, 'message': 'Số lượng vượt quá tồn kho'})

            ChiTietGioHang.objects.create(
                ma_gio_hang=gio_hang,
                ma_banh=banh,
                so_luong=so_luong,
                don_gia=don_gia_hien_tai,
                thanh_tien=don_gia_hien_tai * so_luong
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
                    b.Gia AS DonGia,
                    (b.Gia * ct.SoLuong) AS ThanhTien
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
                    'don_gia': float(row[4]) if row[4] is not None else 0,
                    'thanh_tien': float(row[5]) if row[5] is not None else 0,
                })
                tong_so_luong += row[3]
                tong_tien += float(row[5]) if row[5] is not None else 0

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


def dong_bo_trang_thai_khuyen_mai():
    """
    Tự động cập nhật trạng thái khuyến mãi theo ngày.
    - Hết hạn nếu ngày kết thúc đã qua
    - Đang áp dụng nếu đang trong thời gian hợp lệ
    """

    now = timezone.now()

    # Khuyến mãi hết hạn
    KhuyenMai.objects.filter(
        ngay_ket_thuc__isnull=False,
        ngay_ket_thuc__lt=now
    ).update(
        trang_thai='Hết hạn'
    )

    # Khuyến mãi đang áp dụng
    KhuyenMai.objects.filter(
        Q(ngay_bat_dau__lte=now) | Q(ngay_bat_dau__isnull=True),
        Q(ngay_ket_thuc__gte=now) | Q(ngay_ket_thuc__isnull=True)
    ).exclude(
        trang_thai='Tạm dừng'
    ).exclude(
        trang_thai='Hết hạn'
    ).update(
        trang_thai='Đang áp dụng'
    )


def khuyen_mai_con_hieu_luc():
    """
    Lấy danh sách khuyến mãi còn hiệu lực để hiển thị cho khách.
    Khách chỉ thấy:
    - Còn số lượng
    - Đang trong thời gian áp dụng
    - Trạng thái Đang áp dụng
    """

    dong_bo_trang_thai_khuyen_mai()
    now = timezone.now()

    return KhuyenMai.objects.filter(
        Q(so_luong__gt=0) | Q(so_luong__isnull=True),
        Q(ngay_bat_dau__lte=now) | Q(ngay_bat_dau__isnull=True),
        Q(ngay_ket_thuc__gte=now) | Q(ngay_ket_thuc__isnull=True),
        trang_thai='Đang áp dụng'
    ).order_by('-ma_khuyen_mai')


def ap_dung_khuyen_mai(tong, ma):
    """
    Kiểm tra mã giảm giá khi khách nhập mã.
    """

    if not ma:
        return {
            'success': False,
            'message': 'Chưa nhập mã giảm giá'
        }

    dong_bo_trang_thai_khuyen_mai()
    now = timezone.now()

    km = KhuyenMai.objects.filter(ma_giam_gia__iexact=ma.strip()).first()

    if not km:
        return {
            'success': False,
            'message': 'Mã giảm giá không tồn tại'
        }

    if km.trang_thai == 'Tạm dừng':
        return {
            'success': False,
            'message': 'Mã giảm giá đang tạm dừng'
        }

    if km.ngay_bat_dau and km.ngay_bat_dau > now:
        return {
            'success': False,
            'message': 'Mã giảm giá chưa đến thời gian áp dụng'
        }

    if km.ngay_ket_thuc and km.ngay_ket_thuc < now:
        km.trang_thai = 'Hết hạn'
        km.save(update_fields=['trang_thai'])

        return {
            'success': False,
            'message': 'Mã giảm giá đã hết hạn'
        }

    if km.so_luong is not None and km.so_luong <= 0:
        return {
            'success': False,
            'message': 'Mã giảm giá đã hết lượt sử dụng'
        }

    if km.trang_thai != 'Đang áp dụng':
        return {
            'success': False,
            'message': 'Mã giảm giá không khả dụng'
        }

    phan_tram = float(km.phan_tram_giam or 0)
    tien_giam = tong * phan_tram / 100

    return {
        'success': True,
        'khuyen_mai': km,
        'ma_giam_gia': km.ma_giam_gia,
        'phan_tram_giam': phan_tram,
        'tien_giam': tien_giam
    }


def api_kiem_tra_khuyen_mai(request):
    """
    API kiểm tra mã giảm giá khi khách bấm áp dụng.
    """

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'message': 'Phương thức không hợp lệ'
        })

    try:
        data = json.loads(request.body or '{}')
        ma_giam_gia = data.get('ma_giam_gia', '').strip()
        tam_tinh = float(data.get('tam_tinh', 0))

        ket_qua = ap_dung_khuyen_mai(tam_tinh, ma_giam_gia)

        if not ket_qua['success']:
            return JsonResponse(ket_qua)

        phi_ship = tinh_phi_ship(tam_tinh)
        tong_thanh_toan = tam_tinh - ket_qua['tien_giam'] + phi_ship

        if tong_thanh_toan < 0:
            tong_thanh_toan = 0

        return JsonResponse({
            'success': True,
            'message': 'Áp dụng mã giảm giá thành công',
            'ma_giam_gia': ket_qua['ma_giam_gia'],
            'phan_tram_giam': ket_qua['phan_tram_giam'],
            'tien_giam': ket_qua['tien_giam'],
            'tong_thanh_toan': tong_thanh_toan
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })


def api_danh_sach_khuyen_mai(request):
    """
    API lấy danh sách khuyến mãi cho khách.
    Chỉ trả về mã còn hiệu lực.
    """

    try:
        ds = khuyen_mai_con_hieu_luc()

        data = []

        for km in ds:
            data.append({
                'ma_giam_gia': km.ma_giam_gia,
                'ten_khuyen_mai': km.ten_khuyen_mai,
                'phan_tram_giam': float(km.phan_tram_giam or 0),
                'dieu_kien_ap_dung': km.dieu_kien_ap_dung or '',
                'so_luong': km.so_luong or 0,
                'trang_thai': km.trang_thai or '',
                'ngay_bat_dau': km.ngay_bat_dau.strftime('%d/%m/%Y') if km.ngay_bat_dau else '',
                'ngay_ket_thuc': km.ngay_ket_thuc.strftime('%d/%m/%Y') if km.ngay_ket_thuc else '',
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

            don_gia = float(banh.gia or 0)
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

            gio_hang = GioHang.objects.filter(
                ma_tai_khoan_id=ma_tai_khoan,
                trang_thai_gio_hang='Đang chọn'
            ).first()

            if gio_hang:
                ChiTietGioHang.objects.filter(ma_gio_hang=gio_hang).delete()
                gio_hang.trang_thai_gio_hang = 'Đã đặt hàng'
                gio_hang.save(update_fields=['trang_thai_gio_hang'])

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

            banh.refresh_from_db()

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
    context = get_common_data(request)

    if request.method == 'POST':
        ho_ten = request.POST.get('HoTen', '').strip()
        email = request.POST.get('Email', '').strip()
        so_dien_thoai = request.POST.get('SoDienThoai', '').strip()
        noi_dung = request.POST.get('NoiDung', '').strip()

        ma_tai_khoan = request.session.get('ma_tai_khoan')

        context.update({
            'old_hoten': ho_ten,
            'old_email': email,
            'old_sodienthoai': so_dien_thoai,
            'old_noidung': noi_dung,
        })

        if not ho_ten or not email or not noi_dung:
            messages.error(request, 'Vui lòng nhập đầy đủ các trường bắt buộc.')
            return render(request, 'app/LienHe.html', context)

        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO lienhe (
                        MaTaiKhoan,
                        HoTen,
                        Email,
                        SoDienThoai,
                        NoiDung,
                        TrangThaiXuLy
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    ma_tai_khoan if ma_tai_khoan else None,
                    ho_ten,
                    email,
                    so_dien_thoai if so_dien_thoai else None,
                    noi_dung,
                    'Chưa xử lý'
                ])

            messages.success(request, 'Gửi thông tin liên hệ thành công! Cửa hàng sẽ phản hồi sớm nhất.')
            return redirect('lien_he')

        except Exception as e:
            messages.error(request, f'Có lỗi xảy ra khi gửi liên hệ: {str(e)}')
            return render(request, 'app/LienHe.html', context)

    return render(request, 'app/LienHe.html', context)


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
# ADMIN 
# =========================

def quan_ly_lien_he(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)

    keyword = request.GET.get('keyword', '').strip()
    trang_thai = request.GET.get('trang_thai', '').strip()

    query = """
        SELECT 
            lh.MaLienHe,
            lh.MaTaiKhoan,
            lh.HoTen,
            lh.Email,
            lh.SoDienThoai,
            lh.NoiDung,
            lh.NgayGui,
            lh.TrangThaiXuLy
        FROM lienhe lh
        WHERE 1 = 1
    """
    params = []

    if keyword:
        query += """
            AND (
                lh.HoTen LIKE %s
                OR lh.Email LIKE %s
                OR lh.SoDienThoai LIKE %s
                OR lh.NoiDung LIKE %s
            )
        """
        keyword_like = f"%{keyword}%"
        params.extend([keyword_like, keyword_like, keyword_like, keyword_like])

    if trang_thai:
        query += " AND lh.TrangThaiXuLy = %s "
        params.append(trang_thai)

    query += " ORDER BY lh.MaLienHe DESC "

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    ds_lien_he = []
    for row in rows:
        ds_lien_he.append({
            'MaLienHe': row[0],
            'MaTaiKhoan': row[1],
            'HoTen': row[2],
            'Email': row[3],
            'SoDienThoai': row[4] or '',
            'NoiDung': row[5],
            'NgayGui': row[6],
            'TrangThaiXuLy': row[7] or 'Chưa xử lý',
        })

    context['ds_lien_he'] = ds_lien_he
    context['keyword'] = keyword
    context['trang_thai'] = trang_thai
    return render(request, 'app/QuanLyLienHe.html', context)


def cap_nhat_trang_thai_lien_he(request, malienhe):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    if request.method == 'POST':
        trang_thai_moi = request.POST.get('trang_thai_xu_ly', '').strip()

        if trang_thai_moi in ['Chưa xử lý', 'Đang xử lý', 'Đã xử lý']:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE lienhe
                    SET TrangThaiXuLy = %s
                    WHERE MaLienHe = %s
                """, [trang_thai_moi, malienhe])

    return redirect('quan_ly_lien_he')

def phan_hoi_lien_he(request, malienhe):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    if request.method == 'POST':
        noi_dung_phan_hoi = request.POST.get('noi_dung_phan_hoi', '').strip()

        if not noi_dung_phan_hoi:
            messages.error(request, 'Vui lòng nhập nội dung phản hồi')
            return redirect('quan_ly_lien_he')

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT Email, HoTen, NoiDung
                FROM lienhe
                WHERE MaLienHe = %s
            """, [malienhe])
            row = cursor.fetchone()

        if not row:
            messages.error(request, 'Không tìm thấy liên hệ')
            return redirect('quan_ly_lien_he')

        email_khach = row[0]
        ho_ten = row[1]
        noi_dung_goc = row[2]

        try:
            send_mail(
                subject='Phản hồi từ cửa hàng SPRINTTEAM',
                message=f"""
Xin chào {ho_ten},

Cửa hàng đã nhận được liên hệ của bạn:

"{noi_dung_goc}"

Phản hồi:
{noi_dung_phan_hoi}

Trân trọng,
SPRINTTEAM
    """,
            from_email='your_email@gmail.com',  # ⚠️ QUAN TRỌNG
            recipient_list=[email_khach],
            fail_silently=False,
)

            # cập nhật trạng thái
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE lienhe
                    SET TrangThaiXuLy = 'Đã xử lý'
                    WHERE MaLienHe = %s
                """, [malienhe])

            messages.success(request, 'Đã gửi phản hồi cho khách')

        except Exception as e:
            messages.error(request, f'Lỗi gửi email: {str(e)}')

    return redirect('quan_ly_lien_he')

def quan_ly_danh_gia(request):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    context = get_common_data(request)

    keyword = request.GET.get('keyword', '').strip()
    so_sao = request.GET.get('so_sao', '').strip()
    page_number = request.GET.get('page', 1)

    query = """
        SELECT 
            dg.MaDanhGia,
            dg.SoSao,
            dg.NoiDung,
            dg.MaTaiKhoan,
            dg.MaBanh,
            tk.HoTen,
            tk.TenDangNhap,
            b.TenBanh,
            b.HinhAnh
        FROM danhgia dg
        INNER JOIN taikhoan tk ON dg.MaTaiKhoan = tk.MaTaiKhoan
        INNER JOIN banh b ON dg.MaBanh = b.MaBanh
        WHERE 1 = 1
    """
    params = []

    if so_sao in ['5', '4', '3', '2', '1']:
        query += " AND dg.SoSao = %s "
        params.append(int(so_sao))

    if keyword:
        query += " AND (tk.HoTen LIKE %s OR tk.TenDangNhap LIKE %s) "
        keyword_like = f"%{keyword}%"
        params.extend([keyword_like, keyword_like])

    query += " ORDER BY dg.MaDanhGia DESC "

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        rows = cursor.fetchall()

    ds_danh_gia_all = []
    for row in rows:
        ds_danh_gia_all.append({
            'MaDanhGia': row[0],
            'SoSao': row[1],
            'NoiDung': row[2],
            'MaTaiKhoan': row[3],
            'MaBanh': row[4],
            'HoTen': row[5],
            'TenDangNhap': row[6],
            'TenBanh': row[7],
            'HinhAnh': row[8],
        })

    paginator = Paginator(ds_danh_gia_all, 6)
    ds_danh_gia = paginator.get_page(page_number)

    query_string = ""
    if keyword:
        query_string += f"&keyword={keyword}"
    if so_sao:
        query_string += f"&so_sao={so_sao}"

    context['ds_danh_gia'] = ds_danh_gia
    context['keyword'] = keyword
    context['so_sao'] = so_sao
    context['page_obj'] = ds_danh_gia
    context['query_string'] = query_string
    return render(request, 'app/QuanLyDanhGia.html', context)


def xoa_danh_gia(request, madanhgia):
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM danhgia
            WHERE MaDanhGia = %s
        """, [madanhgia])

    return redirect('quan_ly_danh_gia')

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
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    filter_type = request.GET.get('filter_type', 'all').strip()
    selected_date = request.GET.get('selected_date', '').strip()
    selected_month = request.GET.get('selected_month', '').strip()

    ds_don_hang = []
    chart_labels = []
    chart_data = []
    tong_doanh_thu = 0
    tong_don_hang = 0
    don_hoan_thanh = 0
    don_cho_xu_ly = 0

    where_sql = ""
    params = []

    if filter_type == 'day' and selected_date:
        where_sql = "WHERE DATE(dh.NgayDat) = %s"
        params = [selected_date]
    elif filter_type == 'month' and selected_month:
        try:
            year, month = selected_month.split('-')
            where_sql = "WHERE YEAR(dh.NgayDat) = %s AND MONTH(dh.NgayDat) = %s"
            params = [year, month]
        except ValueError:
            filter_type = 'all'
            selected_month = ''
            where_sql = ""
            params = []
    else:
        filter_type = 'all'
        where_sql = ""
        params = []

    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT 
                dh.MaDonHang,
                dh.NgayDat,
                dh.TongTien,
                dh.TrangThaiDonHang,
                tk.MaTaiKhoan,
                tk.HoTen,
                tk.TenDangNhap
            FROM donhang dh
            LEFT JOIN taikhoan tk ON dh.MaTaiKhoan = tk.MaTaiKhoan
            {where_sql}
            ORDER BY dh.NgayDat DESC
        """, params)
        rows = cursor.fetchall()

        for row in rows:
            ds_don_hang.append({
                'ma_don_hang': row[0],
                'ngay_dat': row[1],
                'tong_tien': float(row[2]) if row[2] is not None else 0,
                'trang_thai_don_hang': row[3] or 'Chờ xử lý',
                'ma_tai_khoan': {
                    'ma_tai_khoan': row[4],
                    'ho_ten': row[5] or '',
                    'ten_dang_nhap': row[6] or ''
                } if row[4] else None
            })

        cursor.execute(f"""
            SELECT 
                COUNT(*) AS tong_don,
                COALESCE(SUM(dh.TongTien), 0) AS tong_doanh_thu,
                SUM(CASE WHEN dh.TrangThaiDonHang = 'Hoàn thành' THEN 1 ELSE 0 END) AS don_hoan_thanh,
                SUM(CASE WHEN dh.TrangThaiDonHang = 'Chờ xử lý' THEN 1 ELSE 0 END) AS don_cho_xu_ly
            FROM donhang dh
            {where_sql}
        """, params)
        stat_row = cursor.fetchone()

        tong_don_hang = stat_row[0] or 0
        tong_doanh_thu = float(stat_row[1] or 0)
        don_hoan_thanh = stat_row[2] or 0
        don_cho_xu_ly = stat_row[3] or 0

        if filter_type == 'day' and selected_date:
            cursor.execute("""
                SELECT HOUR(NgayDat) AS gio, SUM(TongTien) AS tong
                FROM donhang
                WHERE DATE(NgayDat) = %s
                GROUP BY HOUR(NgayDat)
                ORDER BY gio ASC
            """, [selected_date])
            chart_rows = cursor.fetchall()
            for row in chart_rows:
                chart_labels.append(f"{int(row[0]):02d}:00")
                chart_data.append(float(row[1] or 0))

        elif filter_type == 'month' and selected_month:
            year, month = selected_month.split('-')
            cursor.execute("""
                SELECT DATE(NgayDat) AS ngay, SUM(TongTien) AS tong
                FROM donhang
                WHERE YEAR(NgayDat) = %s AND MONTH(NgayDat) = %s
                GROUP BY DATE(NgayDat)
                ORDER BY ngay ASC
            """, [year, month])
            chart_rows = cursor.fetchall()
            for row in chart_rows:
                if row[0]:
                    chart_labels.append(row[0].strftime('%d/%m'))
                    chart_data.append(float(row[1] or 0))
        else:
            cursor.execute("""
                SELECT DATE(NgayDat) AS ngay, SUM(TongTien) AS tong
                FROM donhang
                GROUP BY DATE(NgayDat)
                ORDER BY ngay ASC
            """)
            chart_rows = cursor.fetchall()
            for row in chart_rows:
                if row[0]:
                    chart_labels.append(row[0].strftime('%d/%m/%Y'))
                    chart_data.append(float(row[1] or 0))

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
    if request.session.get('ma_quyen') != 1:
        return redirect('home')

    don_hang = get_object_or_404(
        DonHang.objects.select_related('ma_tai_khoan'),
        ma_don_hang=ma_don_hang
    )

    if request.method == 'POST':
        trang_thai_moi = request.POST.get('trang_thai_don_hang', '').strip()
        if trang_thai_moi:
            don_hang.trang_thai_don_hang = trang_thai_moi
            don_hang.save(update_fields=['trang_thai_don_hang'])
        return redirect('chi_tiet_don_hang_admin', ma_don_hang=ma_don_hang)

    chi_tiet_don = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                b.MaBanh,
                b.TenBanh,
                b.HinhAnh,
                ctdh.SoLuong,
                ctdh.DonGia,
                ctdh.ThanhTien
            FROM chitietdonhang ctdh
            INNER JOIN banh b ON ctdh.MaBanh = b.MaBanh
            WHERE ctdh.MaDonHang = %s
            ORDER BY b.MaBanh ASC
        """, [ma_don_hang])
        rows = cursor.fetchall()

    for row in rows:
        chi_tiet_don.append({
            'MaBanh': row[0],
            'TenBanh': row[1],
            'HinhAnh': row[2],
            'SoLuong': row[3],
            'DonGia': float(row[4]) if row[4] is not None else 0,
            'ThanhTien': float(row[5]) if row[5] is not None else 0,
        })

    context = {
        'don_hang': don_hang,
        'chi_tiet_don': chi_tiet_don,
    }
    return render(request, 'app/ChiTietDonHangAdmin.html', context)

# =========================
# KHÁCH - ĐƠN HÀNG
# =========================

def don_hang_cua_toi(request):
    ma_tai_khoan = request.session.get('ma_tai_khoan')
    if not ma_tai_khoan:
        return redirect('login')

    context = get_common_data(request)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                MaDonHang,
                NgayDat,
                TongTien,
                DiaChiGiaoHang,
                TrangThaiDonHang
            FROM donhang
            WHERE MaTaiKhoan = %s
            ORDER BY MaDonHang DESC
        """, [ma_tai_khoan])
        rows = cursor.fetchall()

    don_hangs = []
    for row in rows:
        don_hangs.append({
            'MaDonHang': row[0],
            'NgayDat': row[1],
            'TongTien': float(row[2]) if row[2] is not None else 0,
            'DiaChiGiaoHang': row[3] or '',
            'TrangThaiDonHang': row[4] or 'Chờ xử lý',
        })

    context['don_hangs'] = don_hangs
    return render(request, 'app/DonHangCuaToi.html', context)


def chi_tiet_don_hang(request, ma_don_hang):
    ma_tai_khoan = request.session.get('ma_tai_khoan')
    if not ma_tai_khoan:
        return redirect('login')

    context = get_common_data(request)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                dh.MaDonHang,
                dh.NgayDat,
                dh.TongTien,
                dh.DiaChiGiaoHang,
                dh.TrangThaiDonHang
            FROM donhang dh
            WHERE dh.MaDonHang = %s
              AND dh.MaTaiKhoan = %s
            LIMIT 1
        """, [ma_don_hang, ma_tai_khoan])
        don = cursor.fetchone()

        if not don:
            return redirect('don_hang_cua_toi')

        cursor.execute("""
            SELECT
                b.MaBanh,
                b.TenBanh,
                b.HinhAnh,
                ctdh.SoLuong,
                ctdh.DonGia,
                ctdh.ThanhTien
            FROM chitietdonhang ctdh
            INNER JOIN banh b ON ctdh.MaBanh = b.MaBanh
            WHERE ctdh.MaDonHang = %s
            ORDER BY ctdh.MaBanh DESC
        """, [ma_don_hang])
        rows = cursor.fetchall()

    items = []
    for row in rows:
        hinh_anh = row[2] or ''
        if hinh_anh:
            hinh_anh = str(hinh_anh).strip()
            if hinh_anh.startswith(('http://', 'https://', '/media/', '/static/')):
                pass
            else:
                hinh_anh = f"/static/app/images/{hinh_anh}"
        else:
            hinh_anh = "/static/app/images/no-image.png"

        items.append({
            'MaBanh': row[0],
            'TenBanh': row[1],
            'HinhAnh': hinh_anh,
            'SoLuong': row[3],
            'DonGia': float(row[4]) if row[4] is not None else 0,
            'ThanhTien': float(row[5]) if row[5] is not None else 0,
        })

    don_hang = {
        'MaDonHang': don[0],
        'NgayDat': don[1],
        'TongTien': float(don[2]) if don[2] is not None else 0,
        'DiaChiGiaoHang': don[3] or '',
        'TrangThaiDonHang': don[4] or 'Chờ xử lý',
    }

    context['don_hang'] = don_hang
    context['items'] = items
    return render(request, 'app/ChiTietDonHang.html', context)