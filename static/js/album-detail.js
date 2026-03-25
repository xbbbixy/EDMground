(function() {
  document.addEventListener('click', function(e) {
    const playBtn = e.target.closest('.js-play-album');
    const queueBtn = e.target.closest('.js-queue-album');

    if (!playBtn && !queueBtn) return;

    e.preventDefault();

    const tracks = Array.from(document.querySelectorAll('.track-row')).map(row => {
      const btn = row.querySelector('.js-add-to-player');
      if (!btn) return null;

      return {
        id: btn.dataset.trackId || null,
        title: btn.dataset.title || '未知曲目',
        artists: btn.dataset.artists || '',
        audio: btn.dataset.audio || '',
        cover: btn.dataset.cover || '',
        genres: (btn.dataset.genres || '').split(',').filter(Boolean)
      };
    }).filter(Boolean);

    if (tracks.length === 0) {
      alert('该专辑暂无歌曲可播放');
      return;
    }

    // 假设全局播放器有一个 addToPlaylist(tracks, autoPlay) 的方法
    // autoPlay = true  -> 清空并播放
    // autoPlay = false -> 追加到队列
    if (window.player && typeof window.player.addTracksToPlaylist === 'function') {
      const autoPlay = !!playBtn; // 点击“播放专辑”时为 true
      window.player.addTracksToPlaylist(tracks, autoPlay);
    } else {
      console.error('播放器功能未找到');
    }
  });
})();
