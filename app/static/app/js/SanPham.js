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
    const buyNowCheckoutUrl = document.getElementById("buyNowCheckoutUrl");

    let currentProduct = null;
    let popupMessageEl = null;

    function ensurePopupMessage() {
        if (popupMessageEl) return popupMessageEl;

        popupMessageEl = document.getElementById("buyNowPopupMessage");
        if (popupMessageEl) return popupMessageEl;

        popupMessageEl = document.createElement("p");
        popupMessageEl.id = "buyNowPopupMessage";
        popupMessageEl.style.color = "#d70018";
        popupMessageEl.style.fontWeight = "600";
        popupMessageEl.style.marginTop = "12px";
        popupMessageEl.style.marginBottom = "0";

        const actionBox = document.querySelector(".buy-now-actions");
        if (actionBox && actionBox.parentNode) {
            actionBox.parentNode.insertBefore(popupMessageEl, actionBox.nextSibling);
        }

        return popupMessageEl;
    }

    function showPopupMessage(message, type = "error") {
        const el = ensurePopupMessage();
        if (!el) return;
        el.textContent = message || "";
        el.style.color = type === "error" ? "#d70018" : "#16a34a";
    }

    function clearPopupMessage() {
        const el = ensurePopupMessage();
        if (!el) return;
        el.textContent = "";
    }

    function parsePrice(price) {
        if (price === null || price === undefined) return 0;

        let value = String(price).trim();
        value = value.replace(/VNĐ|VND|đ/gi, "").trim();

        if (/^\d{1,3}(\.\d{3})+$/.test(value)) {
            return parseInt(value.replace(/\./g, ""), 10);
        }

        if (/^\d{1,3}(,\d{3})+$/.test(value)) {
            return parseInt(value.replace(/,/g, ""), 10);
        }

        return parseInt(value.replace(/[^\d]/g, ""), 10) || 0;
    }

    function formatPrice(price) {
        return parsePrice(price).toLocaleString("vi-VN") + " đ";
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

    function updateBadge() {
        const badge = document.querySelector(".open-cart-btn .badge");
        const cart = getCart();
        const totalQty = cart.reduce((sum, item) => sum + Number(item.soLuong || 0), 0);
        if (badge) badge.textContent = totalQty;
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

    function getCurrentQty() {
        return Number(buyNowQtyInput?.value || 1);
    }

    function getMaxStock() {
        return getStock(currentProduct);
    }

    function updatePopupButtons() {
        const maxStock = getMaxStock();
        const qty = getCurrentQty();

        if (buyNowMinus) buyNowMinus.disabled = qty <= 1;
        if (buyNowPlus) buyNowPlus.disabled = maxStock <= 0 || qty >= maxStock;

        if (buyNowConfirmBtn) {
            buyNowConfirmBtn.disabled = maxStock <= 0;
            buyNowConfirmBtn.textContent = maxStock <= 0 ? "Hết hàng" : "Mua ngay";
        }
    }

    function openPopup() {
        buyNowPopup?.classList.add("active");
        buyNowPopupOverlay?.classList.add("active");
        document.body.classList.add("popup-open");
    }

    function closePopup() {
        buyNowPopup?.classList.remove("active");
        buyNowPopupOverlay?.classList.remove("active");
        document.body.classList.remove("popup-open");
        clearPopupMessage();
    }

    function saveBuyNowToCart(product, quantity) {
        const tonKho = Number(product.soLuongTon || 0);
        let soLuongThem = Number(quantity || 1);

        if (soLuongThem < 1) soLuongThem = 1;

        let cart = [];
        try {
            cart = JSON.parse(localStorage.getItem("cart") || "[]");
            if (!Array.isArray(cart)) cart = [];
        } catch {
            cart = [];
        }

        const index = cart.findIndex(item => String(item.maBanh) === String(product.maBanh));
        const giaDung = parsePrice(product.gia);

        if (index !== -1) {
            let soLuongMoi = Number(cart[index].soLuong || 0) + soLuongThem;

            if (tonKho > 0 && soLuongMoi > tonKho) {
                soLuongMoi = tonKho;
            }

            cart[index].soLuong = soLuongMoi;
            cart[index].soLuongTon = tonKho;
            cart[index].gia = giaDung;
            cart[index].tenBanh = product.tenBanh;
            cart[index].hinhAnh = product.hinhAnh;
        } else {
            let soLuong = soLuongThem;

            if (tonKho > 0 && soLuong > tonKho) {
                soLuong = tonKho;
            }

            cart.push({
                maBanh: String(product.maBanh),
                tenBanh: product.tenBanh,
                gia: giaDung,
                hinhAnh: product.hinhAnh,
                soLuong: soLuong,
                soLuongTon: tonKho,
                noiDung: product.noiDung || ""
            });
        }

        localStorage.setItem("cart", JSON.stringify(cart));
    }

    function setPopupData(product) {
        currentProduct = product;

        if (buyNowImage) buyNowImage.src = product.hinhAnh || "";
        if (buyNowName) buyNowName.textContent = product.tenBanh || "Sản phẩm";
        if (buyNowPrice) buyNowPrice.textContent = formatPrice(product.gia);

        const tonKho = getStock(product);

        if (buyNowStock) buyNowStock.textContent = tonKho > 0 ? tonKho : "Hết hàng";
        if (buyNowQtyInput) buyNowQtyInput.value = tonKho > 0 ? 1 : 0;

        clearPopupMessage();
        updatePopupButtons();
    }

    document.querySelectorAll(".product-buy-now-btn, .buy-now-btn").forEach(function (button) {
        button.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();

            currentProduct = {
                maBanh: this.dataset.id,
                tenBanh: this.dataset.name,
                gia: this.dataset.price,
                hinhAnh: this.dataset.image,
                soLuongTon: this.dataset.stock
            };

            if (!currentProduct.maBanh) return;

            setPopupData(currentProduct);
            openPopup();
        });
    });

    buyNowMinus?.addEventListener("click", function () {
        let qty = getCurrentQty();
        qty = Math.max(1, qty - 1);
        if (buyNowQtyInput) buyNowQtyInput.value = qty;
        clearPopupMessage();
        updatePopupButtons();
    });

    buyNowPlus?.addEventListener("click", function () {
        let qty = getCurrentQty();
        const maxStock = getMaxStock();

        if (maxStock <= 0) {
            showPopupMessage("Sản phẩm đã hết hàng", "error");
            updatePopupButtons();
            return;
        }

        if (qty < maxStock) {
            if (buyNowQtyInput) buyNowQtyInput.value = qty + 1;
            clearPopupMessage();
        } else {
            showPopupMessage("Số lượng vượt quá tồn kho", "error");
        }

        updatePopupButtons();
    });

    buyNowConfirmBtn?.addEventListener("click", function () {
        if (!currentProduct) return;

        const quantity = getCurrentQty();
        const tonKho = getMaxStock();

        if (tonKho <= 0) {
            showPopupMessage("Sản phẩm đã hết hàng", "error");
            return;
        }

        if (quantity > tonKho) {
            showPopupMessage("Số lượng vượt quá tồn kho", "error");
            return;
        }

        saveBuyNowToCart(currentProduct, quantity);
        updateBadge();

        const checkoutUrl = buyNowCheckoutUrl?.value || "/checkout/";
        closePopup();
        window.location.href = checkoutUrl;
    });

    closeBuyNowPopup?.addEventListener("click", function (e) {
        e.preventDefault();
        closePopup();
    });

    buyNowPopupOverlay?.addEventListener("click", function () {
        closePopup();
    });

    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closePopup();
    });

    updateBadge();
});