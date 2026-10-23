(function () {
  const contentTextareaId = 'id_content';
  const uploadUrl = '/admin/blog/upload-image/';

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop().split(';').shift();
    }
    return '';
  }

  function setFallbackStatus(textarea, message, isError) {
    let status = document.getElementById('markdown-editor-status');
    if (!status) {
      status = document.createElement('p');
      status.id = 'markdown-editor-status';
      status.className = 'markdown-editor-status';
      textarea.insertAdjacentElement('afterend', status);
    }
    status.textContent = message;
    status.classList.toggle('is-error', Boolean(isError));
  }

  async function uploadImage(file) {
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
      body: formData,
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || '图片上传失败');
    }

    return payload;
  }

  function createLivePreview(editor) {
    const editorContainer = editor.codemirror.getWrapperElement().closest('.EasyMDEContainer');
    if (!editorContainer || editorContainer.parentElement.classList.contains('markdown-editor-workspace')) {
      return;
    }

    const workspace = document.createElement('div');
    workspace.className = 'markdown-editor-workspace';
    const editingPane = document.createElement('div');
    editingPane.className = 'markdown-editor-pane';
    const previewPane = document.createElement('aside');
    previewPane.className = 'markdown-live-preview';
    previewPane.setAttribute('aria-label', 'Markdown 实时预览');
    previewPane.innerHTML = [
      '<div class="markdown-live-preview-header">实时预览</div>',
      '<div class="markdown-live-preview-body"></div>',
    ].join('');

    editorContainer.parentNode.insertBefore(workspace, editorContainer);
    workspace.appendChild(editingPane);
    editingPane.appendChild(editorContainer);
    workspace.appendChild(previewPane);

    const previewBody = previewPane.querySelector('.markdown-live-preview-body');
    let previewTimer = null;

    function renderLivePreview() {
      const markdown = editor.value();
      previewBody.innerHTML = markdown
        ? editor.markdown(markdown)
        : '<p class="markdown-live-preview-empty">开始写 Markdown 后，这里会实时显示预览。</p>';
    }

    function schedulePreviewRender() {
      window.clearTimeout(previewTimer);
      previewTimer = window.setTimeout(renderLivePreview, 160);
    }

    editor.codemirror.on('change', schedulePreviewRender);
    renderLivePreview();
  }

  function initMarkdownEditor() {
    const textarea = document.getElementById(contentTextareaId);
    if (!textarea || textarea.dataset.markdownEditorBound === 'true') {
      return;
    }
    textarea.dataset.markdownEditorBound = 'true';

    if (!window.EasyMDE) {
      setFallbackStatus(textarea, 'Markdown 编辑器未加载，当前使用普通正文框。', true);
      return;
    }

    const toolbar = [
      {
        name: 'heading',
        action: window.EasyMDE.toggleHeadingSmaller,
        className: 'mde-icon mde-heading',
        title: '标题',
      },
      {
        name: 'bold',
        action: window.EasyMDE.toggleBold,
        className: 'mde-icon mde-bold',
        title: '加粗',
      },
      {
        name: 'italic',
        action: window.EasyMDE.toggleItalic,
        className: 'mde-icon mde-italic',
        title: '斜体',
      },
      {
        name: 'quote',
        action: window.EasyMDE.toggleBlockquote,
        className: 'mde-icon mde-quote',
        title: '引用',
      },
      {
        name: 'code',
        action: window.EasyMDE.toggleCodeBlock,
        className: 'mde-icon mde-code',
        title: '代码块',
      },
      '|',
      {
        name: 'unordered-list',
        action: window.EasyMDE.toggleUnorderedList,
        className: 'mde-icon mde-ul',
        title: '无序列表',
      },
      {
        name: 'ordered-list',
        action: window.EasyMDE.toggleOrderedList,
        className: 'mde-icon mde-ol',
        title: '有序列表',
      },
      '|',
      {
        name: 'link',
        action: window.EasyMDE.drawLink,
        className: 'mde-icon mde-link',
        title: '链接',
      },
      {
        name: 'upload-image',
        action: function (editor) {
          editor.openBrowseFileWindow();
        },
        className: 'mde-icon mde-upload-image',
        title: '上传图片',
      },
      {
        name: 'image',
        action: window.EasyMDE.drawImage,
        className: 'mde-icon mde-image',
        title: '图片链接',
      },
      '|',
      {
        name: 'preview',
        action: window.EasyMDE.togglePreview,
        className: 'mde-icon mde-preview no-disable',
        title: '预览',
      },
      {
        name: 'side-by-side',
        action: window.EasyMDE.toggleSideBySide,
        className: 'mde-icon mde-side-by-side no-disable no-mobile',
        title: '分屏预览',
      },
      {
        name: 'fullscreen',
        action: window.EasyMDE.toggleFullScreen,
        className: 'mde-icon mde-fullscreen no-disable no-mobile',
        title: '全屏写作',
      },
    ];

    const editor = new window.EasyMDE({
      element: textarea,
      forceSync: true,
      spellChecker: false,
      autoDownloadFontAwesome: false,
      placeholder: '在这里写 Markdown。可以粘贴截图，或把图片拖进编辑器自动上传。',
      minHeight: '520px',
      previewImagesInEditor: true,
      uploadImage: true,
      imageMaxSize: 1024 * 1024 * 20,
      imageAccept: 'image/png, image/jpeg, image/gif, image/webp',
      imageUploadFunction: async function (file, onSuccess, onError) {
        try {
          const payload = await uploadImage(file);
          onSuccess(payload.url);
        } catch (error) {
          onError(error.message);
        }
      },
      imageTexts: {
        sbInit: '可粘贴截图、拖拽图片，或点击图片上传按钮。',
        sbOnDragEnter: '松开即可上传图片。',
        sbOnDrop: '正在上传 #images_names#',
        sbProgress: '正在上传 #file_name#: #progress#%',
        sbOnUploaded: '已上传 #image_name#',
        sizeUnits: ' B, KB, MB',
      },
      errorMessages: {
        noFileGiven: '请选择要上传的图片',
        typeNotAllowed: '只能上传 PNG、JPG、GIF 或 WebP 图片',
        fileTooLarge: '图片 #image_name# 太大，最大支持 #image_max_size#。',
        importError: '图片 #image_name# 上传失败。',
      },
      toolbar,
      status: ['upload-image', 'lines', 'words', 'cursor'],
      renderingConfig: {
        singleLineBreaks: false,
      },
    });

    const form = textarea.closest('form');
    if (form) {
      form.addEventListener('submit', () => {
        editor.codemirror.save();
      });
    }

    createLivePreview(editor);
    window.postContentMarkdownEditor = editor;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMarkdownEditor);
  } else {
    initMarkdownEditor();
  }
})();
