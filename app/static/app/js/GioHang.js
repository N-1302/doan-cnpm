document.addEventListener("DOMContentLoaded", function () {
    const gioHangTableBody = document.getElementById("gioHangTableBody");
    const gioHangEmpty = document.getElementById("gioHangEmpty");
    const tongSanPhamEl = document.getElementById("tongSanPham");
    const tamTinhEl = document.getElementById("tamTinh");
    const tongCongEl = document.getElementById("tongCong");

    function formatCurrency(value) {
        return Number(value || 0).toLocaleString("vi-VN") + " đ";
    }

    function isUserLoggedIn() {
        const body = document.body;
        if (!body) return false;

        const userId = body.dataset.user || body.dataset.userId || body.dataset.loggedIn;
        return !!(userId && String(userId).trim() !== "");
    }

    function getCart() {
        try {
            return JSON.parse(localStorage.getItem("cart")) || [];
        } catch (error) {
            console.error("Lỗi đọc giỏ hàng:", error);
            return [];
        }
    }

    function saveCart(cart) {
        localStorage.setItem("cart", JSON.stringify(cart));
    }

    function clearCart() {
        localStorage.removeItem("cart");
    }

    function updateSummary(cart) {
        const tongSanPham = cart.reduce((sum, item) => sum + Number(item.soLuong || 0), 0);
        const tamTinh = cart.reduce((sum, item) => {
            return sum + Number(item.gia || 0) * Number(item.soLuong || 0);
        }, 0);

        if (tongSanPhamEl) tongSanPhamEl.textContent = tongSanPham;
        if (tamTinhEl) tamTinhEl.textContent = formatCurrency(tamTinh);
        if (tongCongEl) tongCongEl.textContent = formatCurrency(tamTinh);
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

        if (!isUserLoggedIn()) {
            clearCart();
            renderEmptyTable();
            if (gioHangEmpty) gioHangEmpty.style.display = "block";
            updateSummary([]);
            return;
        }

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
        const minusButtons = document.querySelectorAll(".qty-minus");
        const plusButtons = document.querySelectorAll(".qty-plus");
        const removeButtons = document.querySelectorAll(".giohang-remove-btn");

        minusButtons.forEach(button => {
            button.addEventListener("click", function () {
                if (!isUserLoggedIn()) {
                    clearCart();
                    renderCart();
                    return;
                }

                const index = Number(this.dataset.index);
                const cart = getCart();

                if (!cart[index]) return;

                if (Number(cart[index].soLuong) > 1) {
                    cart[index].soLuong = Number(cart[index].soLuong) - 1;
                } else {
                    cart.splice(index, 1);
                }

                saveCart(cart);
                renderCart();
            });
        });

        plusButtons.forEach(button => {
            button.addEventListener("click", function () {
                if (!isUserLoggedIn()) {
                    clearCart();
                    renderCart();
                    return;
                }

                const index = Number(this.dataset.index);
                const cart = getCart();

                if (!cart[index]) return;

                cart[index].soLuong = Number(cart[index].soLuong || 1) + 1;

                saveCart(cart);
                renderCart();
            });
        });

        removeButtons.forEach(button => {
            button.addEventListener("click", function () {
                if (!isUserLoggedIn()) {
                    clearCart();
                    renderCart();
                    return;
                }

                const index = Number(this.dataset.index);
                const cart = getCart();

                if (!cart[index]) return;

                cart.splice(index, 1);
                saveCart(cart);
                renderCart();
            });
        });
    }

    renderCart();
});