document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("searchInput");
    const statusFilter = document.getElementById("statusFilter");
    const rows = document.querySelectorAll("#userTable tbody tr");

    function filterTable() {
        const keyword = searchInput.value.toLowerCase().trim();
        const status = statusFilter.value.toLowerCase().trim();

        rows.forEach(row => {
            const nameCell = row.querySelector(".user-name");
            const usernameCell = row.querySelector(".user-username");
            const emailCell = row.querySelector(".user-email");
            const statusCell = row.querySelector(".user-status");

            if (!nameCell || !usernameCell || !emailCell || !statusCell) return;

            const name = nameCell.textContent.toLowerCase();
            const username = usernameCell.textContent.toLowerCase();
            const email = emailCell.textContent.toLowerCase();
            const userStatus = statusCell.textContent.toLowerCase();

            const matchKeyword =
                name.includes(keyword) ||
                username.includes(keyword) ||
                email.includes(keyword);

            const matchStatus = status === "" || userStatus.includes(status);

            row.style.display = (matchKeyword && matchStatus) ? "" : "none";
        });
    }

    if (searchInput) {
        searchInput.addEventListener("input", filterTable);
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", filterTable);
    }
});