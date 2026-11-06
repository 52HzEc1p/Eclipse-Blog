const { test } = require('node:test');
const assert = require('node:assert/strict');
const MarkdownIt = require('../static/blog/vendor/markdown-it/markdown-it.min.js');
const createPreserver = require('../static/blog/admin/markdown_preservation.js');

test('an originally unclosed fence must not swallow newly added prose', () => {
  const source = '```python\nprint(1)\n';
  const rendered = '```python\nprint(1)\n```\n';
  const edited = rendered + '\n新增正文\n';
  const preserve = createPreserver(new MarkdownIt(), source, rendered);
  assert.equal(preserve(edited), edited);
});

test('prose changes preserve untouched code whitespace without undoing code edits', () => {
  const source = '# 原文\n\n```python\nprint("[已打码]")\n        \n```\n';
  const rendered = '# 原文\n\n```python\nprint("[已打码]")\n      \n```\n';
  const preserve = createPreserver(new MarkdownIt(), source, rendered);
  assert.equal(preserve(rendered + '\n新增说明\n'), source + '\n新增说明\n');
  const editedCode = rendered.replace('print(', 'log(');
  assert.equal(preserve(editedCode), editedCode);
});

test('ambiguous duplicate code blocks are not replaced with an arbitrary original', () => {
  const source = '```text\nx\n    \n```\n\n```text\nx\n  \n```\n';
  const rendered = '```text\nx\n\n```\n\n```text\nx\n\n```\n';
  const preserve = createPreserver(new MarkdownIt(), source, rendered);
  assert.equal(preserve(rendered + '\n说明'), rendered + '\n说明');
});
