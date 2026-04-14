from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Create your models here.
#  Thao tác để tạo các bảng csdl trong đây nha 
# tạo bảng danh mục sản phẩm, bảng sản phẩm, bảng đơn hàng, bảng chi tiết đơn hàng, bảng địa chỉ giao hàng category, product, order, order item, shipping address

class Category(models.Model):
    sub_category = models.ForeignKey('self', on_delete=models.CASCADE, related_name='sub_categorys', null=True, blank=True)
    is_sub = models.BooleanField(default=False)
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200,unique=True)
    def __str__(self):
        return self.name
 
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name','last_name', 'password1', 'password2']

class Sanpham(models.Model):
    category = models.ManyToManyField(Category, related_name='sanpham')
    name = models.CharField(max_length=200, null=True)
    price = models.FloatField()
    digital = models.BooleanField(default=False, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)
    detail = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.name
    @property
    def ImageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

class Donhang(models.Model):
    khachhang= models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)
    @property
    def get_cart_items(self):
        donhangsanpham = self.donhangsanpham_set.all()
        total = sum([item.quantity for item in donhangsanpham])
        return total
    @property
    def get_cart_total(self):
        donhangsanpham = self.donhangsanpham_set.all()
        total = sum([item.get_total for item in donhangsanpham])
        return total
class Donhangsanpham(models.Model):
    sanpham = models.ForeignKey(Sanpham, on_delete=models.SET_NULL, blank=True, null=True)
    donhang = models.ForeignKey(Donhang, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    @property
    def get_total(self):
        total = self.sanpham.price * self.quantity
        return total

class Diachi(models.Model):
    khachhang = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    donhang = models.ForeignKey(Donhang, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address