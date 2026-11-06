# 文章编辑器回归检查

运行 Django 测试使用独立测试数据库。浏览器检查使用临时上传目录，所有编辑、上传和保存都作用于测试副本。

```powershell
# 在项目根目录安装独立的浏览器测试工具；需要本机 Chrome。
npm install --prefix _private/editor-test-tools playwright
$env:PLAYWRIGHT_MODULE = (Resolve-Path '_private/editor-test-tools/node_modules/playwright').Path
node --test backend/blog/browser_tests/markdown_preservation.test.cjs
Set-Location backend
..\.venv\Scripts\python.exe manage.py test blog accounts --noinput
```

不设置 `PLAYWRIGHT_MODULE` 时，仅跳过浏览器检查。浏览器测试占用本机 18001 端口。

可选：将 `EDITOR_COMPATIBILITY_FIXTURE` 设置为 UTF-8 JSON 文件的绝对路径，内容为 `[{"content":"Markdown 正文"}]`。测试会创建文章副本，检查保存再打开、修改说明文字后代码块和图片引用的保留情况。

编辑器依赖在 `static/blog/vendor/` 本地提供：Vditor 4.0.1、markdown-it 14.2.0，保留各自许可证。无需运行前端构建即可使用后台编辑器。

本地草稿按用户与文章区分，保留七天，恢复范围是标题、摘要和正文；发布设置和上传文件需手动保存。草稿恢复不会自动发布文章。
