document.addEventListener("DOMContentLoaded", function () {
    const btnDecrease = document.getElementById("btnDecrease");
    const btnIncrease = document.getElementById("btnIncrease");
    const quantityInput = document.getElementById("quantity");

    const btnBuyNow = document.getElementById("btnBuyNow");
    const buyNowModal = document.getElementById("buyNowModal");
    const modalQuantity = document.getElementById("modalQuantity");

    const cartQuantity = document.getElementById("cartQuantity");
    const buyNowQuantity = document.getElementById("buyNowQuantity");

    function getQuantity() {
        let qty = parseInt(quantityInput.value) || 1;
        if (qty < 1) qty = 1;
        return qty;
    }

    function updateQuantity(qty) {
        if (qty < 1) qty = 1;

        quantityInput.value = qty;

        if (modalQuantity) {
            modalQuantity.textContent = qty;
        }

        if (cartQuantity) {
            cartQuantity.value = qty;
        }

        if (buyNowQuantity) {
            buyNowQuantity.value = qty;
        }
    }

    if (btnDecrease) {
        btnDecrease.addEventListener("click", function () {
            updateQuantity(getQuantity() - 1);
        });
    }

    if (btnIncrease) {
        btnIncrease.addEventListener("click", function () {
            updateQuantity(getQuantity() + 1);
        });
    }

    if (btnBuyNow) {
        btnBuyNow.addEventListener("click", function () {
            updateQuantity(getQuantity());
            buyNowModal.style.display = "flex";
        });
    }

    window.closeBuyNowModal = function () {
        buyNowModal.style.display = "none";
    };

    window.addEventListener("click", function (e) {
        if (e.target === buyNowModal) {
            buyNowModal.style.display = "none";
        }
    });

    updateQuantity(getQuantity());
});