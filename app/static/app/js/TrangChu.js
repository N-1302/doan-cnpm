document.addEventListener("DOMContentLoaded", function () {
  const track = document.getElementById("featuredTrack");
  const prevBtn = document.getElementById("featuredPrev");
  const nextBtn = document.getElementById("featuredNext");

  if (!track || !prevBtn || !nextBtn) return;

  const cards = track.querySelectorAll(".featured-card");
  if (!cards.length) return;

  let currentIndex = 0;

  function getCardsPerView() {
    if (window.innerWidth <= 576) return 1;
    if (window.innerWidth <= 991) return 2;
    return 4;
  }

  function updateSlider() {
    const cardsPerView = getCardsPerView();
    const card = cards[0];
    const cardStyle = window.getComputedStyle(card);
    const gap = parseInt(window.getComputedStyle(track).gap) || 24;
    const cardWidth = card.offsetWidth + gap;

    track.style.transform = `translateX(-${currentIndex * cardWidth}px)`;

    const maxIndex = Math.max(0, cards.length - cardsPerView);

    prevBtn.style.opacity = currentIndex <= 0 ? "0.5" : "1";
    nextBtn.style.opacity = currentIndex >= maxIndex ? "0.5" : "1";
    prevBtn.style.pointerEvents = currentIndex <= 0 ? "none" : "auto";
    nextBtn.style.pointerEvents = currentIndex >= maxIndex ? "none" : "auto";
  }

  nextBtn.addEventListener("click", function () {
    const cardsPerView = getCardsPerView();
    const maxIndex = Math.max(0, cards.length - cardsPerView);

    if (currentIndex < maxIndex) {
      currentIndex++;
      updateSlider();
    }
  });

  prevBtn.addEventListener("click", function () {
    if (currentIndex > 0) {
      currentIndex--;
      updateSlider();
    }
  });

  window.addEventListener("resize", function () {
    const cardsPerView = getCardsPerView();
    const maxIndex = Math.max(0, cards.length - cardsPerView);
    if (currentIndex > maxIndex) currentIndex = maxIndex;
    updateSlider();
  });

  updateSlider();
});