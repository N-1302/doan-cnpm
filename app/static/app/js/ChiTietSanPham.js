document.addEventListener("DOMContentLoaded", function () {
    const btnDecrease = document.getElementById("btnDecrease");
    const btnIncrease = document.getElementById("btnIncrease");
    const quantityInput = document.getElementById("quantity");

    const btnAddCart = document.getElementById("btnAddCart");
    const btnBuyNow = document.getElementById("btnBuyNow");

    const modal = document.getElementById("buyNowModal");
    const modalOverlay = document.getElementById("buyNowModalOverlay");
    const closeModal = document.getElementById("closeBuyNowModal");

    const modalImage = document.getElementById("modalProductImage");
    const modalName = document.getElementById("modalProductName");
    const modalPrice = document.getElementById("modalProductPrice");
    const modalStock = document.getElementById("modalProductStock");

    const modalQtyInput = document.getElementById("modalQuantityInput");
    const modalDecrease = document.getElementById("modalDecrease");
    const modalIncrease = document.getElementById("modalIncrease");
    const modalBuyBtn = document.getElementById("modalBuyNowBtn");

    const checkoutUrlInput = document.getElementById("detailCheckoutUrl");
    const detailMessage = document.getElementById("detailMessage");

    function closeModalFn() {
        if (modal) modal.classList.remove("active");
        if (modalOverlay) modalOverlay.classList.remove("active");
        document.body.classList.remove("popup-open");
    }

    closeModal?.addEventListener("click", function (e) {
        e.preventDefault();
        closeModalFn();
    });

    modalOverlay?.addEventListener("click", function () {
        closeModalFn();
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") {
            closeModalFn();
        }
    });

    function showMessage(message, type = "success") {
        if (!detailMessage) return;
        detailMessage.textContent = message;
        detailMessage.className = "detail-message " + type;
    }

    function parsePrice(price) {
        if (price === null || price === undefined) return 0;
        return Number(String(price).replace(/[^\d]/g, "")) || 0;
    }

    function formatPrice(price) {
        return parsePrice(price).toLocaleString("vi-VN") + " đ";
    }

    function getQuantity() {
        return Number(quantityInput?.value || 1);
    }

    function setQuantity(val) {
        if (quantityInput) quantityInput.value = val;
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
    }

    function updateBadge() {
        const badge = document.querySelector(".open-cart-btn .badge");
        const cart = getCart();
        const total = cart.reduce((sum, item) => sum + Number(item.soLuong || 0), 0);
        if (badge) badge.textContent = total;
    }

    function getStock(product) {
        return Number(
            product?.soLuongTon ??
            product?.so_luong_ton ??
            product?.tonKho ??
            product?.stock ??
            0
        );
    }

    function normalizeCart(cart) {
        let changed = false;

        cart = cart.map(item => {
            let soLuong = Number(item.soLuong || 1);
            const tonKho = getStock(item);

            if (soLuong < 1) {
                soLuong = 1;
                changed = true;
            }

            if (tonKho > 0 && soLuong > tonKho) {
                soLuong = tonKho;
                changed = true;
            }

            return {
                ...item,
                soLuong: soLuong
            };
        });

        if (changed) {
            saveCart(cart);
        }

        return cart;
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

    function openCartDrawerSafe() {
        if (typeof window.openCartDrawer === "function") {
            window.openCartDrawer();
            return;
        }

        const drawer = document.getElementById("gioHangTruot");
        const overlay = document.getElementById("gioHangTruotOverlay");

        if (drawer) drawer.classList.add("active");
        if (overlay) overlay.classList.add("active");
        document.body.classList.add("giohangtruot-open");
    }

    function getMainProduct() {
        if (!btnAddCart) return null;

        return {
            maBanh: btnAddCart.getAttribute("data-id"),
            tenBanh: btnAddCart.getAttribute("data-name"),
            gia: btnAddCart.getAttribute("data-price"),
            hinhAnh: btnAddCart.getAttribute("data-image"),
            soLuongTon: btnAddCart.getAttribute("data-stock")
        };
    }

    let currentProduct = null;

    function openModal(product) {
        currentProduct = product;

        if (modalImage) modalImage.src = product.hinhAnh || "";
        if (modalName) modalName.textContent = product.tenBanh || "Sản phẩm";
        if (modalPrice) modalPrice.textContent = formatPrice(product.gia);
        if (modalStock) modalStock.textContent = getStock(product);

        const soLuongDangChon = getQuantity();
        const tonKho = getStock(product);
        const soLuongHopLe = tonKho > 0 ? Math.min(soLuongDangChon, tonKho) : 1;

        if (modalQtyInput) modalQtyInput.value = soLuongHopLe;

        if (modal) modal.classList.add("active");
        if (modalOverlay) modalOverlay.classList.add("active");
        document.body.classList.add("popup-open");
    }

    btnDecrease?.addEventListener("click", function () {
        let q = getQuantity();
        if (q > 1) {
            setQuantity(q - 1);
            showMessage("", "success");
        }
    });

    btnIncrease?.addEventListener("click", function () {
        let q = getQuantity();
        const max = Number(btnAddCart?.getAttribute("data-stock") || 0);

        if (max <= 0) {
            showMessage("Sản phẩm hiện đã hết hàng", "error");
            return;
        }

        if (q < max) {
            setQuantity(q + 1);
            showMessage("", "success");
        } else {
            showMessage("Số lượng vượt quá tồn kho", "error");
        }
    });

    btnAddCart?.addEventListener("click", function () {
        const product = getMainProduct();
        const quantity = getQuantity();

        if (!product || !product.maBanh) {
            showMessage("Không tìm thấy mã sản phẩm", "error");
            return;
        }

        const success = addToCart(product, quantity);
        if (!success) return;

        showMessage("Đã thêm vào giỏ hàng", "success");
        openCartDrawerSafe();
    });

    btnBuyNow?.addEventListener("click", function () {
        const product = {
            maBanh: btnBuyNow.getAttribute("data-id"),
            tenBanh: btnBuyNow.getAttribute("data-name"),
            gia: btnBuyNow.getAttribute("data-price"),
            hinhAnh: btnBuyNow.getAttribute("data-image"),
            soLuongTon: btnBuyNow.getAttribute("data-stock")
        };

        if (!product.maBanh) {
            showMessage("Không tìm thấy mã sản phẩm", "error");
            return;
        }

        openModal(product);
    });

    document.querySelectorAll(".related-buy-now-btn").forEach(function (button) {
        button.addEventListener("click", function () {
            const product = {
                maBanh: this.getAttribute("data-id"),
                tenBanh: this.getAttribute("data-name"),
                gia: this.getAttribute("data-price"),
                hinhAnh: this.getAttribute("data-image"),
                soLuongTon: this.getAttribute("data-stock")
            };

            if (!product.maBanh) return;
            if (modalQtyInput) modalQtyInput.value = 1;
            openModal(product);
        });
    });

    modalDecrease?.addEventListener("click", function () {
        let q = Number(modalQtyInput?.value || 1);
        if (q > 1) {
            modalQtyInput.value = q - 1;
        }
    });

    modalIncrease?.addEventListener("click", function () {
        let q = Number(modalQtyInput?.value || 1);
        const max = getStock(currentProduct);

        if (max <= 0) return;

        if (q < max) {
            modalQtyInput.value = q + 1;
        }
    });

    modalBuyBtn?.addEventListener("click", function () {
        if (!currentProduct) return;

        const quantity = Number(modalQtyInput?.value || 1);
        const success = addToCart(currentProduct, quantity);

        if (!success) return;

        const url = checkoutUrlInput?.value || "/checkout/";
        window.location.href = url;
    });

    document.querySelectorAll(".money-value").forEach(el => {
        const price = el.getAttribute("data-price");
        el.textContent = formatPrice(price);
    });

    updateBadge();
});