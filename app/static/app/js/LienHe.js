document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("contactForm");
    const submitBtn = document.getElementById("submitBtn");
    const alerts = document.querySelectorAll(".contact-alert");

    if (form && submitBtn) {
        form.addEventListener("submit", function () {
            submitBtn.classList.add("loading");
            submitBtn.innerHTML = '<span class="btn-text">Đang gửi...</span>';
        });
    }

    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = "all 0.4s ease";
                alert.style.opacity = "0";
                alert.style.transform = "translateY(-6px)";
                setTimeout(() => {
                    alert.remove();
                }, 400);
            });
        }, 4000);
    }
});