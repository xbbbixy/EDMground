console.log("🔥 HOME.JS LOADED");

(function () {
  /* =========================
   * 工具函数
   * ========================= */

  if (window.__HOME_PAGE_INITIALIZED__) {
    console.warn('🏠 home.js skipped (SPA)');
    return;
  }
  window.__HOME_PAGE_INITIALIZED__ = true;

  function getCSRFToken() {
    const name = "csrftoken=";
    const decodedCookie = decodeURIComponent(document.cookie || "");
    const ca = decodedCookie.split(";");
    for (let i = 0; i < ca.length; i++) {
      let c = ca[i].trim();
      if (c.indexOf(name) === 0) return c.substring(name.length);
    }
    return "";
  }

  // 兼容不同字段名
  function pickAudioUrl(track) {
    return (
      track?.audio ||
      track?.audio_url ||
      track?.audioFile ||
      track?.file ||
      track?.url ||
      ""
    );
  }

  /* =========================
   * 推荐歌曲刷新（核心）
   * ========================= */

  async function refreshTracks() {
  const refreshBtn = document.querySelector("#refreshTracks");

  // 🔒 并发锁：防止重复请求
  if (refreshBtn && refreshBtn.dataset.loading === "1") {
    console.log("⏳ refresh locked");
    return;
  }

  refreshBtn && (refreshBtn.dataset.loading = "1");


  try {
    const row = document.querySelector("#trackRow");
    if (!row) {
      console.warn("❌ trackRow not found");
      return;
    }

    const baseUrl = row.dataset.refreshUrl;
    if (!baseUrl) {
      console.warn("❌ refreshUrl not found on trackRow");
      return;
    }

    // 🔥 关键：加时间戳，强制每次都是新请求
    const url = baseUrl + (baseUrl.includes("?") ? "&" : "?") + "_t=" + Date.now();
    console.log("fetch url =", url);

    const r = await fetch(url, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      cache: "no-store"   // 🔥 明确禁止缓存
    });

    if (!r.ok) {
      console.error("❌ fetch failed:", r.status);
      return;
    }

    const data = await r.json();
    console.log("tracks received =", data.tracks);

    // 清空旧内容
    row.innerHTML = "";

    // 只渲染 5 个
    (data.tracks || []).slice(0, 5).forEach(t => {
      const div = document.createElement("div");
      div.className = "music-card";

      div.innerHTML = `
        ${t.cover ? `<img src="${t.cover}" class="music-cover" alt="${t.title}">` : ""}
        <h4>${t.title || "Untitled"}</h4>
        <p class="artist-name">${t.artist || ""}</p>

        <div class="track-actions">
          <button
            class="track-btn circle play-now js-add-to-player"
            data-track-id="${t.id}"
            data-title="${t.title}"
            data-artists="${t.artist}"
            data-audio="${t.audio}"
            data-cover="${t.cover || ''}"
            data-cover="${t.cover}"
          >▶</button>

          <button
            class="track-btn circle add-next js-add-to-player"
            data-autoplay="false"
            data-track-id="${t.id}"
            data-title="${t.title}"
            data-artists="${t.artist}"
            data-audio="${t.audio}"
            data-cover="${t.cover}"
          >＋</button>

          <button
              class="btn-fav-playlist js-fav-playlist ${t.is_added ? 'is-added' : ''}"
              data-track-id="${t.id}"
              title="收藏到歌单"
            >
              ❤
            </button>
        </div>
      `;

      row.appendChild(div);
    });

    console.log("row children after =", row.children.length);

  } catch (err) {
    console.error("❌ refreshTracks error", err);

  } finally {
    // 🔓 无论成功失败，都解锁
    refreshBtn && (refreshBtn.dataset.loading = "0");
  }
}

  /* =========================
   * 艺术家刷新
   * ========================= */

  async function refreshArtists() {
  const row = document.getElementById("artistRow");
  if (!row) return;

  // 🔒 并发锁，防止多次点击
  if (row.dataset.loading === "1") return;
  row.dataset.loading = "1";

  console.log("🎨 refreshArtists START");

  try {
    const url = row.dataset.refreshUrl || "/recommendation/?_ajax=artists";
    console.log("fetch artist url =", url);

    const res = await fetch(url, { cache: "no-store" });
    const data = await res.json();

    console.log("artists received =", data.artists);

    // 🔥 强制清空（无条件）
    row.innerHTML = "";

    if (!Array.isArray(data.artists)) {
      console.warn("artists is not array");
      return;
    }

    // 🔥 只渲染前 5 个
    data.artists.slice(0, 5).forEach((artist) => {
      const card = document.createElement("div");
      card.className = "artist-card-small";
      const avatarHtml = artist.avatar
          ? `
            <div class="artist-avatar-wrap">
              <img src="${artist.avatar}" alt="${artist.name}">
            </div>
          `
          : `
            <div class="artist-avatar-wrap">
              <div class="artist-avatar placeholder"></div>
            </div>
          `;

      card.innerHTML = `
        <a href="/artists/${artist.id}/" class="js-spa-link artist-card-link">
          ${avatarHtml}
          <div class="artist-name">${artist.name}</div>
        </a>
      `;

      row.appendChild(card);
    });

    console.log(
      "artistRow children after =",
      row.querySelectorAll(".artist-card-small").length
    );
  } catch (err) {
    console.error("refreshArtists error", err);
  } finally {
    row.dataset.loading = "0";
  }
}

/* =========================
 * 热门曲风刷新
 * ========================= */

async function refreshGenres() {
  const row = document.getElementById("genreRow");
  if (!row) return;

  // 🔒 并发锁
  if (row.dataset.loading === "1") return;
  row.dataset.loading = "1";

  console.log("🎚 refreshGenres START");

  try {
    const baseUrl =
      row.dataset.refreshUrl ||
      "/recommendation/?_ajax=genres";

    const url =
      baseUrl + (baseUrl.includes("?") ? "&" : "?") + "_t=" + Date.now();

    const r = await fetch(url, {
      headers: { "X-Requested-With": "XMLHttpRequest" },
      cache: "no-store",
    });

    const data = await r.json();
    console.log("genres received =", data.genres);

    // 🔥 清空旧内容
    row.innerHTML = "";

    if (!Array.isArray(data.genres)) return;

    data.genres.slice(0, 5).forEach((g) => {
      const card = document.createElement("div");
      card.className = "genre-card";

      card.innerHTML = `
        <h4>
          <a class="js-spa-link" href="/genres/${g.slug}/">
            ${g.name}
          </a>
        </h4>

        <button
          class="play-genre"
          data-genre="${g.slug}"
          data-random-url="/recommendation/random_tracks_by_genre/">
          ▶ 随机播放
        </button>
      `;

      row.appendChild(card);
    });

    console.log("genreRow children after =", row.children.length);
  } catch (err) {
    console.error("refreshGenres error", err);
  } finally {
    row.dataset.loading = "0";
  }
}

function initHomeGenres() {
  const row = document.getElementById("genreRow");
  if (!row) return;

  console.log("🎚 initHomeGenres");

  // 🔥 不自己清空，交给 refreshGenres 处理
  refreshGenres();
}

function initHomeArtists() {
  const row = document.getElementById("artistRow");
  if (!row) return;

  console.log("🎨 initHomeArtists");

  // 🔥 只负责“触发刷新”，不自己清空
  refreshArtists();
}



  /* =========================
   * 曲风随机播放
   * ========================= */

  let globalAudioPlayer = null;
  let currentPlayToken = 0;

  async function playRandomByGenre(genreSlug, btn) {
  if (btn.dataset.loading === "1") return;

  btn.dataset.loading = "1";
  btn.disabled = true;

  try {
    const container = document.getElementById("genreRow");
    const fallbackUrl =
      container?.dataset.randomUrl ||
      "/recommendation/random_tracks_by_genre/";
    const url = btn.dataset.randomUrl || fallbackUrl;

    const r = await fetch(
      url + "?genre=" + encodeURIComponent(genreSlug),
      { headers: { "X-Requested-With": "XMLHttpRequest" } }
    );

    const data = await r.json();
    const track = data.tracks?.[0];

    if (!track) {
      alert("该曲风暂无可播放曲目");
      return;
    }

    const audioUrl = pickAudioUrl(track);
    if (!audioUrl) {
      alert("该曲风暂无可播放音频");
      return;
    }

    /* =========================
     * 🔥 接入全局播放器（关键）
     * ========================= */

    const fakeBtn = document.createElement("button");
    fakeBtn.className = "js-add-to-player";
    fakeBtn.dataset.autoplay = "true";
    fakeBtn.dataset.trackId = track.id || "";
    fakeBtn.dataset.title = track.title || "";
    fakeBtn.dataset.artists = track.artist || track.artists || "";
    fakeBtn.dataset.audio = audioUrl;
    fakeBtn.dataset.cover = track.cover || "";

    document.body.appendChild(fakeBtn);
    fakeBtn.click();
    fakeBtn.remove();

  } catch (e) {
    console.error(e);
    alert("播放失败，请重试");
  } finally {
    btn.disabled = false;
    btn.dataset.loading = "0";
  }
}


  /* =========================
   * 全站事件委托（关键）
   * ========================= */

  function bindDocumentDelegationOnce() {
  if (document.body.dataset.homeDelegationBound === "1") return;
  document.body.dataset.homeDelegationBound = "1";

  document.addEventListener("click", function (e) {

    /* 🔄 刷新推荐歌曲 */
    const refreshBtn = e.target.closest("#refreshTracks");
    if (refreshBtn) {
      e.preventDefault();
      console.log("🔥 refresh click caught");
      refreshTracks();
      return;
    }

    /* 🔄 刷新热门艺术家 */
    const refreshArtistsBtn = e.target.closest("#refreshArtists");
    if (refreshArtistsBtn) {
      e.preventDefault();
      console.log("🔥 refreshArtists click caught");
      initHomeArtists();
      return;
    }

    /* 🔄 刷新热门曲风 */
    const refreshGenresBtn = e.target.closest("#refreshGenres");
    if (refreshGenresBtn) {
      e.preventDefault();
      console.log("🔥 refreshGenres click caught");
      refreshGenres();
      return;
    }

    /* 🎵 曲风随机播放 */
    const playBtn = e.target.closest(".play-genre");
    if (playBtn) {
      e.preventDefault();
      playRandomByGenre(playBtn.dataset.genre, playBtn);
      return;
    }


  }); // ✅ 结束 addEventListener
}     // ✅ 结束 bindDocumentDelegationOnce



  /* =========================
   * 初始化
   * ========================= */

  document.addEventListener("DOMContentLoaded", function () {
    bindDocumentDelegationOnce();
    initHomeGenres();

    const trackRow = document.getElementById("trackRow");
      if (trackRow) {
        // trackRow.innerHTML = "";
        // console.log("🧹 initial trackRow cleared");
        // refreshTracks();
      }
      initHomeArtists();

  });

  document.addEventListener("DOMContentLoaded", function () {
  const observer = new MutationObserver(() => {
    const artistRow = document.getElementById("artistRow");
    if (artistRow) {
      console.log("👀 artistRow detected, initHomeArtists()");
      initHomeArtists();
      observer.disconnect();
    }
  });

  if (document.body) {
    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }
});

  /* =========================
 * 监听主页内容插入，初始化热门曲风（兜底）
 * ========================= */
document.addEventListener("DOMContentLoaded", function () {
  const observer = new MutationObserver(() => {
    const genreRow = document.getElementById("genreRow");
    if (genreRow) {
      console.log("👀 genreRow detected, initHomeGenres()");
      initHomeGenres();
      observer.disconnect();
    }
  });

  if (document.body) {
    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }
});


})();
