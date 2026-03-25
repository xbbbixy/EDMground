// ===== 艺术家列表页轮播初始化 =====
function initArtistsListPage() {
  const track = document.getElementById('artistCarousel');
  const prev = document.getElementById('carouselPrev');
  const next = document.getElementById('carouselNext');

  // 不在 artists/list 页面，直接退出
  if (!track || !prev || !next) return;

  // 防止 SPA 重复绑定
  if (track.dataset.inited === '1') return;
  track.dataset.inited = '1';

  const scrollAmount = 320;

  prev.addEventListener('click', () => {
    track.scrollBy({
      left: -scrollAmount,
      behavior: 'smooth'
    });
  });

  next.addEventListener('click', () => {
    track.scrollBy({
      left: scrollAmount,
      behavior: 'smooth'
    });
  });
}

// 🌍 暴露给 SPA
window.initArtistsListPage = initArtistsListPage;

// 🧱 兼容整页刷新
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initArtistsListPage);
} else {
  initArtistsListPage();
}
