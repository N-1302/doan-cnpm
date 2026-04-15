document.addEventListener("DOMContentLoaded", function () {
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
    const buyNowProductId = document.getElementById("buyNowProductId");
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
        document.body.classList.add("popup-open");
    }

    function closePopup() {
        if (buyNowPopup) buyNowPopup.classList.remove("active");
        if (buyNowPopupOverlay) buyNowPopupOverlay.classList.remove("active");
        document.body.classList.remove("popup-open");
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

    function setPopupData(product) {
        currentProduct = product;

        if (buyNowProductId) buyNowProductId.value = product.maBanh;
        if (buyNowImage) buyNowImage.src = product.hinhAnh;
        if (buyNowName) buyNowName.textContent = product.tenBanh;
        if (buyNowPrice) buyNowPrice.textContent = formatPrice(product.gia);
        if (buyNowStock) buyNowStock.textContent = product.soLuongTon || 0;
        if (buyNowQtyInput) buyNowQtyInput.value = 1;
    }

    function getCurrentQty() {
        if (!buyNowQtyInput) return 1;
        return Number(buyNowQtyInput.value) || 1;
    }

    function getMaxStock() {
        if (!currentProduct) return 1;
        return Number(currentProduct.soLuongTon) || 1;
    }

    document.addEventListener("click", function (e) {
        const button = e.target.closest(".home-buy-now-btn, .buy-now-btn");
        if (!button) return;

        e.preventDefault();
        e.stopPropagation();

        const product = {
            maBanh: button.dataset.id,
            tenBanh: button.dataset.name,
            gia: button.dataset.price,
            hinhAnh: button.dataset.image,
            soLuongTon: button.dataset.stock
        };

        setPopupData(product);
        openPopup();
    });

    if (buyNowMinus) {
        buyNowMinus.addEventListener("click", function () {
            let qty = getCurrentQty();
            qty = Math.max(1, qty - 1);
            buyNowQtyInput.value = qty;
        });
    }

    if (buyNowPlus) {
        buyNowPlus.addEventListener("click", function () {
            let qty = getCurrentQty();
            const maxStock = getMaxStock();

            if (qty < maxStock) {
                qty += 1;
                buyNowQtyInput.value = qty;
            }
        });
    }

    if (buyNowConfirmBtn) {
        buyNowConfirmBtn.addEventListener("click", function () {
            if (!currentProduct) return;

            const quantity = getCurrentQty();
            addToCart(currentProduct, quantity);

            const checkoutUrl = buyNowCheckoutUrl ? buyNowCheckoutUrl.value : "/checkout/";
            window.location.href = checkoutUrl;
        });
    }

    if (closeBuyNowPopup) {
        closeBuyNowPopup.addEventListener("click", function (e) {
            e.preventDefault();
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