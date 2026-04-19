document.addEventListener("DOMContentLoaded", function () {
    const thanhtoanOrderList = document.getElementById("thanhtoanOrderList");
    const tongSanPhamEl = document.getElementById("tongSanPhamThanhToan");
    const tamTinhEl = document.getElementById("tamTinhThanhToan");
    const phiVanChuyenEl = document.getElementById("phiVanChuyen");
    const tienGiamGiaEl = document.getElementById("tienGiamGia");
    const tongCongEl = document.getElementById("tongCongThanhToan");
    const btnDatHang = document.getElementById("btnDatHang");
    const thanhtoanMessage = document.getElementById("thanhtoanMessage");
    const saleList = document.getElementById("saleList");
    const khuyenMaiMessage = document.getElementById("khuyenMaiMessage");

    const hoTenInput = document.getElementById("hoTen");
    const soDienThoaiInput = document.getElementById("soDienThoai");
    const diaChiInput = document.getElementById("diaChi");
    const ghiChuInput = document.getElementById("ghiChu");

    const chuyenKhoanBox = document.getElementById("chuyenKhoanBox");
    const viDienTuBox = document.getElementById("viDienTuBox");
    const backToCartBtn = document.querySelector(".thanhtoan-back-btn");

    let khuyenMaiDaApDung = null;

    function formatCurrency(value) {
        return Number(value || 0).toLocaleString("vi-VN") + " đ";
    }

    function parsePrice(value) {
        if (!value) return 0;

        let raw = String(value).trim();
        raw = raw.replace(/đ|vnd|vnđ/gi, "").trim();

        if (/^\d{1,3}(\.\d{3})+$/.test(raw)) {
            return parseInt(raw.replace(/\./g, ""), 10);
        }

        if (/^\d{1,3}(,\d{3})+$/.test(raw)) {
            return parseInt(raw.replace(/,/g, ""), 10);
        }

        return parseInt(raw.replace(/[^\d]/g, ""), 10) || 0;
    }
    
    function isUserLoggedIn() {
        const body = document.body;
        if (!body) return false;

        const value =
            body.dataset.loggedIn ||
            body.dataset.user ||
            body.dataset.userId ||
            "";

        return ["true", "1", "yes"].includes(String(value).trim().toLowerCase()) ||
            (String(value).trim() !== "" &&
             !["false", "0", "none", "null", "undefined"].includes(String(value).trim().toLowerCase()));
    }

    function getCart() {
        try {
            const buyNowItem = JSON.parse(localStorage.getItem("buyNowItem") || "null");
            if (Array.isArray(buyNowItem) && buyNowItem.length > 0) {
                return buyNowItem;
            }

            const cart = JSON.parse(localStorage.getItem("cart") || "[]");
            return Array.isArray(cart) ? cart : [];
        } catch (error) {
            console.error("Lỗi đọc giỏ hàng:", error);
            return [];
        }
    }

    function saveCurrentCheckoutCart(cart) {
        if (Array.isArray(JSON.parse(localStorage.getItem("buyNowItem") || "null"))) {
            localStorage.setItem("buyNowItem", JSON.stringify(cart));
        } else {
            localStorage.setItem("cart", JSON.stringify(cart));
        }
    }

    function clearCart() {
        localStorage.removeItem("cart");
        localStorage.removeItem("buyNowItem");
        window.dispatchEvent(new Event("cartUpdated"));
        document.dispatchEvent(new CustomEvent("cartUpdated"));
    }

    function showMessage(message, type = "error") {
        if (!thanhtoanMessage) return;
        thanhtoanMessage.textContent = message;
        thanhtoanMessage.classList.remove("success", "error");
        thanhtoanMessage.classList.add(type);
    }

    function showKhuyenMaiMessage(message, type = "error") {
        if (!khuyenMaiMessage) return;
        khuyenMaiMessage.textContent = message;
        khuyenMaiMessage.classList.remove("success", "error");
        khuyenMaiMessage.classList.add(type);
    }

    function tinhPhiVanChuyen(tamTinh) {
        if (tamTinh <= 0) return 0;
        if (tamTinh < 800000) return 30000;
        return 15000;
    }

    function tinhTamTinh(cart) {
        return cart.reduce((sum, item) => {
            return sum + Number(item.gia || 0) * Number(item.soLuong || 0);
        }, 0);
    }

    function getTonKho(item) {
        return Number(
            item.soLuongTon ??
            item.so_luong_ton ??
            item.tonKho ??
            item.stock ??
            0
        );
    }

    function normalizeCart(cart) {
        let changed = false;

        cart = cart
            .map(item => {
                let soLuong = Number(item.soLuong || 1);
                const tonKho = getTonKho(item);

                if (soLuong < 1) {
                    soLuong = 1;
                    changed = true;
                }

                if (tonKho > 0 && soLuong > tonKho) {
                    soLuong = tonKho;
                    changed = true;
                }

                item.soLuong = soLuong;
                return item;
            })
            .filter(item => Number(item.soLuong || 0) > 0);

        if (changed) {
            saveCurrentCheckoutCart(cart);
        }

        return cart;
    }

    function updateSummary(cart) {
        const tongSanPham = cart.reduce((sum, item) => sum + Number(item.soLuong || 0), 0);
        const tamTinh = tinhTamTinh(cart);
        const phiVanChuyen = tinhPhiVanChuyen(tamTinh);
        const tienGiam = khuyenMaiDaApDung ? Number(khuyenMaiDaApDung.tien_giam || 0) : 0;
        const tongCong = Math.max(0, tamTinh - tienGiam + phiVanChuyen);

        if (tongSanPhamEl) tongSanPhamEl.textContent = tongSanPham;
        if (tamTinhEl) tamTinhEl.textContent = formatCurrency(tamTinh);
        if (phiVanChuyenEl) phiVanChuyenEl.textContent = formatCurrency(phiVanChuyen);
        if (tienGiamGiaEl) tienGiamGiaEl.textContent = formatCurrency(tienGiam);
        if (tongCongEl) tongCongEl.textContent = formatCurrency(tongCong);
    }

    function renderOrderList() {
        if (!thanhtoanOrderList) return;

        let cart = getCart();
        cart = normalizeCart(cart);

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
            const tonKho = getTonKho(item);

            return `
                <div class="thanhtoan-order-item">
                    <div class="thanhtoan-order-left">
                        <img
                            src="${item.hinhAnh || ""}"
                            alt="${item.tenBanh || "Sản phẩm"}"
                            class="thanhtoan-order-img"
                            onerror="this.src='/static/app/images/no-image.png'"
                        >
                        <div class="thanhtoan-order-info">
                            <h4>${item.tenBanh || "Sản phẩm"}</h4>
                            <span>Số lượng: ${soLuong}</span>
                            ${tonKho > 0 ? `<small>Còn lại: ${tonKho}</small>` : ""}
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

    function addToCart(product, quantity) {
        let cart = normalizeCart(getCart());

        const maBanh = String(product.maBanh || "").trim();
        const tonKho = getStock(product);

        quantity = Number(quantity || 1);
        if (quantity < 1) quantity = 1;

        if (!maBanh) {
            showMessage("Không tìm thấy mã sản phẩm", "error");
            return false;
        }

        if (tonKho <= 0) {
            showMessage("Sản phẩm hiện đã hết hàng", "error");
            return false;
        }

        if (quantity > tonKho) {
            quantity = tonKho;
        }

        const index = cart.findIndex(
            item => String(item.maBanh) === maBanh
        );

        if (index !== -1) {
            const soLuongHienTai = Number(cart[index].soLuong || 0);
            let tongSoLuongMoi = soLuongHienTai + quantity;

            cart[index].soLuongTon = tonKho;
            cart[index].gia = parsePrice(product.gia);
            cart[index].tenBanh = product.tenBanh;
            cart[index].hinhAnh = product.hinhAnh;
            cart[index].noiDung = product.noiDung || cart[index].noiDung || "";

            if (tongSoLuongMoi > tonKho) {
                tongSoLuongMoi = tonKho;
                cart[index].soLuong = tongSoLuongMoi;
                saveCart(cart);
                updateBadge();
                document.dispatchEvent(new CustomEvent("cartUpdated"));
                showMessage(`Sản phẩm chỉ còn ${tonKho} cái trong kho`, "error");
                return false;
            }

            cart[index].soLuong = tongSoLuongMoi;
        } else {
            cart.push({
                maBanh: maBanh,
                tenBanh: product.tenBanh,
                gia: parsePrice(product.gia),
                hinhAnh: product.hinhAnh,
                soLuong: quantity,
                soLuongTon: tonKho,
                noiDung: product.noiDung || ""
            });
        }

        cart = normalizeCart(cart);
        saveCart(cart);
        updateBadge();
        document.dispatchEvent(new CustomEvent("cartUpdated"));
        return true;
    }
    
    function validateForm() {
        let cart = getCart();
        cart = normalizeCart(cart);

        if (!isUserLoggedIn()) return "Vui lòng đăng nhập để đặt hàng.";
        if (cart.length === 0) return "Giỏ hàng đang trống.";
        if (!hoTenInput || !hoTenInput.value.trim()) return "Vui lòng nhập họ và tên.";
        if (!soDienThoaiInput || !soDienThoaiInput.value.trim()) return "Vui lòng nhập số điện thoại.";
        if (!diaChiInput || !diaChiInput.value.trim()) return "Vui lòng nhập địa chỉ giao hàng.";

        const soDienThoai = soDienThoaiInput.value.trim();
        if (!/^(0|\+84)[0-9]{9,10}$/.test(soDienThoai)) {
            return "Số điện thoại không hợp lệ.";
        }

        for (const item of cart) {
            const tonKho = getTonKho(item);
            const soLuong = Number(item.soLuong || 0);

            if (tonKho > 0 && soLuong > tonKho) {
                return `Sản phẩm "${item.tenBanh}" chỉ còn ${tonKho} cái trong kho.`;
            }
        }

        return "";
    }

    async function apDungKhuyenMaiTheoMa(maGiamGia) {
        let cart = getCart();
        cart = normalizeCart(cart);
        const tamTinh = tinhTamTinh(cart);

        try {
            const response = await fetch("/api/kiem-tra-khuyen-mai/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": typeof csrftoken !== "undefined" ? csrftoken : ""
                },
                body: JSON.stringify({
                    ma_giam_gia: maGiamGia,
                    tam_tinh: tamTinh
                })
            });

            const result = await response.json();

            if (result.success) {
                khuyenMaiDaApDung = {
                    ...result,
                    ma_giam_gia: maGiamGia
                };
                showKhuyenMaiMessage(
                    `🎉 Bạn đã tiết kiệm được ${formatCurrency(result.tien_giam)}`,
                    "success"
                );
            } else {
                khuyenMaiDaApDung = null;
                showKhuyenMaiMessage(result.message || "Không áp dụng được mã giảm giá", "error");
            }

            updateSummary(cart);
        } catch (error) {
            console.error(error);
            khuyenMaiDaApDung = null;
            showKhuyenMaiMessage("Có lỗi xảy ra khi kiểm tra mã giảm giá", "error");
            updateSummary(cart);
        }
    }

    async function loadDanhSachKhuyenMai() {
        if (!saleList) return;

        try {
            const response = await fetch("/api/danh-sach-khuyen-mai/");
            const result = await response.json();

            if (!result.success || !Array.isArray(result.items) || result.items.length === 0) {
                saleList.innerHTML = `<div class="thanhtoan-empty">Hiện chưa có mã giảm giá</div>`;
                return;
            }

            saleList.innerHTML = result.items.map(item => `
                <div class="sale-item">
                    <div class="sale-item-left">
                        <strong>${item.ten_khuyen_mai || item.ma_giam_gia}</strong>
                        <span>Mã: ${item.ma_giam_gia}</span>
                        <small>Giảm ${item.phan_tram_giam}%${item.dieu_kien_ap_dung ? " • Đơn từ " + Number(item.dieu_kien_ap_dung).toLocaleString("vi-VN") + " đ" : ""}</small>
                    </div>
                    <button type="button" class="sale-select-btn" data-code="${item.ma_giam_gia}">
                        Chọn
                    </button>
                </div>
            `).join("");

            saleList.querySelectorAll(".sale-select-btn").forEach(btn => {
                btn.addEventListener("click", function () {
                    const code = this.getAttribute("data-code");
                    apDungKhuyenMaiTheoMa(code);
                });
            });
        } catch (error) {
            console.error(error);
            saleList.innerHTML = `<div class="thanhtoan-empty">Không tải được mã giảm giá</div>`;
        }
    }

    async function submitOrder() {
        const error = validateForm();
        if (error) {
            showMessage(error, "error");
            renderOrderList();
            return;
        }

        let cart = getCart();
        cart = normalizeCart(cart);

        for (const item of cart) {
            const tonKho = getTonKho(item);
            const soLuong = Number(item.soLuong || 0);

            if (tonKho > 0 && soLuong > tonKho) {
                showMessage(`Sản phẩm "${item.tenBanh}" chỉ còn ${tonKho} cái trong kho.`, "error");
                renderOrderList();
                return;
            }
        }

        const phuongThucThanhToan =
            document.querySelector('input[name="phuongThucThanhToan"]:checked')?.value || "COD";

        const viDienTu =
            document.querySelector('input[name="viDienTu"]:checked')?.value || "";

        const payload = {
            ho_ten: hoTenInput.value.trim(),
            so_dien_thoai: soDienThoaiInput.value.trim(),
            dia_chi: diaChiInput.value.trim(),
            ghi_chu: ghiChuInput ? ghiChuInput.value.trim() : "",
            phuong_thuc_thanh_toan: phuongThucThanhToan,
            vi_dien_tu: phuongThucThanhToan === "Ví điện tử" ? viDienTu : "",
            ma_giam_gia: khuyenMaiDaApDung ? khuyenMaiDaApDung.ma_giam_gia : "",
            cart: cart.map(item => ({
                ma_banh: Number(item.maBanh || 0),
                so_luong: Number(item.soLuong || 0)
            }))
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
                clearCart();
                khuyenMaiDaApDung = null;

                btnDatHang.classList.remove("is-loading");
                btnDatHang.classList.add("is-success");
                btnDatHang.textContent = "ĐẶT HÀNG THÀNH CÔNG";

                setTimeout(() => {
                    window.location.href = "/gio-hang/";
                }, 1800);
            } else {
                showMessage(result.message || "Đặt hàng thất bại.", "error");
                renderOrderList();
                btnDatHang.disabled = false;
                btnDatHang.classList.remove("is-loading", "is-success");
                btnDatHang.textContent = oldText;
            }
        } catch (error) {
            console.error(error);
            showMessage("Có lỗi xảy ra khi gửi đơn hàng.", "error");
            renderOrderList();
            btnDatHang.disabled = false;
            btnDatHang.classList.remove("is-loading", "is-success");
            btnDatHang.textContent = oldText;
        }
    }

    document.querySelectorAll('input[name="phuongThucThanhToan"]').forEach(radio => {
        radio.addEventListener("change", togglePaymentBoxes);
    });

    backToCartBtn?.addEventListener("click", function () {
        localStorage.removeItem("buyNowItem");
    });

    if (btnDatHang) {
        btnDatHang.addEventListener("click", submitOrder);
    }

    if (!isUserLoggedIn()) {
        showMessage("Vui lòng đăng nhập để thanh toán.", "error");
    }

    togglePaymentBoxes();
    renderOrderList();
    loadDanhSachKhuyenMai();
});