document.addEventListener("DOMContentLoaded", function () { 
    const modal = document.getElementById("addCakeModal");
    const openBtn = document.getElementById("openAddModal");
    const closeBtn = document.getElementById("closeAddModal");
    const cancelBtn = document.getElementById("cancelAddModal");

    if (openBtn) {
        openBtn.addEventListener("click", function () {
            modal.classList.add("show");
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", function () {
            modal.classList.remove("show");
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener("click", function () {
            modal.classList.remove("show");
        });
    }

    window.addEventListener("click", function (e) {
        if (e.target === modal) {
            modal.classList.remove("show");
        }
    });

    const searchInput = document.getElementById("searchInput");
    const categoryFilter = document.getElementById("categoryFilter");
    const rows = document.querySelectorAll("#cakeTable tbody tr");

    function filterTable() {
        const keyword = searchInput.value.toLowerCase().trim();
        const category = categoryFilter.value.toLowerCase().trim();

        rows.forEach(row => {
            const nameCell = row.querySelector(".cake-name");
            const categoryCell = row.querySelector(".cake-category");

            if (!nameCell || !categoryCell) return;

            const name = nameCell.textContent.toLowerCase();
            const cakeCategory = categoryCell.textContent.toLowerCase();

            const matchKeyword = name.includes(keyword);
            const matchCategory = category === "" || cakeCategory.includes(category);

            row.style.display = (matchKeyword && matchCategory) ? "" : "none";
        });
    }

    if (searchInput) searchInput.addEventListener("input", filterTable);
    if (categoryFilter) categoryFilter.addEventListener("change", filterTable);

    function formatPrice(price) {
        let value = String(price ?? "").trim();

        value = value.replace(/đ|vnd|vnđ/gi, "").trim();

        if (/^\d{1,3}([.,]\d{3})+([.,]\d+)?$/.test(value)) {
            value = value.replace(/[.,](?=\d{3}\b)/g, "");
        }

        value = value.replace(",", ".");

        const number = parseFloat(value);
        return (isNaN(number) ? 0 : number).toLocaleString("vi-VN") + " đ";
    }

    document.querySelectorAll(".money-value").forEach(el => {
        const price = el.getAttribute("data-price");
        el.textContent = formatPrice(price);
    });
});