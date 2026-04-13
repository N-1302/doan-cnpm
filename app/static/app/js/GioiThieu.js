let currentIndex = 0;
const maxIndex = 2; // 3 dots
let autoSlide;

function updateSlider() {
  const track = document.getElementById("cakeTrack");
  const dots = document.querySelectorAll(".slider-dots span");

  if (!track) return;

  // mỗi lần trượt 1 bánh = 20%
  track.style.transform = `translateX(-${currentIndex * 20}%)`;

  dots.forEach((dot, i) => {
    dot.classList.toggle("active", i === currentIndex);
  });
}

function nextSlide() {
  currentIndex++;
  if (currentIndex > maxIndex) currentIndex = 0;
  updateSlider();
}

function goToSlide(index) {
  currentIndex = index;
  updateSlider();
  resetAuto();
}

function startAuto() {
  autoSlide = setInterval(nextSlide, 3000);
}

function resetAuto() {
  clearInterval(autoSlide);
  startAuto();
}

document.addEventListener("DOMContentLoaded", () => {
  updateSlider();
  startAuto();
});