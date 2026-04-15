document.addEventListener("DOMContentLoaded", function () {
    const thanhtoanOrderList = document.getElementById("thanhtoanOrderList");
    const tongSanPhamEl = document.getElementById("tongSanPhamThanhToan");
    const tamTinhEl = document.getElementById("tamTinhThanhToan");
    const phiVanChuyenEl = document.getElementById("phiVanChuyen");
    const tongCongEl = document.getElementById("tongCongThanhToan");
    const btnDatHang = document.getElementById("btnDatHang");
    const thanhtoanMessage = document.getElementById("thanhtoanMessage");

    const hoTenInput = document.getElementById("hoTen");
    const soDienThoaiInput = document.getElementById("soDienThoai");
    const diaChiInput = document.getElementById("diaChi");
    const ghiChuInput = document.getElementById("ghiChu");

    const chuyenKhoanBox = document.getElementById("chuyenKhoanBox");
    const viDienTuBox = document.getElementById("viDienTuBox");

    function formatCurrency(value) {
        return Number(value || 0).toLocaleString("vi-VN") + " đ";
    }

    function getCart() {
        try {
            return JSON.parse(localStorage.getItem("cart")) || [];
        } catch (error) {
            console.error("Lỗi đọc giỏ hàng:", error);
            return [];
        }
    }

    function showMessage(message, type = "error") {
        if (!thanhtoanMessage) return;
        thanhtoanMessage.textContent = message;
        thanhtoanMessage.classList.remove("success", "error");
        thanhtoanMessage.classList.add(type);
    }

    function updateSummary(cart) {
        const tongSanPham = cart.reduce((sum, item) => sum + Number(item.soLuong || 0), 0);
        const tamTinh = cart.reduce((sum, item) => {
            return sum + Number(item.gia || 0) * Number(item.soLuong || 0);
        }, 0);
        const phiVanChuyen = 0;
        const tongCong = tamTinh + phiVanChuyen;

        if (tongSanPhamEl) tongSanPhamEl.textContent = tongSanPham;
        if (tamTinhEl) tamTinhEl.textContent = formatCurrency(tamTinh);
        if (phiVanChuyenEl) phiVanChuyenEl.textContent = formatCurrency(phiVanChuyen);
        if (tongCongEl) tongCongEl.textContent = formatCurrency(tongCong);
    }

    function renderOrderList() {
        const cart = getCart();

        if (!thanhtoanOrderList) return;

        if (cart.length === 0) {
            thanhtoanOrderList.innerHTML = `
                <div class="thanhtoan-empty">Chưa có sản phẩm trong đơn hàng</div>
            `;
            updateSummary([]);
            return;
        }

        thanhtoanOrderList.innerHTML = cart.map(item => {
            const soLuong = Number(item.soLuong || 0);
            const gia = Number(item.gia || 0);
            const thanhTien = soLuong * gia;

            return `
                <div class="thanhtoan-order-item">
                    <div class="thanhtoan-order-left">
                        <img src="${item.hinhAnh || ""}" alt="${item.tenBanh || "Sản phẩm"}" class="thanhtoan-order-img">
                        <div class="thanhtoan-order-info">
                            <h4>${item.tenBanh || "Sản phẩm"}</h4>
                            <span>Số lượng: ${soLuong}</span>
                        </div>
                    </div>
                    <div class="thanhtoan-order-price">
                        ${formatCurrency(thanhTien)}
                    </div>
                </div>
            `;
        }).join("");

        updateSummary(cart);
    }

    function togglePaymentBoxes() {
        const selected = document.querySelector('input[name="phuongThucThanhToan"]:checked')?.value || "COD";

        if (chuyenKhoanBox) {
            chuyenKhoanBox.style.display = selected === "Chuyển khoản" ? "block" : "none";
        }

        if (viDienTuBox) {
            viDienTuBox.style.display = selected === "Ví điện tử" ? "block" : "none";
        }
    }

    function validateForm() {
        const cart = getCart();

        if (cart.length === 0) return "Giỏ hàng đang trống.";
        if (!hoTenInput || !hoTenInput.value.trim()) return "Vui lòng nhập họ và tên.";
        if (!soDienThoaiInput || !soDienThoaiInput.value.trim()) return "Vui lòng nhập số điện thoại.";
        if (!diaChiInput || !diaChiInput.value.trim()) return "Vui lòng nhập địa chỉ giao hàng.";

        const soDienThoai = soDienThoaiInput.value.trim();
        if (!/^(0|\+84)[0-9]{9,10}$/.test(soDienThoai)) {
            return "Số điện thoại không hợp lệ.";
        }

        return "";
    }

    async function submitOrder() {
        const error = validateForm();
        if (error) {
            showMessage(error, "error");
            return;
        }

        const phuongThucThanhToan =
            document.querySelector('input[name="phuongThucThanhToan"]:checked')?.value || "COD";

        const viDienTu =
            document.querySelector('input[name="viDienTu"]:checked')?.value || "";

        const payload = {
            dia_chi: diaChiInput.value.trim(),
            phuong_thuc_thanh_toan: phuongThucThanhToan,
            vi_dien_tu: phuongThucThanhToan === "Ví điện tử" ? viDienTu : ""
        };

        const oldText = btnDatHang.textContent;
        btnDatHang.disabled = true;
        btnDatHang.classList.add("is-loading");
        btnDatHang.textContent = "ĐANG XỬ LÝ...";

        try {
            const response = await fetch("/api/dat-hang/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": typeof csrftoken !== "undefined" ? csrftoken : ""
                },
                body: JSON.stringify(payload)
            });

            const result = await response.json();

            if (result.success) {
                showMessage(`Đặt hàng thành công. Mã đơn hàng: #${result.ma_don_hang}`, "success");

                localStorage.removeItem("cart");

                btnDatHang.classList.remove("is-loading");
                btnDatHang.classList.add("is-success");
                btnDatHang.textContent = "ĐẶT HÀNG THÀNH CÔNG";

                setTimeout(() => {
                    window.location.href = "/gio-hang/";
                }, 1800);
            } else {
                showMessage(result.message || "Đặt hàng thất bại.", "error");
                btnDatHang.disabled = false;
                btnDatHang.classList.remove("is-loading");
                btnDatHang.classList.remove("is-success");
                btnDatHang.textContent = oldText;
            }
        } catch (error) {
            console.error(error);
            showMessage("Có lỗi xảy ra khi gửi đơn hàng.", "error");
            btnDatHang.disabled = false;
            btnDatHang.classList.remove("is-loading");
            btnDatHang.classList.remove("is-success");
            btnDatHang.textContent = oldText;
        }
    }

    document.querySelectorAll('input[name="phuongThucThanhToan"]').forEach(radio => {
        radio.addEventListener("change", togglePaymentBoxes);
    });

    if (btnDatHang) {
        btnDatHang.addEventListener("click", submitOrder);
    }

    togglePaymentBoxes();
    renderOrderList();
});