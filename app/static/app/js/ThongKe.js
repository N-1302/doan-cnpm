document.addEventListener("DOMContentLoaded", function () {
    const filterType = document.getElementById("filter_type");
    const dayWrap = document.getElementById("dayFilterWrap");
    const monthWrap = document.getElementById("monthFilterWrap");

    function toggleFilterInputs() {
        if (!filterType) return;

        if (filterType.value === "day") {
            if (dayWrap) dayWrap.style.display = "block";
            if (monthWrap) monthWrap.style.display = "none";
        } else if (filterType.value === "month") {
            if (dayWrap) dayWrap.style.display = "none";
            if (monthWrap) monthWrap.style.display = "block";
        } else {
            if (dayWrap) dayWrap.style.display = "none";
            if (monthWrap) monthWrap.style.display = "none";
        }
    }

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

    if (filterType) {
        toggleFilterInputs();
        filterType.addEventListener("change", toggleFilterInputs);
    }

    const canvas = document.getElementById("revenueChart");
    if (!canvas) return;

    const labelText =
        window.currentFilterType === "day"
            ? "Doanh thu theo giờ"
            : window.currentFilterType === "month"
            ? "Doanh thu theo ngày"
            : "Doanh thu tổng quan";

    new Chart(canvas, {
        type: "line",
        data: {
            labels: window.chartLabels || [],
            datasets: [{
                label: labelText,
                data: window.chartData || [],
                borderColor: "rgba(220, 38, 38, 1)",
                backgroundColor: "rgba(239, 68, 68, 0.12)",
                borderWidth: 3,
                tension: 0.35,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: "rgba(220, 38, 38, 1)",
                pointBorderColor: "#ffffff",
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let value = context.raw || 0;
                            return " " + Number(value).toLocaleString("vi-VN") + " đ";
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return Number(value).toLocaleString("vi-VN") + " đ";
                        }
                    }
                }
            }
        }
    });

    document.querySelectorAll(".money-value").forEach(el => {
        const price = el.getAttribute("data-price");
        el.textContent = formatPrice(price);
    });
});