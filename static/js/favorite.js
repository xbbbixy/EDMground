// ===== CSRF =====
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    document.cookie.split(";").forEach(c => {
      const cookie = c.trim();
      if (cookie.startsWith(name + "=")) {
        cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
      }
    });
  }
  return cookieValue;
}

// ===== 收藏切换（全站唯一逻辑）=====
document.addEventListener("click", function (e) {
  const btn = e.target.closest(".fav-btn");
  if (!btn) return;

  e.preventDefault();


  const artistId = btn.dataset.id;
  if (!artistId) return;

  fetch("/accounts/toggle-favorite-artist/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCookie("csrftoken"),
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: "artist_id=" + encodeURIComponent(artistId),
  })
    .then(res => {
      if (res.status === 403) {
        alert("请先登录后再收藏艺术家");
        throw new Error("unauthorized");
      }
      return res.json();
    })
    .then(data => {
      const textEl = btn.querySelector(".fav-text");
      const countEl = btn.querySelector(".fav-count");

      if (data.status === "added") {
        btn.classList.add("is-favorited");
        if (textEl) textEl.textContent = "已收藏";
      } else if (data.status === "removed") {
        btn.classList.remove("is-favorited");
        if (textEl) textEl.textContent = "收藏";

        // 收藏页允许直接移除卡片
        const card = btn.closest(".fav-artist") || btn.closest(".artist-card");
        if (card) card.remove();
      }

      if (countEl) {
        countEl.textContent = data.favorites_count;
      }
    })
    .catch(err => console.error(err));
});
