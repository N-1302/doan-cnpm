document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const togglePasswordBtn = document.getElementById("togglePassword");
    const eyeIcon = document.getElementById("eyeIcon");
    const usernameInput = document.getElementById("username");
    const rememberLogin = document.getElementById("rememberLogin");
    const form = document.getElementById("dangNhapForm");
    const fbBtn = document.getElementById("fbBtn");
    const savedLogin = JSON.parse(localStorage.getItem("dangNhapInfo") || "{}");

    // Nút Facebook
    if (fbBtn) {
        fbBtn.addEventListener("click", function () {
            alert("Tính năng đăng nhập Facebook đang phát triển 🚧");
        });
    }

    // Nếu còn checkbox ghi nhớ đăng nhập thì mới khôi phục dữ liệu
    if (savedLogin.username && usernameInput && rememberLogin) {
        usernameInput.value = savedLogin.username;
        rememberLogin.checked = true;
    }

    // Hiện / ẩn mật khẩu
    if (togglePasswordBtn && passwordInput && eyeIcon) {
        togglePasswordBtn.addEventListener("click", function () {
            if (passwordInput.type === "password") {
                passwordInput.type = "text";
                eyeIcon.classList.remove("fa-eye-slash");
                eyeIcon.classList.add("fa-eye");
            } else {
                passwordInput.type = "password";
                eyeIcon.classList.remove("fa-eye");
                eyeIcon.classList.add("fa-eye-slash");
            }
        });
    }

    // Submit form
    if (form) {
        form.addEventListener("submit", function () {
            if (rememberLogin && rememberLogin.checked && usernameInput) {
                localStorage.setItem(
                    "dangNhapInfo",
                    JSON.stringify({
                        username: usernameInput.value.trim()
                    })
                );
            } else {
                localStorage.removeItem("dangNhapInfo");
            }
        });
    }
});