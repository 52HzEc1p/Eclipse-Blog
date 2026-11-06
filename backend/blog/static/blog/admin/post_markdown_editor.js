(function () {
  'use strict';
  function init() {
    const receiptKey = 'blog:article-pending-save';
    // Run on the list/add/change response, after Django confirms a successful save.
    try {
      const receipt = JSON.parse(sessionStorage.getItem(receiptKey) || 'null');
      if (receipt && Date.now() - receipt.time < 300000 &&
          /^\/admin\/blog\/post\/(?:\d+\/change\/|add\/)?$/.test(location.pathname) &&
          document.querySelector('.messagelist .success')) {
        if (receipt.raw && localStorage.getItem(receipt.key) === receipt.raw) localStorage.removeItem(receipt.key);
        sessionStorage.removeItem(receiptKey);
      }
    } catch (_) { /* A blocked cache must not prevent editing. */ }
    const textarea = document.getElementById('id_content');
    const layout = document.getElementById('studio-layout');
    if (!textarea || !layout) return;
    const form = textarea.closest('form');
    const status = document.getElementById('studio-save-status');
    const notice = document.getElementById('studio-draft-notice');
    const settingsButton = document.getElementById('studio-toggle-settings');
    const original = textarea.value;
    const key = `blog:article-draft:${layout.dataset.user}:${layout.dataset.post}`;
    const owner = Array.from(crypto.getRandomValues(new Uint32Array(4)), value => value.toString(16)).join('-');
    const hasErrors = Boolean(form.querySelector('.errornote, .errorlist'));
    let editor, initialRendered = '', initialForm, timer, pendingDraft, pendingRaw;
    let ready = false, submitting = false, uploading = false, changedBody = false;
    let preserveMarkdown = value => value;

    function showStatus(message, error = false) {
      status.textContent = message;
      status.classList.toggle('is-error', error);
    }
    function snapshot() {
      return { title: document.getElementById('id_title').value,
        excerpt: document.getElementById('id_excerpt').value,
        content: ready && changedBody ? preserveMarkdown(editor.getValue()) : textarea.value };
    }
    const saved = snapshot();
    function formFingerprint() {
      const fields = [...new FormData(form).entries()]
        .filter(([name]) => name !== 'csrfmiddlewaretoken' && name !== 'tags' && name !== 'tags_old' && !name.startsWith('_'))
        .map(([name, value]) => [name, value instanceof File ? (value.name ? `${value.name}:${value.size}:${value.lastModified}` : '') : value]);
      const chosen = window.SelectBox?.cache?.id_tags_to;
      const tags = chosen ? chosen.map(item => item.value) : [...(document.getElementById('id_tags')?.selectedOptions || [])].map(option => option.value);
      fields.push(['tags', tags.sort().join(',')]);
      return JSON.stringify(fields);
    }
    function removeDraft(force = false) {
      try {
        if (force) { localStorage.removeItem(key); return; }
        const existing = JSON.parse(localStorage.getItem(key) || 'null');
        if (existing?.owner === owner) localStorage.removeItem(key);
      } catch (_) { /* Storage may be disabled. */ }
    }
    function persistDraft() {
      if (pendingDraft) return;
      const value = snapshot();
      if (JSON.stringify(value) === JSON.stringify(saved) && !hasErrors) {
        removeDraft();
        showStatus(formFingerprint() === initialForm ? '内容已与服务器同步' : '文章设置有未保存修改');
        return;
      }
      try {
        const existing = JSON.parse(localStorage.getItem(key) || 'null');
        if (existing && existing.owner !== owner && ['content', 'title', 'excerpt'].some(field => existing[field] !== value[field])) {
          restoreNotice();
          if (pendingDraft) return;
        }
        localStorage.setItem(key, JSON.stringify({ ...value, owner, time: Date.now(), revision: layout.dataset.revision }));
        showStatus('未保存 · 标题、摘要和正文已备份到本机');
      } catch (_) { showStatus('本机草稿不可用，请及时保存文章', true); }
    }
    function syncBody() {
      if (!ready) return;
      changedBody = editor.getValue() !== initialRendered;
      textarea.value = changedBody ? preserveMarkdown(editor.getValue()) : original;
    }
    function onChange() {
      if (!ready) return;
      syncBody();
      window.clearTimeout(timer);
      timer = window.setTimeout(persistDraft, 500);
      showStatus(pendingDraft ? '请先恢复或丢弃旧草稿，再继续自动备份' : '有未保存修改');
    }
    settingsButton.addEventListener('click', () => {
      const open = layout.classList.toggle('settings-open');
      settingsButton.setAttribute('aria-expanded', String(open));
    });
    function restoreNotice() {
      try {
        const raw = localStorage.getItem(key);
        const draft = raw ? JSON.parse(raw) : null;
        if (!draft || !['content', 'title', 'excerpt'].every(field => typeof draft[field] === 'string') ||
            !Number.isFinite(draft.time) || Date.now() - draft.time > 7 * 86400000) {
          if (raw) removeDraft(true);
          return;
        }
        const matches = draft.title === saved.title && draft.excerpt === saved.excerpt &&
          (draft.content === original || draft.content === initialRendered);
        if (matches && !hasErrors) { removeDraft(true); return; }
        if (matches && hasErrors) {
          // The bound form already contains this failed submission; keep backing up corrections.
          localStorage.setItem(key, JSON.stringify({ ...draft, owner }));
          return;
        }
        pendingDraft = draft;
        pendingRaw = raw;
        notice.hidden = false;
        document.getElementById('studio-draft-description').textContent =
          `${new Date(draft.time).toLocaleString('zh-CN')} 的标题、摘要和正文。` +
          (draft.revision !== layout.dataset.revision ? '服务器版本已有变化；恢复将替换编辑区，保存后才会写入服务器。' : '恢复只替换编辑区，点击保存文章后才会写入服务器。');
        showStatus('发现本地草稿，等待选择');
      } catch (_) { showStatus('本机草稿无法读取，请及时保存文章', true); }
    }
    function draftChoiceStillCurrent() {
      try {
        if (localStorage.getItem(key) === pendingRaw) return true;
        pendingDraft = null;
        notice.hidden = true;
        restoreNotice();
        showStatus('草稿已在其他标签页更新，请重新选择恢复或丢弃');
      } catch (_) { showStatus('无法读取草稿，请保留当前页面并保存文章', true); }
      return false;
    }
    document.getElementById('studio-restore-draft').addEventListener('click', () => {
      if (!pendingDraft || !ready || !draftChoiceStillCurrent()) return;
      const draft = pendingDraft;
      document.getElementById('id_title').value = draft.title;
      document.getElementById('id_excerpt').value = draft.excerpt;
      editor.setValue(draft.content);
      removeDraft(true);
      pendingDraft = null;
      notice.hidden = true;
      onChange();
    });
    document.getElementById('studio-discard-draft').addEventListener('click', () => {
      if (!pendingDraft || !draftChoiceStillCurrent()) return;
      pendingDraft = null;
      notice.hidden = true;
      removeDraft(true);
      persistDraft();
    });

    const uploadStatus = document.createElement('p');
    uploadStatus.className = 'studio-upload-status';
    uploadStatus.setAttribute('role', 'status');
    uploadStatus.hidden = true;
    textarea.after(uploadStatus);
    const imageInput = document.createElement('input');
    imageInput.type = 'file';
    imageInput.accept = 'image/png,image/jpeg,image/gif,image/webp';
    imageInput.multiple = true;
    imageInput.hidden = true;
    imageInput.dataset.editorUpload = 'true';
    textarea.after(imageInput);

    async function uploadImages(files) {
      if (!ready || uploading) return '请等待当前图片上传完成';
      const images = Array.from(files);
      if (!images.length) return null;
      uploadStatus.hidden = false;
      uploadStatus.classList.remove('is-error');
      const selection = window.getSelection();
      const range = selection.rangeCount ? selection.getRangeAt(0).cloneRange() : null;
      uploading = true;
      editor.disabled();
      const submitButtons = [...form.querySelectorAll('[type="submit"]')];
      submitButtons.forEach(button => { button.disabled = true; });
      try {
        for (let index = 0; index < images.length; index++) {
          const file = images[index];
          if (!/^image\/(png|jpeg|gif|webp)$/.test(file.type)) throw new Error('只支持 PNG、JPG、GIF 和 WebP 图片。');
          if (file.size > 20 * 1024 * 1024) throw new Error('单张图片不能超过 20 MB。');
          uploadStatus.textContent = `正在上传 ${index + 1}/${images.length}：${file.name}，请稍候…`;
          const data = new FormData();
          data.append('image', file);
          const response = await fetch(layout.dataset.upload, {
            method: 'POST', credentials: 'same-origin', body: data,
            headers: { 'X-CSRFToken': form.querySelector('[name="csrfmiddlewaretoken"]').value },
            signal: AbortSignal.timeout(60000),
          });
          if (response.redirected || !response.headers.get('content-type')?.includes('application/json')) {
            throw new Error('登录可能已过期。请在新标签页登录后台，再重试上传。');
          }
          const payload = await response.json();
          if (!response.ok) throw new Error(payload.error || `上传失败（${response.status}），请重试。`);
          if (typeof payload.url !== 'string' || !payload.url.startsWith('/media/')) throw new Error('上传返回了无效的图片地址。');
          editor.enable();
          if (index === 0 && range && range.startContainer.isConnected && document.getElementById('article-editor').contains(range.startContainer)) {
            selection.removeAllRanges(); selection.addRange(range);
          } else { editor.focus(); }
          const alt = file.name.replace(/\.[^.]+$/, '').replace(/[\\\[\]\r\n]/g, ' ');
          editor.insertValue(`\n![${alt}](${payload.url.replace(/\(/g, '%28').replace(/\)/g, '%29')})\n`);
          onChange();
          editor.disabled();
        }
        uploadStatus.textContent = `已插入 ${images.length} 张图片，保存文章后生效。`;
        return null;
      } catch (error) {
        const message = error.name === 'TimeoutError' ? '上传超时，请重试。' : (error.message || '图片上传失败，请重试。');
        uploadStatus.textContent = message;
        uploadStatus.classList.add('is-error');
        return message;
      } finally {
        uploading = false;
        editor.enable();
        submitButtons.forEach(button => { button.disabled = false; });
        imageInput.value = '';
      }
    }
    imageInput.addEventListener('change', () => uploadImages(imageInput.files));
    form.addEventListener('input', event => { if (!event.target.closest('#article-editor')) onChange(); });
    form.addEventListener('change', event => { if (!event.target.closest('#article-editor') && event.target !== imageInput) onChange(); });
    form.addEventListener('submit', event => {
      if (uploading) { event.preventDefault(); return; }
      syncBody();
      window.clearTimeout(timer);
      if (ready) persistDraft();
      try {
        // Never claim a conflicting draft belongs to this submission.
        const raw = localStorage.getItem(key);
        if (raw && JSON.parse(raw).owner === owner) {
          sessionStorage.setItem(receiptKey, JSON.stringify({ key, raw, time: Date.now() }));
        } else { sessionStorage.removeItem(receiptKey); }
      } catch (_) { /* Server-side saving works without local storage. */ }
      submitting = true;
    });
    window.addEventListener('beforeunload', event => {
      if (submitting) return;
      if (ready) { syncBody(); persistDraft(); }
      if (uploading || hasErrors || formFingerprint() !== initialForm) {
        event.preventDefault(); event.returnValue = '';
      }
    });
    document.addEventListener('keydown', event => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
        event.preventDefault();
        if (!uploading) form.requestSubmit(form.querySelector('[name="_continue"]'));
      }
    });
    initialForm = formFingerprint();
    if (!window.Vditor || !window.markdownit || !window.createMarkdownPreserver) { showStatus('编辑器未加载，仍可使用下方 Markdown 正文框', true); return; }
    const host = document.createElement('div');
    host.id = 'article-editor';
    textarea.before(host);
    const fallback = window.setTimeout(() => {
      if (!ready) { host.hidden = true; showStatus('编辑器加载失败，请刷新；下方 Markdown 正文框仍可编辑', true); }
    }, 15000);
    const isDark = () => document.documentElement.dataset.theme === 'dark' ||
      (document.documentElement.dataset.theme === 'auto' && matchMedia('(prefers-color-scheme: dark)').matches);
    try {
      editor = new window.Vditor(host, {
        value: original, mode: 'ir', lang: 'zh_CN', cdn: layout.dataset.vendor,
        cache: { enable: false }, height: 'calc(100vh - 300px)', minHeight: 480,
        placeholder: '开始写作。输入 # 写标题，粘贴截图或拖入图片。',
        theme: isDark() ? 'dark' : 'classic', icon: 'ant', toolbarConfig: { pin: false },
        outline: { enable: window.innerWidth > 1200, position: 'left' },
        counter: { enable: false }, resize: { enable: false }, fullscreen: { index: 1200 },
        toolbar: ['headings', 'bold', 'italic', 'strike', '|', 'list', 'ordered-list', 'quote', 'code', 'inline-code', 'link',
          { name: 'upload-photo', tip: '上传图片', icon: '<svg><use xlink:href="#vditor-icon-upload"></use></svg>', click: () => imageInput.click() },
          'table', '|', 'undo', 'redo', '|', 'outline', 'edit-mode', 'fullscreen'],
        preview: {
          delay: 200, maxWidth: 900, mode: 'editor',
          markdown: { autoSpace: false, fixTermTypo: false, sanitize: true, inlineMath: false, mathBlockPreview: false, footnotes: false, toc: false, mark: false },
          hljs: { enable: true, lineNumber: false },
          theme: { current: isDark() ? 'dark' : 'light', path: `${layout.dataset.vendor}/dist/css/content-theme` },
        },
        upload: { handler: uploadImages, accept: imageInput.accept, max: 20 * 1024 * 1024 },
        input: onChange,
        after() {
          window.clearTimeout(fallback);
          host.hidden = false;
          initialRendered = editor.getValue();
          preserveMarkdown = window.createMarkdownPreserver(window.markdownit(), original, initialRendered);
          const loadingEdits = textarea.value;
          if (loadingEdits !== original) editor.setValue(loadingEdits);
          ready = true;
          textarea.hidden = true;
          document.body.classList.add('studio-ready');
          if (hasErrors) { layout.classList.add('settings-open'); settingsButton.setAttribute('aria-expanded', 'true'); }
          showStatus(hasErrors ? '保存未成功，请检查标红的字段' : '内容已与服务器同步', hasErrors);
          restoreNotice();
          window.postContentMarkdownEditor = editor;
          if (loadingEdits !== original) onChange();
          new MutationObserver(() => editor.setTheme(isDark() ? 'dark' : 'classic', isDark() ? 'dark' : 'light'))
            .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
        },
      });
    } catch (_) {
      window.clearTimeout(fallback); host.hidden = true;
      showStatus('编辑器初始化失败，仍可使用 Markdown 正文框', true);
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
