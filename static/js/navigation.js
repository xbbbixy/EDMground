/**
 * navigation.js
 * SPA 导航（DOM 替换 + 页面级 CSS 同步）
 */

(function () {
  const contentEl = document.getElementById("page-content");
  if (!contentEl) return;

  // ===== 工具：解析 HTML =====
  function parseHTML(htmlText) {
    const parser = new DOMParser();
    return parser.parseFromString(htmlText, "text/html");
  }

  // ===== 工具：同步页面级 CSS =====
  function syncPageCSS(newDoc) {
    const head = document.head;

    // 1️⃣ 当前页面已有的“页面级 CSS”
    const currentLinks = Array.from(
      head.querySelectorAll('link[rel="stylesheet"][data-page-css]')
    );

    // 2️⃣ 新页面需要的“页面级 CSS”
    const newLinks = Array.from(
      newDoc.querySelectorAll('link[rel="stylesheet"]')
    ).filter((link) => !link.hasAttribute("data-global-css"));

    // 3️⃣ 新页面 CSS href 列表
    const newHrefs = newLinks.map((l) => l.getAttribute("href"));

    // 4️⃣ 移除旧页面不需要的 CSS
    currentLinks.forEach((link) => {
      if (!newHrefs.includes(link.getAttribute("href"))) {
        link.remove();
      }
    });

    // 5️⃣ 添加新页面缺失的 CSS
    newLinks.forEach((link) => {
      const href = link.getAttribute("href");
      if (!href) return;

      const exists = head.querySelector(
        `link[rel="stylesheet"][href="${href}"]`
      );
      if (exists) {
        exists.remove();
      }

      const newLink = document.createElement("link");
      newLink.rel = "stylesheet";
      newLink.href = href;
      newLink.setAttribute("data-page-css", "1");
      head.appendChild(newLink);
      void document.body.offsetHeight;
    });
  }

  function syncPageJS(newDoc) {
  const body = document.body;

  // 1️⃣ 当前页面已有的页面级 JS
  const currentScripts = Array.from(
    body.querySelectorAll('script[data-page-js]')
  );

  // 2️⃣ 新页面需要的页面级 JS
  const newScripts = Array.from(
    newDoc.querySelectorAll('script[data-page-js]')
  );

  console.log('[SPA] page scripts found:', newScripts.map(s => s.src));

  // 3️⃣ 新页面 JS 的 src 列表
  const newSrcs = newScripts.map(s => s.getAttribute('src'));

  // 4️⃣ 移除旧页面不需要的 JS
  currentScripts.forEach(script => {
    if (!newSrcs.includes(script.getAttribute('src'))) {
      script.remove();
    }
  });

  // 5️⃣ 插入新页面 JS（始终重新执行）
  newScripts.forEach(script => {
    const src = script.getAttribute('src');
    if (!src) return;

    const newScript = document.createElement('script');
    newScript.src = src;
    newScript.defer = true;
    newScript.setAttribute('data-page-js', '1');
    body.appendChild(newScript);
  });
}

  // ===== 工具：重置页面 JS 状态 =====
  function resetPageStates() {
    delete window.__LIKE_INITED__;
    delete window.__COMMENT_INITED__;
    delete window.__FAVORITE_INITED__;
  }

  // ===== 核心 SPA 跳转 =====
  function spaNavigate(url, pushState) {
    if (!url) return;

    // 支持 /path 和 ?page=2 这种
    if (!url.startsWith("/") && !url.startsWith("?")) {
      window.location.href = url;
      return;
    }

    fetch(url, {
      credentials: "same-origin",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Network error");
        return res.text();
      })
      .then((htmlText) => {
        const doc = parseHTML(htmlText);

        const newPage = doc.querySelector(".page-container");
        const title = doc.querySelector("title");

        if (!newPage) {
          window.location.href = url;
          return;
        }

        // ✅ 同步页面级 CSS
        syncPageCSS(doc);



        // ✅ 同步页面级 JS
        syncPageJS(doc);

        // ✅ 替换 DOM
        contentEl.innerHTML = "";
        contentEl.appendChild(newPage);

        if (location.pathname === '/' || location.pathname === '/home') {
          const body = document.body;

          // 1️⃣ 临时禁用所有过渡，避免闪烁
          body.classList.add('force-layout');

          // 2️⃣ 读取布局信息，强制 reflow
          void body.offsetHeight;

          // 3️⃣ 下一帧恢复
          requestAnimationFrame(() => {
            body.classList.remove('force-layout');
          });
        }

        if (
          window.initLibraryPage &&
          location.pathname.startsWith('/library')
        ) {
          window.initLibraryPage();
          window.initArtistsListPage();
        }

        if (
          window.initArtistDetailTabs &&
          location.pathname.startsWith("/artists/")
        ) {
          window.initArtistDetailTabs();
        }

        if (title) document.title = title.innerText;

        if (pushState) history.pushState({}, "", url);

        resetPageStates();
        window.scrollTo(0, 0);
      })
      .catch(() => {
        window.location.href = url;
      });
  }

  // ===== 点击拦截 =====
  document.addEventListener("click", function (e) {
    const link = e.target.closest("a");
    if (!link) return;

    if (
      e.defaultPrevented ||
      e.button !== 0 ||
      e.metaKey ||
      e.ctrlKey ||
      e.shiftKey ||
      e.altKey
    ) {
      return;
    }

    if (!link.classList.contains("js-spa-link")) return;

    const url = link.getAttribute("href");
    if (!url || url.startsWith("#")) return;

    // 排除你已有的特殊规则
    if (url.includes("/community/post/")) return;

    e.preventDefault();
    spaNavigate(url, true);
  });

  // 浏览器前进 / 后退
  window.addEventListener("popstate", function () {
    spaNavigate(location.pathname, false);
  });
})();
