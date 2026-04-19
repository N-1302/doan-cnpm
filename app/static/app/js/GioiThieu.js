let currentIndex = 0;
let autoSlide = null;

function getSliderElements() {
  const track = document.getElementById("cakeTrack");
  const dots = document.querySelectorAll(".slider-dots span");
  return { track, dots };
}

function updateSlider() {
  const { track, dots } = getSliderElements();
  if (!track || dots.length === 0) return;

  const maxIndex = dots.length - 1;

  if (currentIndex > maxIndex) currentIndex = 0;
  if (currentIndex < 0) currentIndex = maxIndex;

  // mỗi lần trượt 1 bánh = 20%
  track.style.transform = `translateX(-${currentIndex * 20}%)`;

  dots.forEach((dot, i) => {
    dot.classList.toggle("active", i === currentIndex);
  });
}

function nextSlide() {
  const { dots } = getSliderElements();
  if (dots.length === 0) return;

  currentIndex++;
  if (currentIndex > dots.length - 1) {
    currentIndex = 0;
  }

  updateSlider();
}

function prevSlide() {
  const { dots } = getSliderElements();
  if (dots.length === 0) return;

  currentIndex--;
  if (currentIndex < 0) {
    currentIndex = dots.length - 1;
  }

  updateSlider();
}

function goToSlide(index) {
  const { dots } = getSliderElements();
  if (dots.length === 0) return;

  currentIndex = index;
  updateSlider();
  resetAuto();
}

function startAuto() {
  clearInterval(autoSlide);
  autoSlide = setInterval(() => {
    nextSlide();
  }, 3000);
}

function resetAuto() {
  startAuto();
}

document.addEventListener("DOMContentLoaded", () => {
  const { dots } = getSliderElements();

  updateSlider();
  startAuto();

  dots.forEach((dot, index) => {
    dot.addEventListener("click", () => {
      goToSlide(index);
    });
  });
});