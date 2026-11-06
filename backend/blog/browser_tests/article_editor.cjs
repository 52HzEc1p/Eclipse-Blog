const assert = require('node:assert/strict');
const fs = require('node:fs');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE);

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  let page;
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.route('**/*', route => {
      const target = new URL(route.request().url());
      return target.origin === process.env.EDITOR_TEST_URL ? route.continue() : route.abort();
    });
    await context.addCookies([{ name: 'sessionid', value: process.env.EDITOR_TEST_SESSION, url: process.env.EDITOR_TEST_URL }]);
    page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const url = `${process.env.EDITOR_TEST_URL}/admin/blog/post/${process.env.EDITOR_TEST_POST}/change/`;
    await page.goto(url);
    await page.waitForLoadState('networkidle');
    assert.equal(await page.locator('.vditor-ir [contenteditable="true"]').count(), 1,
      'Article body should support Typora-style inline editing');
    await page.waitForFunction(() => window.postContentMarkdownEditor?.getValue);
    assert.match(await page.locator('.vditor-ir').innerText(), /已打码/);
    assert.equal(await page.locator('.vditor-ir table').count(), 1);
    assert.match(await page.locator('.vditor-ir').innerText(), /print\("\[REDACTED\]"\)/);

    // Saving untouched content must not normalize or rewrite the stored Markdown.
    const original = await page.locator('#id_content').inputValue();
    await page.locator('input[name="_continue"]').first().click();
    await page.waitForLoadState('networkidle');
    assert.equal(await page.locator('#id_content').inputValue(), original);

    // Switching modes and fullscreen must preserve code and redacted text.
    await page.locator('button[data-type="edit-mode"]').click();
    await page.locator('button[data-mode="sv"]').click();
    assert.equal(await page.evaluate(() => window.postContentMarkdownEditor.getCurrentMode()), 'sv');
    assert.match(await page.locator('.vditor-sv').inputValue(), /\[REDACTED\]/);
    await page.locator('button[data-type="edit-mode"]').click();
    await page.locator('button[data-mode="ir"]').click();
    await page.locator('button[data-type="fullscreen"]').click();
    assert.equal(await page.locator('.vditor--fullscreen').count(), 1);
    await page.locator('button[data-type="fullscreen"]').click();

    const otherTab = await context.newPage();
    await otherTab.goto(url);
    await otherTab.waitForLoadState('networkidle');
    const body = page.locator('.vditor-ir [contenteditable="true"]');
    await body.click();
    await page.keyboard.press('Control+End');
    await page.keyboard.press('Enter');
    await page.keyboard.type('draft recovery sentinel');
    await page.waitForFunction(() => Object.keys(localStorage).some(key => key.startsWith('blog:article-draft:') && localStorage[key].includes('draft recovery sentinel')));
    await otherTab.goto(`${process.env.EDITOR_TEST_URL}/admin/blog/post/`);
    assert.ok(await page.evaluate(() => Object.keys(localStorage).some(key => key.startsWith('blog:article-draft:') && localStorage[key].includes('draft recovery sentinel'))),
      'An unchanged second tab must not delete another tab\'s draft');
    await otherTab.close();
    page.once('dialog', dialog => dialog.accept());
    await page.reload();
    await page.waitForLoadState('networkidle');
    assert.equal(await page.getByRole('button', { name: '恢复草稿', exact: true }).isVisible(), true);
    assert.doesNotMatch(await body.innerText(), /draft recovery sentinel/);
    // A recovery notice must not overwrite a newer draft written after it was shown.
    const newerRaw = await page.evaluate(() => {
      const key = Object.keys(localStorage).find(key => key.startsWith('blog:article-draft:'));
      const draft = JSON.parse(localStorage.getItem(key));
      draft.content += '\n来自其他标签页的新版本\n';
      draft.time += 1000;
      const raw = JSON.stringify(draft);
      localStorage.setItem(key, raw);
      return raw;
    });
    await page.getByRole('button', { name: '恢复草稿', exact: true }).click();
    assert.doesNotMatch(await body.innerText(), /draft recovery sentinel/);
    assert.ok(await page.evaluate(raw => Object.values(localStorage).includes(raw), newerRaw));
    await page.getByRole('button', { name: '恢复草稿', exact: true }).click();
    assert.match(await body.innerText(), /draft recovery sentinel/);
    assert.match(await body.innerText(), /来自其他标签页的新版本/);
    await body.click();
    await page.keyboard.press('Control+End');
    await page.keyboard.press('Enter');
    await page.keyboard.insertText('恢复后的正文');

    // Upload through the real staff-only endpoint and insert an image in the body.
    await page.locator('input[type="file"][data-editor-upload]').setInputFiles({
      name: '截图-打码验证.png', mimeType: 'image/png',
      buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=', 'base64')
    });
    await page.waitForFunction(() => window.postContentMarkdownEditor.getValue().includes('/media/content/'));
    assert.doesNotMatch(await page.evaluate(() => window.postContentMarkdownEditor.getValue()), /%25E[0-9A-F]/i,
      'Storage URLs must not have percent escapes double-encoded');
    await page.locator('input[name="_continue"]').first().click();
    await page.waitForLoadState('networkidle');
    assert.match(await page.locator('#id_content').inputValue(), /恢复后的正文/);
    assert.equal(await page.getByRole('button', { name: '恢复草稿', exact: true }).isVisible(), false);
    assert.equal(await page.locator('.vditor-ir img').count(), 1);
    await page.waitForFunction(() => [...document.querySelectorAll('.vditor-ir img')].every(image => image.complete));
    assert.ok(await page.locator('.vditor-ir img').evaluate(image => image.naturalWidth > 0), 'Uploaded Chinese filenames must resolve to a working image URL');

    // Rejected uploads must keep the body and leave saving usable.
    const beforeFailure = await page.evaluate(() => window.postContentMarkdownEditor.getValue());
    await page.route('**/admin/blog/upload-image/', route => route.fulfill({ status: 500, contentType: 'application/json', body: '{"error":"测试上传失败"}' }));
    await page.locator('input[data-editor-upload]').setInputFiles({ name: 'failed.png', mimeType: 'image/png', buffer: Buffer.from('failed') });
    await page.locator('.studio-upload-status.is-error').waitFor();
    assert.equal(await page.evaluate(() => window.postContentMarkdownEditor.getValue()), beforeFailure);
    assert.equal(await page.locator('input[name="_continue"]').first().isEnabled(), true);
    await page.unroute('**/admin/blog/upload-image/');

    // Validation errors must retain text and expose the settings needed to fix them.
    await page.locator('#id_title').fill('');
    await page.locator('input[name="_continue"]').first().click();
    await page.waitForLoadState('networkidle');
    assert.equal(await page.locator('.errornote').count(), 1);
    assert.match(await page.locator('#id_content').inputValue(), /恢复后的正文/);
    assert.equal(await page.locator('#studio-settings').isVisible(), true);
    await page.locator('#id_title').fill('编辑器测试副本');
    await page.locator('input[name="_continue"]').first().click();
    await page.waitForLoadState('networkidle');
    assert.equal(await page.locator('.errornote').count(), 0);
    assert.equal(await page.getByRole('button', { name: '恢复草稿', exact: true }).isVisible(), false,
      'Correcting a failed save must clear the draft after a successful retry');
    fs.mkdirSync('../output/playwright', { recursive: true });
    await page.screenshot({ path: '../output/playwright/article-editor-desktop.png', fullPage: false });
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: '../output/playwright/article-editor-mobile.png', fullPage: false });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 2), 'Mobile editor must not overflow horizontally');
    assert.deepEqual(errors, []);

    // A tag-only change also needs a leave-page warning.
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.getByRole('button', { name: '文章设置', exact: true }).click();
    await page.locator('#id_tags_from').selectOption({ label: '浏览器测试标签' });
    await page.locator('#id_tags_add').click();
    assert.equal(await page.evaluate(() => {
      const event = new Event('beforeunload', { cancelable: true });
      window.dispatchEvent(event);
      return event.defaultPrevented;
    }), true, 'Tag-only edits must trigger the unsaved warning');

    // Delay the real parser to test edits made while the fallback textarea is visible.
    const loadingPage = await context.newPage();
    let releaseParser;
    const parserGate = new Promise(resolve => { releaseParser = resolve; });
    await loadingPage.route('**/dist/js/lute/lute.min.js', async route => { await parserGate; await route.continue(); });
    await loadingPage.goto(url, { waitUntil: 'domcontentloaded' });
    await loadingPage.locator('#id_content').fill(original + '\n加载期间输入的正文');
    releaseParser();
    await loadingPage.waitForFunction(() => window.postContentMarkdownEditor?.getValue);
    assert.match(await loadingPage.evaluate(() => window.postContentMarkdownEditor.getValue()), /加载期间输入的正文/,
      'Text entered while the editor loads must survive the handoff');
    await loadingPage.close();

    // A successfully saved new article must not leave a stale "new article" draft.
    const newPage = await context.newPage();
    await newPage.goto(`${process.env.EDITOR_TEST_URL}/admin/blog/post/add/`);
    await newPage.waitForLoadState('networkidle');
    await newPage.locator('#id_title').fill('新建文章测试副本');
    await newPage.getByRole('button', { name: '文章设置', exact: true }).click();
    await newPage.locator('#id_slug').fill('new-editor-check');
    await newPage.locator('#id_section').selectOption('ctf');
    await newPage.locator('.vditor-ir [contenteditable="true"]').click();
    await newPage.keyboard.insertText('新建文章草稿');
    await newPage.waitForFunction(() => Object.keys(localStorage).some(key => key.startsWith('blog:article-draft:') && key.endsWith(':new')));
    await newPage.locator('input[name="_continue"]').first().click();
    await newPage.waitForLoadState('networkidle');
    assert.equal(await newPage.locator('.errornote').count(), 0);
    assert.equal(await newPage.evaluate(() => Object.keys(localStorage).some(key => key.startsWith('blog:article-draft:') && key.endsWith(':new'))), false);
    await newPage.close();
    const MarkdownIt = require('../../../frontend/node_modules/markdown-it');
    const md = new MarkdownIt();
    for (const id of JSON.parse(process.env.EDITOR_COMPATIBILITY_IDS || '[]')) {
      const copyPage = await context.newPage();
      await copyPage.goto(`${process.env.EDITOR_TEST_URL}/admin/blog/post/${id}/change/`);
      await copyPage.waitForLoadState('networkidle');
      const source = await copyPage.locator('#id_content').inputValue();
      const codeBlocks = text => md.parse(text, {}).filter(token => token.type === 'fence' || token.type === 'code_block').map(token => token.content);
      const imageURLs = text => md.parse(text, {}).flatMap(token => token.children || []).filter(token => token.type === 'image').map(token => token.attrGet('src'));
      await copyPage.locator('input[name="_continue"]').first().click();
      await copyPage.waitForLoadState('networkidle');
      assert.equal(await copyPage.locator('#id_content').inputValue(), source, `Untouched article copy ${id} changed on save`);
      await copyPage.locator('.vditor-ir [contenteditable="true"]').click();
      await copyPage.keyboard.press('Control+End');
      await copyPage.keyboard.press('Enter');
      await copyPage.keyboard.press('Enter');
      await copyPage.keyboard.insertText('正文编辑兼容性验证');
      await copyPage.locator('input[name="_continue"]').first().click();
      await copyPage.waitForLoadState('networkidle');
      const edited = await copyPage.locator('#id_content').inputValue();
      assert.match(edited, /正文编辑兼容性验证/);
      assert.deepEqual(codeBlocks(edited), codeBlocks(source), `Unedited code blocks changed in article copy ${id}`);
      assert.deepEqual(imageURLs(edited), imageURLs(source), `Image references changed in article copy ${id}`);
      await copyPage.close();
    }
    console.log('PASS: inline editing, unchanged save, source/fullscreen, draft recovery, uploads/errors, validation, save/reopen, mobile width');
  } catch (error) {
    if (page) {
      fs.mkdirSync('../output/playwright', { recursive: true });
      await page.screenshot({ path: '../output/playwright/article-editor-failure.png' });
      fs.writeFileSync('../output/playwright/article-editor-failure.html', await page.content());
    }
    throw error;
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
