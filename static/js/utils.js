// ===== CSRF 工具函数（全局工具，不动）=====
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(
          cookie.substring(name.length + 1)
        );
        break;
      }
    }
  }
  return cookieValue;
}

// ===== 艺术家详情页 Tabs 初始化（SPA 友好）=====
function initArtistDetailTabs() {
  const tabs = document.querySelectorAll(".section-tab");
  if (!tabs.length) return;

  tabs.forEach(tab => {
    // 🚫 防止 SPA 重复绑定
    if (tab.dataset.binded === "1") return;
    tab.dataset.binded = "1";

    tab.addEventListener("click", () => {
      // 切换 tab 样式
      tabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      // 切换内容区块
      const targetId = tab.dataset.target;

      document
        .querySelectorAll("#tracks-section, #albums-section")
        .forEach(section => {
          section.hidden = section.id !== targetId;
        });
    });
  });
}

// 🌍 暴露给 SPA 调用
window.initArtistDetailTabs = initArtistDetailTabs;

// 🧱 兼容整页刷新（MPA）
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initArtistDetailTabs);
} else {
  initArtistDetailTabs();
}
