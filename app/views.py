from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import TaiKhoan, LoaiBanh, Banh, PhanQuyen


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
    context = get_common_data(request)
    ma_loai = request.GET.get('category')

    if ma_loai:
        context['products'] = Banh.objects.filter(ma_loai_banh_id=ma_loai)

    context['active_category'] = ma_loai
    return render(request, 'app/category.html', context)


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

        if not ho_ten or not ten_dang_nhap or not mat_khau or not email:
            return render(request, 'app/register.html', {
                'loi': 'Vui lòng nhập đầy đủ thông tin bắt buộc'
            })

        if TaiKhoan.objects.filter(ten_dang_nhap=ten_dang_nhap).exists():
            return render(request, 'app/register.html', {
                'loi': 'Tên đăng nhập đã tồn tại'
            })

        if TaiKhoan.objects.filter(email=email).exists():
            return render(request, 'app/register.html', {
                'loi': 'Email đã tồn tại'
            })

        TaiKhoan.objects.create(
            ho_ten=ho_ten,
            ten_dang_nhap=ten_dang_nhap,
            mat_khau=mat_khau,
            email=email,
            sdt=sdt,
            ma_quyen_id=2  # User
        )

        return redirect('login')

    return render(request, 'app/register.html')


def loginPage(request):
    if request.session.get('ma_tai_khoan'):
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            tai_khoan = TaiKhoan.objects.get(
                ten_dang_nhap=username,
                mat_khau=password
            )

            request.session['ma_tai_khoan'] = tai_khoan.ma_tai_khoan
            request.session['ten_dang_nhap'] = tai_khoan.ten_dang_nhap
            request.session['ma_quyen'] = tai_khoan.ma_quyen_id if tai_khoan.ma_quyen else None

            if tai_khoan.ma_quyen_id == 1:
                return redirect('admin_dashboard')

            return redirect('home')

        except TaiKhoan.DoesNotExist:
            return render(request, 'app/login.html', {
                'loi': 'Sai tên đăng nhập hoặc mật khẩu'
            })

    return render(request, 'app/login.html')


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
    return render(request, 'app/admin_dashboard.html', context)