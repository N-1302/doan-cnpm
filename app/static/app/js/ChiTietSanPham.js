document.addEventListener("DOMContentLoaded", function () {
    const btnDecrease = document.getElementById("btnDecrease");
    const btnIncrease = document.getElementById("btnIncrease");
    const quantityInput = document.getElementById("quantity");

    const btnAddCart = document.getElementById("btnAddCart");
    const btnBuyNow = document.getElementById("btnBuyNow");

    const buyNowModal = document.getElementById("buyNowModal");
    const closeBuyNowModalBtn = document.getElementById("closeBuyNowModal");
    const modalQuantity = document.getElementById("modalQuantity");
    const buyNowQuantity = document.getElementById("buyNowQuantity");

    const detailMessage = document.getElementById("detailMessage");

    if (!quantityInput) return;

    const maBanh = btnAddCart ? btnAddCart.dataset.mabanh : null;
    const soLuongTon = btnAddCart ? parseInt(btnAddCart.dataset.soluongton || "0", 10) : 0;

    function getCSRFToken() {
        const name = "csrftoken";
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                return cookie.substring(name.length + 1);
            }
        }
        return "";
    }

    function showMessage(message, type = "success") {
        if (!detailMessage) return;
        detailMessage.textContent = message;
        detailMessage.className = "detail-message " + type;
    }

    function getQuantity() {
        return parseInt(quantityInput.value || "1", 10);
    }

    function setQuantity(value) {
        quantityInput.value = value;

        if (modalQuantity) {
            modalQuantity.textContent = value;
        }

        if (buyNowQuantity) {
            buyNowQuantity.value = value;
        }
    }

    if (btnDecrease) {
        btnDecrease.addEventListener("click", function () {
            let current = getQuantity();
            if (current > 1) {
                setQuantity(current - 1);
            }
        });
    }

    if (btnIncrease) {
        btnIncrease.addEventListener("click", function () {
            let current = getQuantity();
            if (current < soLuongTon) {
                setQuantity(current + 1);
            } else {
                showMessage("Số lượng vượt quá tồn kho", "error");
            }
        });
    }

    if (btnAddCart) {
        btnAddCart.addEventListener("click", async function () {
            const soLuong = getQuantity();

            try {
                btnAddCart.disabled = true;
                btnAddCart.textContent = "ĐANG THÊM...";

                const response = await fetch("/api/cart/add/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify({
                        ma_banh: maBanh,
                        so_luong: soLuong
                    })
                });

                const data = await response.json();

                if (data.success) {
                    showMessage("Đã thêm vào giỏ hàng", "success");

                    if (typeof window.openCartDrawer === "function") {
                        window.openCartDrawer();
                    }
                } else {
                    showMessage(data.message || "Không thể thêm vào giỏ hàng", "error");
                }
            } catch (error) {
                console.error(error);
                showMessage("Có lỗi xảy ra khi thêm vào giỏ hàng", "error");
            } finally {
                btnAddCart.disabled = false;
                btnAddCart.textContent = "Thêm vào giỏ hàng";
            }
        });
    }

    if (btnBuyNow && buyNowModal) {
        btnBuyNow.addEventListener("click", function () {
            setQuantity(getQuantity());
            buyNowModal.classList.add("active");
        });
    }

    if (closeBuyNowModalBtn && buyNowModal) {
        closeBuyNowModalBtn.addEventListener("click", function () {
            buyNowModal.classList.remove("active");
        });
    }

    if (buyNowModal) {
        buyNowModal.addEventListener("click", function (e) {
            if (e.target === buyNowModal) {
                buyNowModal.classList.remove("active");
            }
        });
    }

    setQuantity(getQuantity());
});