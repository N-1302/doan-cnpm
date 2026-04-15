document.addEventListener("DOMContentLoaded", function () {
    const filterType = document.getElementById("filter_type");
    const dayWrap = document.getElementById("dayFilterWrap");
    const monthWrap = document.getElementById("monthFilterWrap");

    function toggleFilterInputs() {
        if (!filterType) return;

        if (filterType.value === "day") {
            dayWrap.style.display = "block";
            monthWrap.style.display = "none";
        } else {
            dayWrap.style.display = "none";
            monthWrap.style.display = "block";
        }
    }

    if (filterType) {
        toggleFilterInputs();
        filterType.addEventListener("change", toggleFilterInputs);
    }

    const ctx = document.getElementById("revenueChart");
    if (ctx) {
        new Chart(ctx, {
            type: "bar",
            data: {
                labels: window.chartLabels || [],
                datasets: [{
                    label: window.currentFilterType === "day" ? "Doanh thu theo ngày" : "Doanh thu theo tháng",
                    data: window.chartData || [],
                    borderWidth: 2,
                    borderRadius: 10,
                    backgroundColor: [
                        "rgba(239, 68, 68, 0.75)",
                        "rgba(249, 115, 22, 0.75)",
                        "rgba(234, 179, 8, 0.75)",
                        "rgba(16, 185, 129, 0.75)",
                        "rgba(59, 130, 246, 0.75)",
                        "rgba(139, 92, 246, 0.75)",
                        "rgba(236, 72, 153, 0.75)"
                    ],
                    borderColor: "rgba(220, 38, 38, 1)"
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
                            label: function(context) {
                                let value = context.raw || 0;
                                return " " + value.toLocaleString("vi-VN") + " đ";
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value.toLocaleString("vi-VN") + " đ";
                            }
                        }
                    }
                }
            }
        });
    }
});