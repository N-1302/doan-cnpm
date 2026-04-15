document.addEventListener("DOMContentLoaded", function () {
    const cartDrawer = document.getElementById("gioHangTruot");
    const cartOverlay = document.getElementById("gioHangTruotOverlay");
    const closeCartBtn = document.getElementById("closeGioHangTruot");
    const openCartButtons = document.querySelectorAll(".open-cart-btn");

    const cartList = document.getElementById("gioHangTruotList");
    const emptyBox = document.getElementById("gioHangTruotEmpty");
    const contentBox = document.getElementById("gioHangTruotContent");
    const footerBox = document.getElementById("gioHangTruotFooter");
    const totalBox = document.getElementById("gioHangTruotTongTien");
    const drawerCount = document.querySelector(".giohangtruot-count");

    function getCart() {
        return JSON.parse(localStorage.getItem("cart")) || [];
    }

    function saveCart(cart) {
        localStorage.setItem("cart", JSON.stringify(cart));
    }

    function formatPrice(price) {
        return Number(price).toLocaleString("vi-VN") + " đ";
    }

    function openCartDrawer(event) {
        if (event) event.preventDefault();
        if (!cartDrawer || !cartOverlay) return;

        cartDrawer.classList.add("active");
        cartOverlay.classList.add("active");
        document.body.classList.add("giohangtruot-open");
        window.openCartDrawer = openCartDrawer;
    }

    function closeCartDrawer() {
        if (cartDrawer) cartDrawer.classList.remove("active");
        if (cartOverlay) cartOverlay.classList.remove("active");
        document.body.classList.remove("giohangtruot-open");
    }

    function updateHeaderBadge(totalQty) {
        const badge = document.querySelector(".open-cart-btn .badge");
        if (badge) {
            badge.textContent = totalQty;
        }
    }

    function updateDrawerCount(totalQty) {
        if (drawerCount) {
            drawerCount.textContent = totalQty;
        }
    }

    function renderEmptyCart() {
        if (emptyBox) emptyBox.style.display = "flex";
        if (contentBox) contentBox.style.display = "none";
        if (footerBox) footerBox.style.display = "none";
        if (cartList) cartList.innerHTML = "";
        if (totalBox) totalBox.textContent = "0 đ";

        updateHeaderBadge(0);
        updateDrawerCount(0);
    }

    function renderFilledCart(cart) {
        if (!cartList) return;

        if (emptyBox) emptyBox.style.display = "none";
        if (contentBox) contentBox.style.display = "block";
        if (footerBox) footerBox.style.display = "block";

        let html = "";
        let totalQty = 0;
        let totalMoney = 0;

        cart.forEach((item, index) => {
            const qty = Number(item.soLuong || 1);
            const price = Number(item.gia || 0);
            const subTotal = qty * price;

            totalQty += qty;
            totalMoney += subTotal;

            html += `
                <div class="giohangtruot-item">
                    <div class="giohangtruot-item-left">
                        <img src="${item.hinhAnh}" alt="${item.tenBanh}" class="giohangtruot-item-img">
                    </div>

                    <div class="giohangtruot-item-center">
                        <h4 class="giohangtruot-item-name">${item.tenBanh} <span>(Số lượng ${qty})</span></h4>
                        <p class="giohangtruot-item-note">Thêm nội dung đặt bánh</p>

                        <div class="giohangtruot-qty-box">
                            <button class="qty-btn minus-btn" data-index="${index}">−</button>
                            <span class="qty-number">${qty}</span>
                            <button class="qty-btn plus-btn" data-index="${index}">+</button>
                        </div>
                    </div>

                    <div class="giohangtruot-item-right">
                        <button class="giohangtruot-remove-btn" data-index="${index}">×</button>
                        <div class="giohangtruot-item-price">${formatPrice(subTotal)}</div>
                    </div>
                </div>
            `;
        });

        cartList.innerHTML = html;

        if (totalBox) {
            totalBox.textContent = formatPrice(totalMoney);
        }

        updateHeaderBadge(totalQty);
        updateDrawerCount(totalQty);

        bindCartActions();
    }

    function renderCart() {
        const cart = getCart();

        if (!cart.length) {
            renderEmptyCart();
            return;
        }

        renderFilledCart(cart);
    }

    function bindCartActions() {
        document.querySelectorAll(".minus-btn").forEach((btn) => {
            btn.addEventListener("click", function () {
                const index = Number(this.dataset.index);
                let cart = getCart();

                if (!cart[index]) return;

                if (cart[index].soLuong > 1) {
                    cart[index].soLuong -= 1;
                } else {
                    cart.splice(index, 1);
                }

                saveCart(cart);
                renderCart();
            });
        });

        document.querySelectorAll(".plus-btn").forEach((btn) => {
            btn.addEventListener("click", function () {
                const index = Number(this.dataset.index);
                let cart = getCart();

                if (!cart[index]) return;

                cart[index].soLuong += 1;
                saveCart(cart);
                renderCart();
            });
        });

        document.querySelectorAll(".giohangtruot-remove-btn").forEach((btn) => {
            btn.addEventListener("click", function () {
                const index = Number(this.dataset.index);
                let cart = getCart();

                if (!cart[index]) return;

                cart.splice(index, 1);
                saveCart(cart);
                renderCart();
            });
        });
    }

    openCartButtons.forEach((btn) => {
        btn.addEventListener("click", openCartDrawer);
    });

    if (closeCartBtn) {
        closeCartBtn.addEventListener("click", closeCartDrawer);
    }

    if (cartOverlay) {
        cartOverlay.addEventListener("click", closeCartDrawer);
    }

    document.addEventListener("cartUpdated", function () {
        renderCart();
    });

    renderCart();
});