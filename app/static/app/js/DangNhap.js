document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("password");
    const togglePasswordBtn = document.getElementById("togglePassword");
    const eyeIcon = document.getElementById("eyeIcon");

    const usernameInput = document.getElementById("username");
    const rememberLogin = document.getElementById("rememberLogin");
    const form = document.getElementById("dangNhapForm");

    const savedLogin = JSON.parse(localStorage.getItem("dangNhapInfo") || "{}");

    if (savedLogin.username) {
        usernameInput.value = savedLogin.username;
        rememberLogin.checked = true;
    }

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

    form.addEventListener("submit", function () {
        if (rememberLogin.checked) {
            localStorage.setItem(
                "dangNhapInfo",
                JSON.stringify({
                    username: usernameInput.value
                })
            );
        } else {
            localStorage.removeItem("dangNhapInfo");
        }
    });
});