document.addEventListener("DOMContentLoaded", function () {
    const tableBody = document.getElementById("gioHangTableBody");
    const emptyBox = document.getElementById("gioHangEmpty");
    const tongSanPham = document.getElementById("tongSanPham");
    const tamTinh = document.getElementById("tamTinh");
    const tongCong = document.getElementById("tongCong");

    function formatMoney(value) {
        return Number(value).toLocaleString("vi-VN") + " đ";
    }

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

    async function loadCartPage() {
        try {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="giohang-loading">Đang tải giỏ hàng...</td>
                </tr>
            `;

            const response = await fetch("/api/cart/");
            const data = await response.json();

            if (!data.success) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="5" class="giohang-loading">Không tải được giỏ hàng</td>
                    </tr>
                `;
                return;
            }

            tongSanPham.textContent = data.total_items || 0;
            tamTinh.textContent = formatMoney(data.subtotal || 0);
            tongCong.textContent = formatMoney(data.subtotal || 0);

            if (!data.items || data.items.length === 0) {
                document.querySelector(".giohang-table-wrap").style.display = "none";
                emptyBox.style.display = "block";
                return;
            }

            document.querySelector(".giohang-table-wrap").style.display = "block";
            emptyBox.style.display = "none";

            let html = "";

            data.items.forEach(item => {
                html += `
                    <tr>
                        <td>
                            <div class="giohang-product">
                                <div class="giohang-product-image">
                                    <img src="${item.hinh_anh}" alt="${item.ten_banh}">
                                </div>
                                <div class="giohang-product-info">
                                    <h4>${item.ten_banh}</h4>
                                    ${item.mo_ta_ngan ? `<p class="giohang-product-note">${item.mo_ta_ngan}</p>` : ""}
                                </div>
                            </div>
                        </td>

                        <td>
                            <div class="giohang-price">${formatMoney(item.don_gia)}</div>
                        </td>

                        <td>
                            <div class="giohang-qty">
                                <button class="btn-minus" data-mabanh="${item.ma_banh}">−</button>
                                <span>${item.so_luong}</span>
                                <button class="btn-plus" data-mabanh="${item.ma_banh}">+</button>
                            </div>
                        </td>

                        <td>
                            <div class="giohang-total">${formatMoney(item.thanh_tien)}</div>
                        </td>

                        <td>
                            <button class="giohang-remove-btn" data-mabanh="${item.ma_banh}">×</button>
                        </td>
                    </tr>
                `;
            });

            tableBody.innerHTML = html;
            bindCartEvents();
        } catch (error) {
            console.error(error);
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="giohang-loading">Có lỗi xảy ra khi tải giỏ hàng</td>
                </tr>
            `;
        }
    }

    function bindCartEvents() {
        document.querySelectorAll(".btn-plus").forEach(button => {
            button.addEventListener("click", function () {
                updateQuantity(this.dataset.mabanh, "plus");
            });
        });

        document.querySelectorAll(".btn-minus").forEach(button => {
            button.addEventListener("click", function () {
                updateQuantity(this.dataset.mabanh, "minus");
            });
        });

        document.querySelectorAll(".giohang-remove-btn").forEach(button => {
            button.addEventListener("click", function () {
                removeItem(this.dataset.mabanh);
            });
        });
    }

    async function updateQuantity(maBanh, action) {
        try {
            const response = await fetch("/api/cart/update/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    ma_banh: maBanh,
                    action: action
                })
            });

            const data = await response.json();

            if (data.success) {
                loadCartPage();
                if (typeof window.loadCartDrawer === "function") {
                    window.loadCartDrawer();
                }
            } else {
                alert(data.message || "Không cập nhật được số lượng");
            }
        } catch (error) {
            console.error(error);
        }
    }

    async function removeItem(maBanh) {
        try {
            const response = await fetch("/api/cart/remove/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    ma_banh: maBanh
                })
            });

            const data = await response.json();

            if (data.success) {
                loadCartPage();
                if (typeof window.loadCartDrawer === "function") {
                    window.loadCartDrawer();
                }
            } else {
                alert(data.message || "Không xóa được sản phẩm");
            }
        } catch (error) {
            console.error(error);
        }
    }

    loadCartPage();
});