document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("datLaiMatKhauForm");
    const rememberCheckbox = document.getElementById("rememberDLMK");
    const otpInput = document.getElementById("otp");

    const toggleButtons = document.querySelectorAll(".dlmk-toggle-password");
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

    const savedOtp = localStorage.getItem("datLaiMatKhauOTP");
    if (savedOtp) {
        otpInput.value = savedOtp;
        rememberCheckbox.checked = true;
    }

    form.addEventListener("submit", function (e) {
        const newPassword = document.getElementById("new_password").value.trim();
        const confirmPassword = document.getElementById("confirm_password").value.trim();

        if (newPassword !== confirmPassword) {
            e.preventDefault();
            alert("Mật khẩu xác nhận không khớp.");
            return;
        }

        if (rememberCheckbox.checked) {
            localStorage.setItem("datLaiMatKhauOTP", otpInput.value);
        } else {
            localStorage.removeItem("datLaiMatKhauOTP");
        }
    });
});