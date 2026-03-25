console.log('🔥 library.js loaded');

// 🔑 页面初始化函数（可重复调用）
function initLibraryPage() {
  console.log('📚 initLibraryPage');

  const buttons = document.querySelectorAll('.scroll-btn');
  if (!buttons.length) return;

  buttons.forEach(btn => {
    // 防止 SPA 重复绑定
    if (btn.dataset.binded === '1') return;
    btn.dataset.binded = '1';

    btn.addEventListener('click', () => {
      const targetSelector = btn.dataset.target;
      const direction = btn.dataset.dir;

      const container = document.querySelector(targetSelector);
      if (!container) return;

      const card = container.querySelector(':scope > *');
      if (!card) return;

      const cardStyle = window.getComputedStyle(card);
      const gap = parseInt(cardStyle.marginRight) || 16;
      const scrollAmount = card.offsetWidth + gap;

      container.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    });
  });
}

// 🌍 暴露给 SPA 使用
window.initLibraryPage = initLibraryPage;

// 🧱 兼容整页刷新（MPA）
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLibraryPage);
} else {
  initLibraryPage();
}
