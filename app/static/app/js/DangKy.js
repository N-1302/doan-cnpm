document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("dangKyForm");
    const rememberCheckbox = document.getElementById("rememberDangKy");

    const toggleButtons = document.querySelectorAll(".dk-toggle-password");
    toggleButtons.forEach(button => {
        button.addEventListener("click", function () {
            const targetId = this.getAttribute("data-target");
            const input = document.getElementById(targetId);
            const icon = this.querySelector("i");

            if (input.type === "password") {
                input.type = "text";
                icon.classList.remove("fa-eye-slash");
                icon.classList.add("fa-eye");
            } else {
                input.type = "password";
                icon.classList.remove("fa-eye");
                icon.classList.add("fa-eye-slash");
            }
        });
    });

    const fields = ["ho_ten", "username", "email", "sdt", "gioi_tinh"];
    const savedData = JSON.parse(localStorage.getItem("dangKyInfo") || "{}");

    if (savedData && Object.keys(savedData).length > 0) {
        fields.forEach(id => {
            const el = document.getElementById(id);
            if (el && savedData[id]) {
                el.value = savedData[id];
            }
        });
        rememberCheckbox.checked = true;
    }

    form.addEventListener("submit", function (e) {
        const password = document.getElementById("password").value.trim();
        const confirmPassword = document.getElementById("confirm_password").value.trim();

        if (password !== confirmPassword) {
            e.preventDefault();
            alert("Mật khẩu xác nhận không khớp.");
            return;
        }

        if (rememberCheckbox.checked) {
            const data = {};
            fields.forEach(id => {
                const el = document.getElementById(id);
                if (el) {
                    data[id] = el.value;
                }
            });
            localStorage.setItem("dangKyInfo", JSON.stringify(data));
        } else {
            localStorage.removeItem("dangKyInfo");
        }
    });
});