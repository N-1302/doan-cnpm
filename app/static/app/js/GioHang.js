document.addEventListener("DOMContentLoaded", function () {
    const gioHangTableBody = document.getElementById("gioHangTableBody");
    const gioHangEmpty = document.getElementById("gioHangEmpty");
    const tongSanPhamEl = document.getElementById("tongSanPham");
    const tamTinhEl = document.getElementById("tamTinh");
    const phiVanChuyenEl = document.getElementById("phiVanChuyen");
    const tongCongEl = document.getElementById("tongCong");
    const btnThanhToan = document.getElementById("btnThanhToan");

    function parsePrice(value) {
        if (value === null || value === undefined) return 0;

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

    function formatCurrency(value) {
        return parsePrice(value).toLocaleString("vi-VN") + " đ";
    }

    function tinhPhiVanChuyen(tamTinh) {
        if (tamTinh <= 0) return 0;
        if (tamTinh < 800000) return 30000;
        return 15000;
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
            (
                String(value).trim() !== "" &&
                !["false", "0", "none", "null", "undefined"].includes(String(value).trim().toLowerCase())
            );
    }

    function getCart() {
        try {
            const cart = JSON.parse(localStorage.getItem("cart") || "[]");
            return Array.isArray(cart) ? cart : [];
        } catch (error) {
            console.error("Lỗi đọc giỏ hàng:", error);
            return [];
        }
    }

    function saveCart(cart) {
        localStorage.setItem("cart", JSON.stringify(cart));
        window.dispatchEvent(new Event("cartUpdated"));
        document.dispatchEvent(new CustomEvent("cartUpdated"));
    }

    function getTonKho(item) {
        const tonKho = Number(
            item.soLuongTon ??
            item.so_luong_ton ??
            item.tonKho ??
            item.stock ??
            0
        );
        return tonKho > 0 ? tonKho : 0;
    }

    function normalizeCart(cart) {
        let changed = false;

        cart = cart.map(item => {
            let soLuong = Number(item.soLuong || 1);
            const tonKho = getTonKho(item);

            item.gia = parsePrice(item.gia);

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
        });

        if (changed) {
            localStorage.setItem("cart", JSON.stringify(cart));
        }

        return cart;
    }

    function updateSummary(cart) {
        const tongSanPham = cart.reduce((sum, item) => sum + Number(item.soLuong || 0), 0);
        const tamTinh = cart.reduce((sum, item) => {
            return sum + parsePrice(item.gia) * Number(item.soLuong || 0);
        }, 0);
        const phiVanChuyen = tinhPhiVanChuyen(tamTinh);
        const tongCong = tamTinh + phiVanChuyen;

        if (tongSanPhamEl) tongSanPhamEl.textContent = tongSanPham;
        if (tamTinhEl) tamTinhEl.textContent = formatCurrency(tamTinh);
        if (phiVanChuyenEl) phiVanChuyenEl.textContent = formatCurrency(phiVanChuyen);
        if (tongCongEl) tongCongEl.textContent = formatCurrency(tongCong);
    }

    function renderEmptyTable() {
        if (!gioHangTableBody) return;

        gioHangTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="giohang-loading">Giỏ hàng của bạn đang trống</td>
            </tr>
        `;
    }

    function renderCart() {
        if (!gioHangTableBody) return;

        let cart = getCart();
        cart = normalizeCart(cart);

        if (cart.length === 0) {
            renderEmptyTable();
            if (gioHangEmpty) gioHangEmpty.style.display = "block";
            updateSummary([]);
            return;
        }

        if (gioHangEmpty) gioHangEmpty.style.display = "none";

        gioHangTableBody.innerHTML = cart.map((item, index) => {
            const gia = parsePrice(item.gia);
            const soLuong = Number(item.soLuong || 1);
            const thanhTien = gia * soLuong;
            const tonKho = getTonKho(item);
            const hetTon = tonKho > 0 && soLuong >= tonKho;

            return `
                <tr>
                    <td>
                        <div class="giohang-product">
                            <img
                                src="${item.hinhAnh || ''}"
                                alt="${item.tenBanh || 'Sản phẩm'}"
                                class="giohang-product-img"
                                onerror="this.src='/static/app/images/no-image.png'"
                            >
                            <div class="giohang-product-info">
                                <h4>${item.tenBanh || 'Sản phẩm'}</h4>
                                ${item.noiDung ? `<p>${item.noiDung}</p>` : ""}
                                ${tonKho > 0 ? `<small>Còn lại: ${tonKho}</small>` : ""}
                            </div>
                        </div>
                    </td>

                    <td class="giohang-price">
                        ${formatCurrency(gia)}
                    </td>

                    <td>
                        <div class="giohang-qty-box">
                            <button type="button" class="giohang-qty-btn qty-minus" data-index="${index}">-</button>
                            <span class="giohang-qty-number">${soLuong}</span>
                            <button type="button" class="giohang-qty-btn qty-plus" data-index="${index}" ${hetTon ? "disabled" : ""}>+</button>
                        </div>
                    </td>

                    <td class="giohang-total">
                        ${formatCurrency(thanhTien)}
                    </td>

                    <td class="giohang-remove-cell">
                        <button type="button" class="giohang-remove-btn" data-index="${index}">×</button>
                    </td>
                </tr>
            `;
        }).join("");

        bindEvents();
        updateSummary(cart);
    }

    function bindEvents() {
        document.querySelectorAll(".qty-minus").forEach(button => {
            button.addEventListener("click", function () {
                const index = Number(this.dataset.index);
                const cart = getCart();

                if (!cart[index]) return;

                if (Number(cart[index].soLuong || 1) > 1) {
                    cart[index].soLuong = Number(cart[index].soLuong || 1) - 1;
                } else {
                    cart.splice(index, 1);
                }

                saveCart(cart);
                renderCart();
            });
        });

        document.querySelectorAll(".qty-plus").forEach(button => {
            button.addEventListener("click", function () {
                const index = Number(this.dataset.index);
                const cart = getCart();

                if (!cart[index]) return;

                const tonKho = getTonKho(cart[index]);
                let soLuongMoi = Number(cart[index].soLuong || 1) + 1;

                if (tonKho > 0 && soLuongMoi > tonKho) {
                    alert(`Sản phẩm chỉ còn ${tonKho} cái trong kho`);
                    soLuongMoi = tonKho;
                }

                cart[index].soLuong = soLuongMoi;
                saveCart(cart);
                renderCart();
            });
        });

        document.querySelectorAll(".giohang-remove-btn").forEach(button => {
            button.addEventListener("click", function () {
                const index = Number(this.dataset.index);
                const cart = getCart();

                if (!cart[index]) return;

                cart.splice(index, 1);
                saveCart(cart);
                renderCart();
            });
        });
    }

    if (btnThanhToan) {
        btnThanhToan.addEventListener("click", function () {
            const cart = getCart();

            if (cart.length === 0) {
                alert("Giỏ hàng của bạn đang trống.");
                return;
            }

            if (!isUserLoggedIn()) {
                alert("Vui lòng đăng nhập để thanh toán.");
                window.location.href = "/login/";
                return;
            }

            localStorage.removeItem("buyNowItem");
            window.location.href = "/thanh-toan/";
        });
    }

    renderCart();
});