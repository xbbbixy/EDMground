console.log('[playlist-detail] loaded');

(function () {

  function getCSRFToken() {
    return document.cookie
      .split('; ')
      .find(r => r.startsWith('csrftoken='))
      ?.split('=')[1];
  }

  /* =========================
     从歌单移除歌曲
  ========================= */
  document.addEventListener('click', async function (e) {
    const btn = e.target.closest('.js-remove-track');
    if (!btn) return;

    e.preventDefault();

    const form = new FormData();
    form.append('playlist_id', btn.dataset.playlistId);
    form.append('track_id', btn.dataset.trackId);

    await fetch('/accounts/api/playlists/remove-track/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: form
    });

    btn.closest('.track-card')?.remove();
  });

  /* =========================
     播放整个歌单
  ========================= */
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.js-play-playlist');
    if (!btn) return;

    e.preventDefault();

    const trackButtons = document.querySelectorAll('.track-card .btn-play');
    if (!trackButtons.length) {
      alert('歌单里还没有歌曲');
      return;
    }

    trackButtons.forEach((playBtn, index) => {
      playBtn.dataset.autoplay = index === 0 ? 'true' : 'false';
      playBtn.click();
    });
  });

  /* =========================
       ✏ 编辑歌单（完整实现）
    ========================= */
    document.addEventListener('click', function (e) {
      const btn = e.target.closest('.js-edit-playlist');
      if (!btn) return;

      e.preventDefault();

      const page = document.querySelector('.playlist-detail-page');
      const playlistId = page.dataset.playlistId;

      // 当前页面信息
      const titleEl = document.querySelector('.playlist-title');
      const descEl = document.querySelector('.playlist-desc');
      const coverImg = document.querySelector('.playlist-cover-img');

      // 创建 modal（复用样式体系）
      const wrapper = document.createElement('div');
      wrapper.innerHTML = `
        <div class="modal playlist-modal">
          <div class="modal-mask"></div>
          <div class="modal-panel">
            <h3 class="modal-title">编辑歌单</h3>

            <form class="edit-playlist-form">
              <div class="form-group">
                <label>歌单名称 *</label>
                <input type="text" name="name" required value="${titleEl.textContent.trim()}">
              </div>

              <div class="form-group">
                <label>歌单简介</label>
                <textarea name="description">${descEl.textContent.trim()}</textarea>
              </div>

              <div class="form-group">
                <label>更换封面</label>
                <input type="file" name="cover" accept="image/*">
              </div>

              <div class="modal-actions">
                <button type="button" class="btn-secondary js-cancel">取消</button>
                <button type="submit" class="btn-primary">保存</button>
              </div>
            </form>
          </div>
        </div>
      `;

      const modal = wrapper.firstElementChild;
      document.body.appendChild(modal);

      // 关闭
      modal.addEventListener('click', function (ev) {
        if (
          ev.target.classList.contains('modal-mask') ||
          ev.target.classList.contains('js-cancel')
        ) {
          modal.remove();
        }
      });

      // 提交编辑
      const form = modal.querySelector('.edit-playlist-form');
      form.addEventListener('submit', async function (ev) {
        ev.preventDefault();

        const formData = new FormData(form);
        formData.append('playlist_id', playlistId);

        const res = await fetch('/accounts/api/playlists/update/', {
          method: 'POST',
          headers: { 'X-CSRFToken': getCSRFToken() },
          body: formData
        });

        const result = await res.json();
        if (result.status !== 'ok') return;

        // ===== 即时更新页面 =====
        titleEl.textContent = result.playlist.name;

        if (result.playlist.description) {
          descEl.textContent = result.playlist.description;
          descEl.classList.remove('muted');
        } else {
          descEl.textContent = '';
          descEl.classList.add('muted');
        }

        if (result.playlist.cover) {
          if (coverImg) {
            coverImg.src = result.playlist.cover;
          } else {
            const coverWrap = document.querySelector('.playlist-cover-large');
            coverWrap.innerHTML = `<img src="${result.playlist.cover}" class="playlist-cover-img">`;
          }
        }

        modal.remove();
      });
    });


})();
