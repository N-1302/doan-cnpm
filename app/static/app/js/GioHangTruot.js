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

    function isUserLoggedIn() {
        const bodyUser = document.body?.dataset?.user || "";
        const globalUser = typeof user !== "undefined" ? String(user || "") : "";
        return bodyUser.trim() !== "" || globalUser.trim() !== "";
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
        window.dispatchEvent(new Event("cartUpdated"));
        document.dispatchEvent(new CustomEvent("cartUpdated"));
    }

    function clearCart() {
        localStorage.removeItem("cart");
        window.dispatchEvent(new Event("cartUpdated"));
        document.dispatchEvent(new CustomEvent("cartUpdated"));
    }

    function formatPrice(price) {
        return Number(price || 0).toLocaleString("vi-VN") + " đ";
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

    function openCartDrawer(event) {
        if (event) event.preventDefault();
        if (!cartDrawer || !cartOverlay) return;

        cartDrawer.classList.add("active");
        cartOverlay.classList.add("active");
        document.body.classList.add("giohangtruot-open");
    }

    function closeCartDrawer() {
        if (cartDrawer) cartDrawer.classList.remove("active");
        if (cartOverlay) cartOverlay.classList.remove("active");
        document.body.classList.remove("giohangtruot-open");
    }

    function updateHeaderBadge(totalQty) {
        const badge = document.querySelector(".open-cart-btn .badge");
        if (badge) badge.textContent = totalQty;
    }

    function updateDrawerCount(totalQty) {
        if (drawerCount) drawerCount.textContent = totalQty;
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
            const tonKho = getTonKho(item);
            const hetHang = tonKho > 0 && qty >= tonKho;

            totalQty += qty;
            totalMoney += subTotal;

            html += `
                <div class="giohangtruot-item">
                    <div class="giohangtruot-item-left">
                        <img src="${item.hinhAnh || ""}" alt="${item.tenBanh || "Sản phẩm"}" class="giohangtruot-item-img">
                    </div>

                    <div class="giohangtruot-item-center">
                        <h4 class="giohangtruot-item-name">
                            ${item.tenBanh || "Sản phẩm"} 
                            <span>(Số lượng ${qty})</span>
                        </h4>

                        <p class="giohangtruot-item-note">
                            ${item.noiDung || "Thêm nội dung đặt bánh"}
                        </p>

                        ${tonKho > 0 ? `<small>Còn lại: ${tonKho}</small>` : ""}

                        <div class="giohangtruot-qty-box">
                            <button class="qty-btn minus-btn" data-index="${index}">−</button>
                            <span class="qty-number">${qty}</span>
                            <button class="qty-btn plus-btn" data-index="${index}" ${hetHang ? "disabled" : ""}>+</button>
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
        if (totalBox) totalBox.textContent = formatPrice(totalMoney);

        updateHeaderBadge(totalQty);
        updateDrawerCount(totalQty);

        bindCartActions();
    }

    function renderCart() {
        let cart = getCart();
        cart = normalizeCart(cart);

        if (!cart.length) {
            renderEmptyCart();
            return;
        }

        renderFilledCart(cart);
    }

    function bindCartActions() {
        document.querySelectorAll(".minus-btn").forEach(btn => {
            btn.addEventListener("click", function () {
                const index = Number(this.dataset.index);
                let cart = getCart();

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

        document.querySelectorAll(".plus-btn").forEach(btn => {
            btn.addEventListener("click", function () {
                const index = Number(this.dataset.index);
                let cart = getCart();

                if (!cart[index]) return;

                const tonKho = getTonKho(cart[index]);
                let soLuongMoi = Number(cart[index].soLuong || 1) + 1;

                if (tonKho > 0 && soLuongMoi > tonKho) {
                    alert(`Chỉ còn ${tonKho} sản phẩm`);
                    soLuongMoi = tonKho;
                }

                cart[index].soLuong = soLuongMoi;

                saveCart(cart);
                renderCart();
            });
        });

        document.querySelectorAll(".giohangtruot-remove-btn").forEach(btn => {
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

    openCartButtons.forEach(btn => {
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

    window.addEventListener("cartUpdated", function () {
        renderCart();
    });

    if (!isUserLoggedIn()) {
        clearCart();
        renderEmptyCart();
    } else {
        renderCart();
    }
});