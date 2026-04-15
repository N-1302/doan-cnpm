document.addEventListener("DOMContentLoaded", function () {
    console.log("SanPham.js da chay");

    const buyNowPopup = document.getElementById("buyNowPopup");
    const buyNowPopupOverlay = document.getElementById("buyNowPopupOverlay");
    const closeBuyNowPopup = document.getElementById("closeBuyNowPopup");

    const buyNowImage = document.getElementById("buyNowImage");
    const buyNowName = document.getElementById("buyNowName");
    const buyNowPrice = document.getElementById("buyNowPrice");
    const buyNowStock = document.getElementById("buyNowStock");
    const buyNowQtyInput = document.getElementById("buyNowQtyInput");
    const buyNowMinus = document.getElementById("buyNowMinus");
    const buyNowPlus = document.getElementById("buyNowPlus");
    const buyNowConfirmBtn = document.getElementById("buyNowConfirmBtn");
    const buyNowCheckoutUrl = document.getElementById("buyNowCheckoutUrl");

    let currentProduct = null;

    function parsePrice(price) {
        if (price === null || price === undefined) return 0;
        return Number(String(price).replace(/[^\d]/g, "")) || 0;
    }

    function formatPrice(price) {
        return parsePrice(price).toLocaleString("vi-VN") + " đ";
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
        const totalQty = cart.reduce((sum, item) => sum + Number(item.soLuong || 0), 0);

        if (badge) {
            badge.textContent = totalQty;
        }
    }

    function openPopup() {
        if (buyNowPopup) buyNowPopup.classList.add("active");
        if (buyNowPopupOverlay) buyNowPopupOverlay.classList.add("active");
    }

    function closePopup() {
        if (buyNowPopup) buyNowPopup.classList.remove("active");
        if (buyNowPopupOverlay) buyNowPopupOverlay.classList.remove("active");
    }

    function addToCart(product, quantity) {
        let cart = getCart();

        const existingItem = cart.find(
            (item) => String(item.maBanh) === String(product.maBanh)
        );

        if (existingItem) {
            existingItem.soLuong += quantity;
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

    document.querySelectorAll(".product-buy-now-btn").forEach(function (button) {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();

            console.log("Da bam nut Mua ngay");

            currentProduct = {
                maBanh: this.dataset.id,
                tenBanh: this.dataset.name,
                gia: this.dataset.price,
                hinhAnh: this.dataset.image,
                soLuongTon: this.dataset.stock
            };

            if (buyNowImage) buyNowImage.src = currentProduct.hinhAnh;
            if (buyNowName) buyNowName.textContent = currentProduct.tenBanh;
            if (buyNowPrice) buyNowPrice.textContent = formatPrice(currentProduct.gia);
            if (buyNowStock) buyNowStock.textContent = currentProduct.soLuongTon || 0;
            if (buyNowQtyInput) buyNowQtyInput.value = 1;

            openPopup();
        });
    });

    if (buyNowMinus) {
        buyNowMinus.addEventListener("click", function () {
            let qty = Number(buyNowQtyInput.value) || 1;
            qty = Math.max(1, qty - 1);
            buyNowQtyInput.value = qty;
        });
    }

    if (buyNowPlus) {
        buyNowPlus.addEventListener("click", function () {
            let qty = Number(buyNowQtyInput.value) || 1;
            const maxStock = Number(currentProduct?.soLuongTon) || 1;

            if (qty < maxStock) {
                qty += 1;
                buyNowQtyInput.value = qty;
            }
        });
    }

    if (buyNowConfirmBtn) {
        buyNowConfirmBtn.addEventListener("click", function () {
            if (!currentProduct) return;

            const quantity = Number(buyNowQtyInput.value) || 1;
            addToCart(currentProduct, quantity);

            const checkoutUrl = buyNowCheckoutUrl ? buyNowCheckoutUrl.value : "/checkout/";
            window.location.href = checkoutUrl;
        });
    }

    if (closeBuyNowPopup) {
        closeBuyNowPopup.addEventListener("click", function () {
            closePopup();
        });
    }

    if (buyNowPopupOverlay) {
        buyNowPopupOverlay.addEventListener("click", function () {
            closePopup();
        });
    }

    updateBadge();
});