from django.db import models


class PhanQuyen(models.Model):
    ma_quyen = models.AutoField(primary_key=True, db_column='MaQuyen')
    ten_quyen = models.CharField(max_length=50, db_column='TenQuyen')

    class Meta:
        managed = False
        db_table = 'phanquyen'

    def __str__(self):
        return self.ten_quyen


class TaiKhoan(models.Model):
    ma_tai_khoan = models.AutoField(primary_key=True, db_column='MaTaiKhoan')
    ten_dang_nhap = models.CharField(max_length=50, unique=True, db_column='TenDangNhap')
    mat_khau = models.CharField(max_length=255, db_column='MatKhau')
    email = models.CharField(max_length=100, unique=True, db_column='Email')
    otp = models.CharField(max_length=10, null=True, blank=True, db_column='OTP')
    otp_date_send = models.DateTimeField(null=True, blank=True, db_column='OTPDateSend')
    date_create = models.DateTimeField(null=True, blank=True, db_column='DateCreate')
    ma_quyen = models.ForeignKey(
        PhanQuyen,
        on_delete=models.DO_NOTHING,
        db_column='MaQuyen',
        null=True,
        blank=True
    )
    ho_ten = models.CharField(max_length=100, db_column='HoTen')
    sdt = models.CharField(max_length=15, null=True, blank=True, db_column='SDT')
    gioi_tinh = models.CharField(max_length=10, null=True, blank=True, db_column='GioiTinh')
    random_key = models.CharField(max_length=100, null=True, blank=True, db_column='RandomKey')

    class Meta:
        managed = False
        db_table = 'taikhoan'

    def __str__(self):
        return self.ten_dang_nhap


class LoaiBanh(models.Model):
    ma_loai_banh = models.AutoField(primary_key=True, db_column='MaLoaiBanh')
    ten_loai_banh = models.CharField(max_length=100, db_column='TenLoaiBanh')
    mo_ta = models.TextField(null=True, blank=True, db_column='MoTa')

    class Meta:
        managed = False
        db_table = 'loaibanh'

    def __str__(self):
        return self.ten_loai_banh


class Banh(models.Model):
    ma_banh = models.AutoField(primary_key=True, db_column='MaBanh')
    ten_banh = models.CharField(max_length=100, db_column='TenBanh')
    hinh_anh = models.CharField(max_length=255, null=True, blank=True, db_column='HinhAnh')
    gia = models.DecimalField(max_digits=10, decimal_places=2, db_column='Gia')
    so_luong_ton = models.IntegerField(default=0, db_column='SoLuongTon')
    mo_ta = models.TextField(null=True, blank=True, db_column='MoTa')
    trang_thai = models.CharField(max_length=50, null=True, blank=True, db_column='TrangThai')
    ma_loai_banh = models.ForeignKey(
        LoaiBanh,
        on_delete=models.DO_NOTHING,
        db_column='MaLoaiBanh',
        null=True,
        blank=True
    )

    class Meta:
        managed = False
        db_table = 'banh'

    def __str__(self):
        return self.ten_banh


class KhuyenMai(models.Model):
    ma_khuyen_mai = models.AutoField(primary_key=True, db_column='MaKhuyenMai')
    ten_khuyen_mai = models.CharField(max_length=100, db_column='TenKhuyenMai')
    ma_giam_gia = models.CharField(max_length=50, null=True, blank=True, db_column='MaGiamGia')
    phan_tram_giam = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, db_column='PhanTramGiam')
    ngay_bat_dau = models.DateTimeField(null=True, blank=True, db_column='NgayBatDau')
    ngay_ket_thuc = models.DateTimeField(null=True, blank=True, db_column='NgayKetThuc')
    dieu_kien_ap_dung = models.TextField(null=True, blank=True, db_column='DieuKienApDung')
    trang_thai = models.CharField(max_length=50, null=True, blank=True, db_column='TrangThai')
    so_luong = models.IntegerField(null=True, blank=True, db_column='SoLuong')

    class Meta:
        managed = False
        db_table = 'khuyenmai'

    def __str__(self):
        return self.ten_khuyen_mai


class GioHang(models.Model):
    ma_gio_hang = models.AutoField(primary_key=True, db_column='MaGioHang')
    ma_tai_khoan = models.ForeignKey(
        TaiKhoan,
        on_delete=models.DO_NOTHING,
        db_column='MaTaiKhoan',
        null=True,
        blank=True
    )
    ngay_tao = models.DateTimeField(null=True, blank=True, db_column='NgayTao')
    trang_thai_gio_hang = models.CharField(max_length=50, null=True, blank=True, db_column='TrangThaiGioHang')

    class Meta:
        managed = False
        db_table = 'giohang'

    def __str__(self):
        return f"GioHang {self.ma_gio_hang}"


class ChiTietGioHang(models.Model):
    ma_gio_hang = models.ForeignKey(
        GioHang,
        on_delete=models.DO_NOTHING,
        db_column='MaGioHang'
    )
    ma_banh = models.ForeignKey(
        Banh,
        on_delete=models.DO_NOTHING,
        db_column='MaBanh'
    )
    so_luong = models.IntegerField(db_column='SoLuong')
    don_gia = models.DecimalField(max_digits=10, decimal_places=2, db_column='DonGia')
    thanh_tien = models.DecimalField(max_digits=10, decimal_places=2, db_column='ThanhTien')

    class Meta:
        managed = False
        db_table = 'chitietgiohang'
        unique_together = (('ma_gio_hang', 'ma_banh'),)

    def __str__(self):
        return f"{self.ma_gio_hang_id} - {self.ma_banh_id}"


class DonHang(models.Model):
    ma_don_hang = models.AutoField(primary_key=True, db_column='MaDonHang')
    ma_tai_khoan = models.ForeignKey(
        TaiKhoan,
        on_delete=models.DO_NOTHING,
        db_column='MaTaiKhoan',
        null=True,
        blank=True
    )
    ma_khuyen_mai = models.ForeignKey(
        KhuyenMai,
        on_delete=models.DO_NOTHING,
        db_column='MaKhuyenMai',
        null=True,
        blank=True
    )
    ngay_dat = models.DateTimeField(null=True, blank=True, db_column='NgayDat')
    tong_tien = models.DecimalField(max_digits=10, decimal_places=2, db_column='TongTien')
    dia_chi_giao_hang = models.CharField(max_length=255, db_column='DiaChiGiaoHang')
    trang_thai_don_hang = models.CharField(max_length=50, null=True, blank=True, db_column='TrangThaiDonHang')

    class Meta:
        managed = False
        db_table = 'donhang'

    def __str__(self):
        return f"DonHang {self.ma_don_hang}"


class ChiTietDonHang(models.Model):
    ma_don_hang = models.ForeignKey(
        DonHang,
        on_delete=models.DO_NOTHING,
        db_column='MaDonHang'
    )
    ma_banh = models.ForeignKey(
        Banh,
        on_delete=models.DO_NOTHING,
        db_column='MaBanh'
    )
    so_luong = models.IntegerField(db_column='SoLuong')
    don_gia = models.DecimalField(max_digits=10, decimal_places=2, db_column='DonGia')
    thanh_tien = models.DecimalField(max_digits=10, decimal_places=2, db_column='ThanhTien')

    class Meta:
        managed = False
        db_table = 'chitietdonhang'
        unique_together = (('ma_don_hang', 'ma_banh'),)

    def __str__(self):
        return f"{self.ma_don_hang_id} - {self.ma_banh_id}"


class DanhGia(models.Model):
    ma_danh_gia = models.AutoField(primary_key=True, db_column='MaDanhGia')
    ma_tai_khoan = models.ForeignKey(
        TaiKhoan,
        on_delete=models.DO_NOTHING,
        db_column='MaTaiKhoan',
        null=True,
        blank=True
    )
    ma_banh = models.ForeignKey(
        Banh,
        on_delete=models.DO_NOTHING,
        db_column='MaBanh',
        null=True,
        blank=True
    )
    so_sao = models.IntegerField(db_column='SoSao')
    noi_dung = models.TextField(null=True, blank=True, db_column='NoiDung')

    class Meta:
        managed = False
        db_table = 'danhgia'

    def __str__(self):
        return f"DanhGia {self.ma_danh_gia}"


class LienHe(models.Model):
    ma_lien_he = models.AutoField(primary_key=True, db_column='MaLienHe')
    ma_tai_khoan = models.ForeignKey(
        TaiKhoan,
        on_delete=models.DO_NOTHING,
        db_column='MaTaiKhoan',
        null=True,
        blank=True
    )
    ho_ten = models.CharField(max_length=100, db_column='HoTen')
    email = models.CharField(max_length=100, db_column='Email')
    so_dien_thoai = models.CharField(max_length=15, null=True, blank=True, db_column='SoDienThoai')
    noi_dung = models.TextField(db_column='NoiDung')
    ngay_gui = models.DateTimeField(null=True, blank=True, db_column='NgayGui')
    trang_thai_xu_ly = models.CharField(max_length=50, null=True, blank=True, db_column='TrangThaiXuLy')

    class Meta:
        managed = False
        db_table = 'lienhe'

    def __str__(self):
        return self.ho_ten


class ChatBox(models.Model):
    ma_tin_nhan = models.AutoField(primary_key=True, db_column='MaTinNhan')
    noi_dung = models.TextField(db_column='NoiDung')
    thoi_gian_gui = models.DateTimeField(null=True, blank=True, db_column='ThoiGianGui')
    nguoi_gui = models.CharField(max_length=100, null=True, blank=True, db_column='NguoiGui')
    trang_thai_doc = models.CharField(max_length=50, null=True, blank=True, db_column='TrangThaiDoc')

    class Meta:
        managed = False
        db_table = 'chatbox'

    def __str__(self):
        return f"TinNhan {self.ma_tin_nhan}"


class ThanhToan(models.Model):
    ma_thanh_toan = models.AutoField(primary_key=True, db_column='MaThanhToan')
    ma_don_hang = models.OneToOneField(
        DonHang,
        on_delete=models.DO_NOTHING,
        db_column='MaDonHang',
        null=True,
        blank=True
    )
    phuong_thuc = models.CharField(max_length=50, null=True, blank=True, db_column='PhuongThuc')
    trang_thai = models.CharField(max_length=50, null=True, blank=True, db_column='TrangThai')

    class Meta:
        managed = False
        db_table = 'thanhtoan'

    def __str__(self):
        return f"ThanhToan {self.ma_thanh_toan}"


class VanChuyen(models.Model):
    ma_van_chuyen = models.AutoField(primary_key=True, db_column='MaVanChuyen')
    ma_don_hang = models.OneToOneField(
        DonHang,
        on_delete=models.DO_NOTHING,
        db_column='MaDonHang',
        null=True,
        blank=True
    )
    phuong_thuc = models.CharField(max_length=50, null=True, blank=True, db_column='PhuongThuc')
    phi_ship = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='PhiShip')

    class Meta:
        managed = False
        db_table = 'vanchuyen'

    def __str__(self):
        return f"VanChuyen {self.ma_van_chuyen}"