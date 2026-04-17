document.addEventListener("DOMContentLoaded", function () {
    const deleteButtons = document.querySelectorAll(".js-delete-review");

    deleteButtons.forEach(function (button) {
        button.addEventListener("click", function (event) {
            const reviewId = this.dataset.reviewId || "";
            const isConfirmed = confirm(`Bạn có chắc muốn xóa đánh giá #${reviewId} không?`);

            if (!isConfirmed) {
                event.preventDefault();
            }
        });
    });
});