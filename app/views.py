from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import TaiKhoan, LoaiBanh, Banh, PhanQuyen
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

def lien_he(request):
    return render(request, 'app/LienHe.html')

def chinh_sach_giao_hang(request):
    return render(request, 'app/ChinhSachGiaoHang.html')

def san_pham(request):
    return render(request, 'app/sanpham.html')

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
        {
            'id': 2,
            'title': 'SPRINTTEAM ra mắt Tiramisu cacao kem mịn cho mùa lễ hội',
            'category': 'san-pham-moi',
            'category_name': 'Sản phẩm mới',
            'date': '05/04/2026',
            'image': 'https://images.unsplash.com/photo-1563729784474-d77dbb933a9e?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Dòng bánh mới lấy cảm hứng từ hương vị Ý, lớp kem mềm mượt và điểm nhấn cacao đậm nhẹ.',
            'buy_now': True,
        },
        {
            'id': 3,
            'title': 'Cách bảo quản bánh kem đúng cách để giữ hương vị trọn vẹn',
            'category': 'kien-thuc-banh',
            'category_name': 'Kiến thức bánh',
            'date': '03/04/2026',
            'image': 'https://images.unsplash.com/photo-1464306076886-debca5e8a6b0?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Bánh kem nên được đặt trong ngăn mát, tránh ánh nắng trực tiếp và hạn chế để gần thực phẩm có mùi mạnh.',
            'buy_now': False,
        },
        {
            'id': 4,
            'title': 'Khách hàng đánh giá cao dòng bánh mousse dâu mới tại SPRINTTEAM',
            'category': 'feedback',
            'category_name': 'Feedback',
            'date': '29/03/2026',
            'image': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Nhiều khách hàng nhận xét bánh có vị thanh nhẹ, hình thức đẹp và phù hợp cho các bữa tiệc nhỏ.',
            'buy_now': False,
        },
        {
            'id': 5,
            'title': 'Combo cuối tuần: Mua 2 bánh nhỏ tặng 1 thức uống',
            'category': 'khuyen-mai',
            'category_name': 'Tin khuyến mãi',
            'date': '27/03/2026',
            'image': 'https://images.unsplash.com/photo-1519864600265-abb23847ef2c?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Ưu đãi dành cho khách mua trực tiếp tại cửa hàng hoặc đặt giao trong nội thành.',
            'buy_now': False,
        },
        {
            'id': 6,
            'title': 'Bộ sưu tập bánh ngọt theo mùa với phong cách trang trí tinh tế',
            'category': 'san-pham-moi',
            'category_name': 'Sản phẩm mới',
            'date': '24/03/2026',
            'image': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Thiết kế nhẹ nhàng, màu sắc thanh lịch và phù hợp cho khách hàng yêu thích phong cách quà tặng cao cấp.',
            'buy_now': True,
        },
        {
            'id': 7,
            'title': 'Phân biệt mousse, tiramisu và chocolate cake cho người mới chọn bánh',
            'category': 'kien-thuc-banh',
            'category_name': 'Kiến thức bánh',
            'date': '01/04/2026',
            'image': 'https://images.unsplash.com/photo-1551024601-bec78aea704b?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Mỗi loại bánh mang một đặc trưng riêng về độ mềm, độ béo và phong cách thưởng thức.',
            'buy_now': False,
        },
        {
            'id': 8,
            'title': 'Nhiều khách hàng chọn SPRINTTEAM cho tiệc sinh nhật gia đình',
            'category': 'feedback',
            'category_name': 'Feedback',
            'date': '20/03/2026',
            'image': 'https://images.unsplash.com/photo-1571115764595-644a1f56a55c?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Bánh được đánh giá cao ở độ chỉn chu, giao hàng đúng giờ và hương vị vừa miệng.',
            'buy_now': False,
        },
        {
            'id': 9,
            'title': 'Ưu đãi nhập mã SPRINT10 giảm ngay 10% cho đơn online',
            'category': 'khuyen-mai',
            'category_name': 'Tin khuyến mãi',
            'date': '18/03/2026',
            'image': 'https://images.unsplash.com/photo-1559622214-f8a9850965bb?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Áp dụng cho đơn từ 250.000đ, mỗi tài khoản được sử dụng một lần.',
            'buy_now': False,
        },
        {
            'id': 10,
            'title': 'Ra mắt bánh chocolate phủ hạt giòn nhẹ',
            'category': 'san-pham-moi',
            'category_name': 'Sản phẩm mới',
            'date': '15/03/2026',
            'image': 'https://images.unsplash.com/photo-1606890737304-57a1ca8a5b62?auto=format&fit=crop&w=1000&q=80',
            'desc': 'Hương chocolate đậm đà, phù hợp cho khách hàng yêu vị ngọt sâu.',
            'buy_now': True,
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