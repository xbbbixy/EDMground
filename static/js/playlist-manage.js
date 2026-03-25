(function () {

  function getCSRFToken() {
    return document.cookie
      .split('; ')
      .find(r => r.startsWith('csrftoken='))
      ?.split('=')[1];
  }

  document.addEventListener('click', async function (e) {
    const btn = e.target.closest('.js-delete-playlist');
    if (!btn) return;

    e.preventDefault();

    const ok = confirm('确定要删除这个歌单吗？');
    if (!ok) return;

    const form = new FormData();
    form.append('playlist_id', btn.dataset.id);

    await fetch('/accounts/api/playlists/delete/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: form
    });

    // 简单处理：直接移除卡片
    btn.closest('.playlist-card').remove();
  });

})();
