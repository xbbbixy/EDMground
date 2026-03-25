// static/js/player.js

(function(){
  const playerBar = document.getElementById('global-player');
  const audioEl = document.getElementById('gp-audio');
  const titleEl = document.getElementById('gp-title');
  const artistEl = document.getElementById('gp-artist');
  const coverEl = document.getElementById('gp-cover');

  const btnPrev = document.getElementById('gp-prev');
  const btnPlayPause = document.getElementById('gp-play-pause');
  const btnNext = document.getElementById('gp-next');

  const progressEl = document.getElementById('gp-progress');
  const curTimeEl = document.getElementById('gp-current-time');
  const durTimeEl = document.getElementById('gp-duration');
  const volumeEl = document.getElementById('gp-volume');

  const playlistPanel = document.getElementById('global-player-playlist');
  const playlistListEl = document.getElementById('gp-playlist-list');
  const btnTogglePlaylist = document.getElementById('gp-toggle-playlist');
  const btnClosePlaylist = document.getElementById('gp-close-playlist');

  if (!audioEl) return;

  let playlist = [];   // {id, title, artists, audio, cover, genres: [slug]}
  let currentIndex = -1;
  let isSeeking = false;

  function formatTime(sec){
    if (isNaN(sec) || sec < 0) return '0:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return m + ':' + (s < 10 ? '0' + s : s);
  }

  function renderPlaylist(){
    playlistListEl.innerHTML = '';
    playlist.forEach((track, idx)=>{
      const li = document.createElement('li');
      li.className = 'gp-playlist-item' + (idx === currentIndex ? ' active' : '');
      li.dataset.index = idx;

      const t = document.createElement('div');
      t.className = 'gp-playlist-title';
      t.textContent = track.title;

      const a = document.createElement('div');
      a.className = 'gp-playlist-artist';
      a.textContent = track.artists || '';

      li.appendChild(t);
      li.appendChild(a);
      playlistListEl.appendChild(li);
    });
  }

  function updateMeta(track){
    titleEl.textContent = track.title || '未知曲目';
    artistEl.textContent = track.artists || '';
    coverEl.innerHTML = '';
    if (track.cover){
      const img = document.createElement('img');
      img.src = track.cover;
      img.alt = track.title;
      coverEl.appendChild(img);
    }
  }

  function playIndex(index){
    if (index < 0 || index >= playlist.length) return;
    currentIndex = index;
    const track = playlist[currentIndex];

    if (!track.audio){
      console.warn('Track has no audio url');
      return;
    }

    audioEl.src = track.audio;
    updateMeta(track);
    renderPlaylist();
    audioEl.play().catch(err=>console.warn(err));

    playerBar.classList.remove('hidden');
    btnPlayPause.textContent = '⏸';
  }

  function playNext(autoRecommend = true){
    if (currentIndex + 1 < playlist.length){
      playIndex(currentIndex + 1);
    } else if (autoRecommend){
      autoRecommendTracks();
    }
  }

  function playPrev(){
    if (currentIndex > 0){
      playIndex(currentIndex - 1);
    }
  }

  function addToPlaylist(track, autoPlay = true){

  console.log(
  '[addToPlaylist]',
  track.title,
  'autoPlay =',
  autoPlay,
  'currentIndex =',
  currentIndex
);

  if (!track || !track.audio) return;

  // 已存在的情况
  const existingIndex = playlist.findIndex(
    t => t.id && track.id && t.id === track.id
  );

  // ▶ 播放：如果已存在，直接切到那首
  if (existingIndex !== -1){
    if (autoPlay){
      playIndex(existingIndex);
    }
    return;
  }

  // ===== 插播 / 播放的分水岭 =====

  // ▶ 播放：清空队列，从这首开始
  if (autoPlay){
    playlist = [track];
    currentIndex = 0;
    renderPlaylist();
    playIndex(0);
    return;
  }

  // ＋ 插播：
  // 如果当前有歌在播 → 只入队（不改 currentIndex）
  if (currentIndex !== -1){
    playlist.push(track);
    renderPlaylist();
    console.log('插播加入队列：', track.title);
    return;
  }

  // ＋ 插播但当前没在播 → 直接播放（符合用户直觉）
  playlist.push(track);
  currentIndex = 0;
  renderPlaylist();
  playIndex(0);
}

  function addTracksToPlaylist(tracks, autoPlay = true) {
    if (!Array.isArray(tracks) || tracks.length === 0) return;

    if (autoPlay) {
      playlist = tracks;
      playIndex(0);
    } else {
      playlist.push(...tracks);
      if (currentIndex === -1) {
        playIndex(0);
      }
    }
    renderPlaylist();
  }

  // ====== 事件绑定 ======

  btnPlayPause.addEventListener('click', function(){
    if (audioEl.paused) {
      if (currentIndex === -1 && playlist.length > 0){
        playIndex(0);
      } else {
        audioEl.play();
      }
    } else {
      audioEl.pause();
    }
  });

  btnPrev.addEventListener('click', playPrev);
  btnNext.addEventListener('click', ()=>playNext(true));

  audioEl.addEventListener('play', function(){
    btnPlayPause.textContent = '⏸';
  });

  audioEl.addEventListener('pause', function(){
    btnPlayPause.textContent = '▶';
  });

  audioEl.addEventListener('timeupdate', function(){
    if (isSeeking) return;
    const current = audioEl.currentTime || 0;
    const duration = audioEl.duration || 0;
    curTimeEl.textContent = formatTime(current);
    durTimeEl.textContent = formatTime(duration);
    if (duration > 0){
      progressEl.value = (current / duration) * 100;
    } else {
      progressEl.value = 0;
    }
  });

  audioEl.addEventListener('ended', function(){
    playNext(true);
  });

  progressEl.addEventListener('input', function(){
    isSeeking = true;
  });

  progressEl.addEventListener('change', function(){
    const duration = audioEl.duration || 0;
    const percent = parseFloat(progressEl.value) || 0;
    audioEl.currentTime = duration * (percent / 100);
    isSeeking = false;
  });

  volumeEl.addEventListener('input', function(){
    const v = parseInt(volumeEl.value, 10) / 100;
    audioEl.volume = Math.min(1, Math.max(0, v));
  });

  btnTogglePlaylist.addEventListener('click', function(){
    playlistPanel.classList.toggle('hidden');
  });

  btnClosePlaylist.addEventListener('click', function(){
    playlistPanel.classList.add('hidden');
  });

  playlistListEl.addEventListener('click', function(e){
    const item = e.target.closest('.gp-playlist-item');
    if (!item) return;
    const idx = parseInt(item.dataset.index, 10);
    if (!isNaN(idx)){
      playIndex(idx);
    }
  });

  // ====== 把页面上的“播放按钮”接入全局播放器 ======
  document.addEventListener('click',function (e) {
    const btn = e.target.closest('.js-add-to-player');
    if (!btn) return;

    e.preventDefault();

    const track = {
      id: btn.dataset.trackId || null,
      title: btn.dataset.title || '未知曲目',
      artists: btn.dataset.artists || '',
      audio: btn.dataset.audio || '',
      cover: btn.dataset.cover || '',
      genres: (btn.dataset.genres || '').split(',').filter(Boolean)
    };

    const autoPlay = btn.dataset.autoplay !== 'false';
    console.log('[addToPlaylist]', track.title, autoPlay);
    addToPlaylist(track, autoPlay);
  },
  true   // 👈 这一位：捕获阶段（核心）
);

  window.player = {
    addTracksToPlaylist
  };


  // ====== 简单按曲风推荐 ======
  // 思路：根据当前播放歌曲的第一个曲风 slug 去后台要一批推荐
  function autoRecommendTracks(){
    if (playlist.length === 0) return;
    const current = playlist[currentIndex] || playlist[playlist.length - 1];

    const genres = current.genres || [];
    if (!genres.length) return;

    const mainGenre = genres[0];

    const excludeIds = playlist
      .map(t => t.id)
      .filter(Boolean)
      .map(id => 'exclude=' + encodeURIComponent(id))
      .join('&');

    const url = `/recommendation/api/by_genre/?genre=${encodeURIComponent(mainGenre)}&${excludeIds}`;

    fetch(url)
      .then(r => r.json())
      .then(data => {
        if (!data.tracks || !data.tracks.length) return;
        data.tracks.forEach(t => {
          const track = {
            id: t.id,
            title: t.title,
            artists: t.artists,
            audio: t.audio,
            cover: t.cover || '',
            genres: t.genres || []
          };
          // 不自动播放，只加入列表
          addToPlaylist(track, false);
        });
        // 自动播放刚推荐出来的第一首
        if (currentIndex === playlist.length - 1){
          playNext(false);
        }
      })
      .catch(err => console.warn('recommend error', err));
  }

})();


