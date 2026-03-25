(function () {
  let pendingTrackId = null;
  let pendingBtn = null;

  function getCSRFToken() {
    return document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1];
  }

  function bindModalClose(modal, form) {
      modal.onclick = function (e) {
        if (
          e.target.classList.contains('modal-mask') ||
          e.target.classList.contains('js-close-modal')
        ) {
          modal.classList.add('hidden');
          if (form) form.reset();
        }
      };
    }


  function ensureModalExists() {
  let modal = document.getElementById('create-playlist-modal');
  if (modal) return modal;

  const wrapper = document.createElement('div');
  wrapper.innerHTML = `
    <div id="create-playlist-modal" class="modal">
      <div class="modal-mask"></div>
      <div class="modal-panel">
        <h3 class="modal-title">创建歌单</h3>
        <form id="create-playlist-form">
          <div class="form-group">
            <label>歌单名称 *</label>
            <input type="text" name="name" required>
          </div>
          <div class="form-group">
            <label>歌单简介（可选）</label>
            <textarea name="description"></textarea>
          </div>
          <div class="form-group">
            <label>歌单封面（可选）</label>
            <input type="file" name="cover" accept="image/*">
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-secondary js-close-modal">取消</button>
            <button type="submit" class="btn-primary">创建并收藏</button>
          </div>
        </form>
      </div>
    </div>
  `;
  document.body.appendChild(wrapper.firstElementChild);
  return document.getElementById('create-playlist-modal');
}

  function openSelectPlaylistsModal(trackId, playlists, btn) {
      pendingTrackId = trackId;
      pendingBtn = btn;

      // 构建 checkbox 列表
      const listHtml = playlists.map(p => `
        <label class="playlist-option">
          <input type="checkbox" value="${p.id}">
          <span>${p.name}</span>
        </label>
      `).join('');

      const wrapper = document.createElement('div');
      wrapper.innerHTML = `
        <div class="modal playlist-select-modal">
          <div class="modal-mask"></div>
          <div class="modal-panel">
            <h3 class="modal-title">选择要收藏的歌单</h3>

            <div class="playlist-select-list">
              ${listHtml}
            </div>

            <div class="modal-actions">
              <button class="btn-secondary js-cancel">取消</button>
              <button class="btn-primary js-confirm">确认收藏</button>
            </div>
          </div>
        </div>
      `;

      const modal = wrapper.firstElementChild;
      document.body.appendChild(modal);

      // 关闭
      modal.onclick = function (e) {
        if (
          e.target.classList.contains('modal-mask') ||
          e.target.classList.contains('js-cancel')
        ) {
          modal.remove();
        }
      };

      // 确认收藏
      modal.querySelector('.js-confirm').onclick = async function () {
        const checked = modal.querySelectorAll('input[type="checkbox"]:checked');
        if (!checked.length) {
          alert('请至少选择一个歌单');
          return;
        }

        const form = new FormData();
        form.append('track_id', pendingTrackId);
        checked.forEach(i => form.append('playlist_ids[]', i.value));

        await fetch('/accounts/api/playlists/add-track/', {
          method: 'POST',
          headers: { 'X-CSRFToken': getCSRFToken() },
          body: form
        });

        modal.remove();
        if (pendingBtn) pendingBtn.classList.add('is-added');
      };
    }


function openModal(trackId, btn) {
  const modal = ensureModalExists();
  const form = modal.querySelector('#create-playlist-form');

  pendingTrackId = trackId;
  pendingBtn = btn;

  modal.classList.remove('hidden');

  form.onsubmit = async function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    if (pendingTrackId) {
      formData.append('track_id', pendingTrackId);
    }

    const res = await fetch('/accounts/api/playlists/create/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: formData
    });

    const result = await res.json();

    if (result.status === 'ok') {
      modal.classList.add('hidden');
      form.reset();

      // 如果是从歌曲收藏创建
      if (pendingBtn) {
        pendingBtn.classList.add('is-added');
      }

      // ⭐ 如果当前页面是个人中心，动态插入歌单
      const grid = document.querySelector('.playlist-grid');
      if (grid && result.playlist) {
        const p = result.playlist;

        const card = document.createElement('div');
        card.className = 'playlist-card';
        card.innerHTML = `
          <a href="/accounts/playlists/${p.id}/" class="playlist-cover js-spa-link">
            ${
              p.cover
                ? `<img src="${p.cover}" alt="${p.name}">`
                : `<div class="playlist-placeholder">🎧</div>`
            }
          </a>

          <div class="playlist-info">
            <div class="playlist-name">${p.name}</div>
            <button
              class="btn-playlist-delete js-delete-playlist"
              data-id="${p.id}"
            >
              删除
            </button>
          </div>
        `;

        grid.prepend(card); // 新歌单放最前面（符合 ordering）
      }

      alert('歌单创建成功');
    }

  };

  bindModalClose(modal, form);

}

function openCreatePlaylistModalOnly() {
  // ⭐ 关键：确保 modal 一定存在
  const modal = ensureModalExists();
  const form = modal.querySelector('#create-playlist-form');
  bindModalClose(modal, form);

  // 清空状态（不绑定歌曲）
  pendingTrackId = null;
  pendingBtn = null;

  modal.classList.remove('hidden');

  form.onsubmit = async function (e) {
    e.preventDefault();

    const formData = new FormData(form);

    const res = await fetch('/accounts/api/playlists/create/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: formData
    });

    const result = await res.json();

    if (result.status === 'ok') {
      modal.classList.add('hidden');
      form.reset();

      // 创建成功后，动态插入歌单卡片
      const grid = document.querySelector('.playlist-grid');
      if (grid && result.playlist) {
        const p = result.playlist;

        const card = document.createElement('div');
        card.className = 'playlist-card';
        card.innerHTML = `
          <a href="/accounts/playlists/${p.id}/" class="playlist-cover js-spa-link">
            ${
              p.cover
                ? `<img src="${p.cover}" alt="${p.name}">`
                : `<div class="playlist-placeholder">🎧</div>`
            }
          </a>
          <div class="playlist-info">
            <div class="playlist-name">${p.name}</div>
            <button class="btn-playlist-delete js-delete-playlist" data-id="${p.id}">
              删除
            </button>
          </div>
        `;
        grid.prepend(card);
      }
    }
  };
}


  async function fetchPlaylists() {
    const res = await fetch('/accounts/api/playlists/');
    return res.json();
  }

  async function createPlaylistAndAddTrack(formData) {
    formData.append('track_id', pendingTrackId);

    const res = await fetch('/accounts/api/playlists/create/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCSRFToken() },
      body: formData
    });

    return res.json();
  }

  document.addEventListener('click', async function (e) {
      const btn = e.target.closest('.js-fav-playlist');
      if (!btn) return;

      e.preventDefault();

      const trackId = btn.dataset.trackId;

      // =========================
      // ⭐ 已收藏 → 取消收藏
      // =========================
      if (btn.classList.contains('is-added')) {
        const form = new FormData();
        form.append('track_id', trackId);

        await fetch('/accounts/api/playlists/remove-track-all/', {
          method: 'POST',
          headers: { 'X-CSRFToken': getCSRFToken() },
          body: form
        });

        btn.classList.remove('is-added');
        return;
      }

      // =========================
      // ⭐ 未收藏 → 收藏流程
      // =========================
      const data = await fetchPlaylists();

      // ① 没有歌单 → 创建歌单
      if (data.count === 0) {
        openModal(trackId, btn);
        return;
      }

      // ② 只有一个歌单 → 直接收藏
      if (data.count === 1) {
        const form = new FormData();
        form.append('track_id', trackId);
        form.append('playlist_ids[]', data.playlists[0].id);

        await fetch('/accounts/api/playlists/add-track/', {
          method: 'POST',
          headers: { 'X-CSRFToken': getCSRFToken() },
          body: form
        });

        btn.classList.add('is-added');
        return;
      }

      // ③ 多歌单 → 选择
      openSelectPlaylistsModal(trackId, data.playlists, btn);
    });


  document.addEventListener('click', function (e) {
      const btn = e.target.closest('.js-create-playlist');
      if (!btn) return;

      e.preventDefault();
      openCreatePlaylistModalOnly();
    });



})();
