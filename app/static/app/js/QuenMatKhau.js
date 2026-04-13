document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("quenMatKhauForm");
    const rememberCheckbox = document.getElementById("rememberQMK");
    const input = document.getElementById("username_or_email");

    const savedValue = localStorage.getItem("quenMatKhauInfo");
    if (savedValue) {
        input.value = savedValue;
        rememberCheckbox.checked = true;
    }

    form.addEventListener("submit", function () {
        if (rememberCheckbox.checked) {
            localStorage.setItem("quenMatKhauInfo", input.value);
        } else {
            localStorage.removeItem("quenMatKhauInfo");
        }
    });
});