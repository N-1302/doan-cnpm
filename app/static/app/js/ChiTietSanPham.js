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
        return JSON.parse(localStorage.getItem("cart")) || [];
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

    function addToCart(product, quantity) {
        let cart = getCart();

        const index = cart.findIndex(
            item => String(item.maBanh) === String(product.maBanh)
        );

        if (index !== -1) {
            cart[index].soLuong += quantity;
        } else {
            cart.push({
                maBanh: product.maBanh,
                tenBanh: product.tenBanh,
                gia: parsePrice(product.gia),
                hinhAnh: product.hinhAnh,
                soLuong: quantity
            });
        }

        saveCart(cart);
        updateBadge();
        document.dispatchEvent(new CustomEvent("cartUpdated"));
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

        if (modalImage) modalImage.src = product.hinhAnh;
        if (modalName) modalName.textContent = product.tenBanh;
        if (modalPrice) modalPrice.textContent = formatPrice(product.gia);
        if (modalStock) modalStock.textContent = product.soLuongTon || 0;
        if (modalQtyInput) modalQtyInput.value = getQuantity();

        if (modal) modal.classList.add("active");
        if (modalOverlay) modalOverlay.classList.add("active");
    }

    function closeModalFn() {
        if (modal) modal.classList.remove("active");
        if (modalOverlay) modalOverlay.classList.remove("active");
    }

    btnDecrease?.addEventListener("click", function () {
        let q = getQuantity();
        if (q > 1) setQuantity(q - 1);
    });

    btnIncrease?.addEventListener("click", function () {
        let q = getQuantity();
        const max = Number(btnAddCart?.getAttribute("data-stock") || 1);

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

        console.log("btnAddCart clicked", product);

        if (!product || !product.maBanh) {
            showMessage("Không tìm thấy mã sản phẩm", "error");
            return;
        }

        addToCart(product, quantity);
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

        console.log("btnBuyNow clicked", product);

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
        if (q > 1) modalQtyInput.value = q - 1;
    });

    modalIncrease?.addEventListener("click", function () {
        let q = Number(modalQtyInput?.value || 1);
        const max = Number(currentProduct?.soLuongTon || 1);

        if (q < max) {
            modalQtyInput.value = q + 1;
        }
    });

    modalBuyBtn?.addEventListener("click", function () {
        if (!currentProduct) return;

        const quantity = Number(modalQtyInput?.value || 1);

        addToCart(currentProduct, quantity);

        const url = checkoutUrlInput?.value || "/checkout/";
        window.location.href = url;
    });

    closeModal?.addEventListener("click", closeModalFn);
    modalOverlay?.addEventListener("click", closeModalFn);

    updateBadge();
});