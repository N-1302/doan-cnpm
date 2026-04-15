document.addEventListener("DOMContentLoaded", function () {
    const orderList = document.getElementById("thanhtoanOrderList");
    const tongSanPham = document.getElementById("tongSanPhamThanhToan");
    const tamTinh = document.getElementById("tamTinhThanhToan");
    const tongCong = document.getElementById("tongCongThanhToan");
    const phiVanChuyen = document.getElementById("phiVanChuyen");
    const btnDatHang = document.getElementById("btnDatHang");
    const messageBox = document.getElementById("thanhtoanMessage");

    const hoTen = document.getElementById("hoTen");
    const soDienThoai = document.getElementById("soDienThoai");
    const diaChi = document.getElementById("diaChi");
    const ghiChu = document.getElementById("ghiChu");

    let currentSubtotal = 0;
    let currentTotalItems = 0;
    let shippingFee = 0;

    function formatMoney(value) {
        return Number(value).toLocaleString("vi-VN") + " đ";
    }

    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                return cookie.substring(name.length + 1);
            }
        }
        return "";
    }

    function showMessage(text, type = "error") {
        messageBox.textContent = text;
        messageBox.className = "thanhtoan-message " + type;
    }

    async function loadCheckoutData() {
        try {
            orderList.innerHTML = `<div class="thanhtoan-loading">Đang tải đơn hàng...</div>`;

            const response = await fetch("/api/cart/");
            const data = await response.json();

            if (!data.success) {
                orderList.innerHTML = `<div class="thanhtoan-empty">Không tải được đơn hàng</div>`;
                return;
            }

            currentSubtotal = Number(data.subtotal || 0);
            currentTotalItems = Number(data.total_items || 0);

            tongSanPham.textContent = currentTotalItems;
            tamTinh.textContent = formatMoney(currentSubtotal);
            phiVanChuyen.textContent = formatMoney(shippingFee);
            tongCong.textContent = formatMoney(currentSubtotal + shippingFee);

            if (!data.items || data.items.length === 0) {
                orderList.innerHTML = `
                    <div class="thanhtoan-empty">
                        Giỏ hàng của bạn đang trống
                    </div>
                `;
                btnDatHang.disabled = true;
                btnDatHang.style.opacity = "0.6";
                btnDatHang.style.cursor = "not-allowed";
                return;
            }

            let html = "";

            data.items.forEach(item => {
                html += `
                    <div class="thanhtoan-order-item">
                        <div class="thanhtoan-order-image">
                            <img src="${item.hinh_anh}" alt="${item.ten_banh}">
                        </div>

                        <div class="thanhtoan-order-info">
                            <h4 class="thanhtoan-order-name">${item.ten_banh}</h4>
                            <p class="thanhtoan-order-meta">Số lượng: ${item.so_luong}</p>
                            <div class="thanhtoan-order-price">${formatMoney(item.thanh_tien)}</div>
                        </div>
                    </div>
                `;
            });

            orderList.innerHTML = html;
        } catch (error) {
            console.error(error);
            orderList.innerHTML = `<div class="thanhtoan-empty">Có lỗi xảy ra khi tải đơn hàng</div>`;
        }
    }

    async function datHang() {
        const selectedMethod = document.querySelector('input[name="phuongThucThanhToan"]:checked');

        if (!hoTen.value.trim()) {
            showMessage("Vui lòng nhập họ và tên");
            hoTen.focus();
            return;
        }

        if (!soDienThoai.value.trim()) {
            showMessage("Vui lòng nhập số điện thoại");
            soDienThoai.focus();
            return;
        }

        if (!diaChi.value.trim()) {
            showMessage("Vui lòng nhập địa chỉ giao hàng");
            diaChi.focus();
            return;
        }

        if (!selectedMethod) {
            showMessage("Vui lòng chọn phương thức thanh toán");
            return;
        }

        btnDatHang.disabled = true;
        btnDatHang.textContent = "ĐANG XỬ LÝ...";

        try {
            const response = await fetch("/api/dat-hang/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    ho_ten: hoTen.value.trim(),
                    so_dien_thoai: soDienThoai.value.trim(),
                    dia_chi: diaChi.value.trim(),
                    ghi_chu: ghiChu.value.trim(),
                    phuong_thuc_thanh_toan: selectedMethod.value
                })
            });

            const data = await response.json();

            if (data.success) {
                showMessage("Đặt hàng thành công", "success");
                setTimeout(() => {
                    window.location.href = "/gio-hang/";
                }, 1200);
            } else {
                showMessage(data.message || "Đặt hàng thất bại");
            }
        } catch (error) {
            console.error(error);
            showMessage("Có lỗi xảy ra khi đặt hàng");
        } finally {
            btnDatHang.disabled = false;
            btnDatHang.textContent = "ĐẶT HÀNG";
        }
    }

    if (btnDatHang) {
        btnDatHang.addEventListener("click", datHang);
    }

    loadCheckoutData();
});