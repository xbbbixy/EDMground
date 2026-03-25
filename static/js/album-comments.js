console.log('🔥 album-comment.js loaded');

document.addEventListener('DOMContentLoaded', () => {

  // ===== 发表评论 =====
  document.addEventListener('submit', function (e) {
    const form = e.target.closest('.js-comment-form');
    if (!form) return;

    e.preventDefault();

    const formData = new FormData(form);
    const url = form.action;

    fetch(url, {
      method: 'POST',
      body: formData,
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(res => res.text())
    .then(() => {
      // 简单方案：刷新评论区（稳）
      location.reload();
    })
    .catch(err => {
      console.error('评论失败', err);
    });
  });

});

// ===== 回复评论 =====
document.addEventListener('submit', function (e) {
  const form = e.target.closest('.js-reply-form');
  if (!form) return;

  e.preventDefault();

  const formData = new FormData(form);
  const url = form.action;

  fetch(url, {
    method: 'POST',
    body: formData,
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.text())
  .then(() => {
    location.reload();
  })
  .catch(err => {
    console.error('回复失败', err);
  });
});

// ===== 点赞评论 =====
document.addEventListener('click', function (e) {
  const btn = e.target.closest('.btn-like-comment');
  if (!btn) return;

  e.preventDefault();

  const url = btn.dataset.url;

  fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(res => res.json())
  .then(data => {
    const span = btn.querySelector('span');
    if (span) {
      span.textContent = data.likes_count;
    }
    btn.classList.toggle('liked', data.liked);
  })
  .catch(err => {
    console.error('点赞失败', err);
  });
});
function getCSRFToken() {
  const name = 'csrftoken';
  const cookies = document.cookie.split(';');
  for (let c of cookies) {
    const cookie = c.trim();
    if (cookie.startsWith(name + '=')) {
      return cookie.substring(name.length + 1);
    }
  }
  return '';
}
