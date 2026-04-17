document.addEventListener("DOMContentLoaded", function () {
    const gioHangTableBody = document.getElementById("gioHangTableBody");
    const gioHangEmpty = document.getElementById("gioHangEmpty");
    const tongSanPhamEl = document.getElementById("tongSanPham");
    const tamTinhEl = document.getElementById("tamTinh");
    const phiVanChuyenEl = document.getElementById("phiVanChuyen");
    const tongCongEl = document.getElementById("tongCong");
    const btnThanhToan = document.getElementById("btnThanhToan");

    function formatCurrency(value) {
        return Number(value || 0).toLocaleString("vi-VN") + " đ";
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
            (String(value).trim() !== "" &&
             !["false", "0", "none", "null", "undefined"].includes(String(value).trim().toLowerCase()));
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
    }

    function updateSummary(cart) {
        const tongSanPham = cart.reduce((sum, item) => sum + Number(item.soLuong || 0), 0);
        const tamTinh = cart.reduce((sum, item) => {
            return sum + Number(item.gia || 0) * Number(item.soLuong || 0);
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

        const cart = getCart();

        if (cart.length === 0) {
            renderEmptyTable();
            if (gioHangEmpty) gioHangEmpty.style.display = "block";
            updateSummary([]);
            return;
        }

        if (gioHangEmpty) gioHangEmpty.style.display = "none";

        gioHangTableBody.innerHTML = cart.map((item, index) => {
            const gia = Number(item.gia || 0);
            const soLuong = Number(item.soLuong || 1);
            const thanhTien = gia * soLuong;

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
                            <button type="button" class="giohang-qty-btn qty-plus" data-index="${index}">+</button>
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

                cart[index].soLuong = Number(cart[index].soLuong || 1) + 1;
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

            window.location.href = "/thanh-toan/";
        });
    }

    renderCart();
});