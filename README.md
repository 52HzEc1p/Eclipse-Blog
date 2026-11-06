# Eclipse/日蚀

[先看看实际效果：52HzEc1p](https://52hzec1p.cn/)

Eclipse 是我花了一周做的个人博客模板，基于 Vue 3、Vite 和 Django，开发时用了 Codex、Kimi 和 Astra。首页用魔眼眨眼动画开场，整体偏赛博风格，动效比较多。内容分成三个栏目，可以按自己的需要安排，文章和页面文案通过 Django 后台编辑。

**[下载服务器部署包](https://github.com/52HzEc1p/Eclipse-Blog/releases/download/v0.1.0/Eclipse-Blog-a868489-deploy.zip)** · [查看版本说明](https://github.com/52HzEc1p/Eclipse-Blog/releases/tag/v0.1.0) · [源码部署说明](DEPLOY.md)

![Eclipse 首页示例](docs/screenshots/home.png)

[Articles](docs/screenshots/ctf.png) · [Projects](docs/screenshots/editing.png) · [Gallery](docs/screenshots/games.png) · [About](docs/screenshots/about.png)

> 我拥有版权的原创部分采用 [Unlicense](LICENSE)，允许自由使用、修改、分发和商用，不要求署名，修改后也不必继续开源。第三方组件有各自的许可，不能一并按 Unlicense 处理。动效组件的来源和分发条件还在核对，具体见 [许可范围](LICENSE_SCOPE.md) 和 [第三方说明](THIRD_PARTY_NOTICES.md)。

## 界面与功能

- 首页：WebGL 魔焰眼睛，搭配聚焦文字、发光卡片和流体导航。
- Articles：支持分类、分页和 Markdown，阅读时可以查看代码高亮、文章目录和阅读进度。
- Projects / Gallery：用作品卡片、视频链接和动态背景展示内容。
- About：个人介绍、卡片和联系方式都能在后台修改。
- 管理后台：保存草稿、发布文章、管理分类和标签，也能上传图片。正文使用 Vditor Markdown 编辑器，支持即时渲染、源码模式、全屏和本机草稿恢复。

模板里放的是虚构的示例文章、程序生成的几何配图和演示动画。About 和 Gallery 保留了从原站选入的两段背景视频，个人博客的数据库、账号、私人文章和原始文章截图没有放进来。

## 下载与服务器部署

想把博客放到服务器上，再登录后台写文章、改内容，下载部署包就可以。

| 下载方式 | 适合用途 | 包含内容 |
|---|---|---|
| [服务器部署包（v0.1.0）](https://github.com/52HzEc1p/Eclipse-Blog/releases/download/v0.1.0/Eclipse-Blog-a868489-deploy.zip) | 部署博客，平时在后台更新内容 | Django 后端、已生成的网页文件 `frontend/dist`、示例素材和部署说明 |
| 克隆仓库或下载源码（Source code） | 修改前端配置、布局和动效，继续开发 | 项目源码，需要自己安装前端依赖并构建 |

部署包已经带好了网页文件，首次部署不用在服务器上安装 Node.js，也不用执行 `npm run build`。后端仍需要 Python 3.12+，按 `backend/requirements.txt` 安装依赖；网站需要配置 Nginx 和 HTTPS。

部署时按下面的顺序操作，详细命令在包内说明中：

1. 下载 `Eclipse-Blog-a868489-deploy.zip`，把包内 `Eclipse-Blog` 文件夹里的内容放到服务器的项目目录。
2. 按包内 `README.md` 安装 Python 依赖，在 `backend/.env` 里填写密钥、域名和可信的 HTTPS 来源地址。
3. 运行数据库迁移并收集静态文件，用 `createsuperuser` 创建管理员账号。想先看看示例文章，可以运行 `seed_demo`。
4. 配置 Gunicorn，让后端持续运行。再按 `nginx.conf.example` 设置 Nginx，把网站根目录设为 `frontend/dist`，并配置 HTTPS。
5. 打开 `https://你的域名/admin/`，登录后修改内容、保存，再刷新前台页面查看。

日常更新可以直接在后台完成：写文章、改摘要和封面、填写视频链接、设置发布状态、管理分类和标签，也能修改 About 介绍、联系方式，以及栏目页的标题、描述和筛选项。首页栏目卡片会使用后台填写的栏目标题和描述。这些内容保存后刷新页面就能看到，不用重新构建前端。

全站名称、首页主标题和标语、备案号、导航名称、社交链接和背景视频配置，目前还需要在前端修改。布局、样式和动效也一样。要改这些内容，需要下载源码，修改后重新构建，再替换服务器上的 `frontend/dist`。后台 About 页的“站点名”只会改动 About 页面。

下载时留意文件名：带 `deploy` 的是部署包，GitHub 自动生成的 `Source code (zip)` 是源码，里面没有构建好的网页文件。使用源码部署时，按 [DEPLOY.md](DEPLOY.md) 操作。

如果服务器上已经有博客，更新前先备份 `backend/.env`、`backend/db.sqlite3` 和 `backend/media/`，替换代码时保留这些文件。

## 源码版：本地运行

本地运行源码需要 Python 3.12+ 和 Node.js 22.12+。先在项目根目录执行下面的命令。

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
.\.venv\Scripts\python.exe backend/manage.py migrate
.\.venv\Scripts\python.exe backend/manage.py seed_demo
.\.venv\Scripts\python.exe backend/manage.py createsuperuser
.\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8000
```

后端启动后，另开一个终端启动前端：

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py seed_demo
.venv/bin/python backend/manage.py createsuperuser
.venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

后端启动后，另开一个终端，进入 `frontend`，依次执行 `npm ci`、`cp .env.example .env` 和 `npm run dev`。

- 前台：<http://127.0.0.1:5173>
- 后台：<http://127.0.0.1:8000/admin/>
- 项目没有预设管理员或默认密码，用 `createsuperuser` 创建自己的账号后再登录。
- `seed_demo` 可以重复执行，不会覆盖已有文章。示例文章可以在后台删除。
- 开发环境没有设置密钥时，会临时生成一个随机密钥，重启后需要重新登录。想保留登录状态，可以在本地 `.env` 中设置自己的密钥。

## 从哪里替换为自己的博客（建议直接使用agent辅助替换）

| 要改的内容                  | 位置                                                                                                                  |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| 站点名、首页标题、标语、备案号、导航社交链接 | `frontend/.env`，参照 `.env.example`                                                                                   |
| 站点分享标题和描述              | `frontend/index.html`                                                                                               |
| 文章、分类、标签、About、分区文案    | Django 管理后台                                                                                                         |
| 导航栏目名称                 | `frontend/src/components/common/NavBar.vue`；首页卡片与页面标题见对应页面及 `router/index.js`                                       |
| 默认示例文章                 | `backend/demo/posts.json`                                                                                           |
| 主题颜色、字体和基础样式           | `frontend/src/styles/main.scss`                                                                                     |
| 各页布局、动效参数              | `frontend/src/views/` 和 `frontend/src/components/effects/`                                                          |
| About / Gallery 背景     | `frontend/public/wallpaper/aboutme.mp4` / `elden-ring-wallpaper.mp4`；可通过 `VITE_ABOUT_VIDEO` / `VITE_GAMES_VIDEO` 替换 |
| 示例作品视频                 | `frontend/public/demo/ambient.mp4`                                                                                  |
| 服务端密钥、域名               | `backend/.env`                                                                                                      |

`VITE_*` 配置会随网页发送到浏览器，里面不能放密码或服务端密钥。改完前端环境变量后，开发时要重启服务，部署时要重新构建。

字体默认从 Google Fonts 加载，加载失败时会使用本地字体。需要完全离线使用的话，可以删除 `index.html` 中的远程字体链接，或把字体放到自己的服务器上。

## 检查和构建

```bash
python backend/manage.py check
python backend/manage.py test blog accounts
node --test backend/blog/browser_tests/markdown_preservation.test.cjs
cd frontend
npm run check:nav
npm run build
```

这里的 Python 命令要用前面创建的虚拟环境执行。服务器部署步骤见 [DEPLOY.md](DEPLOY.md)，发布前如何整理文件见 [PUBLISHING.md](PUBLISHING.md)。

后台编辑器需要的文件已经放在源码里，不用从外部 CDN 加载。如果没有修改正文，保存时会保留原来的 Markdown。本机草稿按用户和文章分别保存，保留七天；恢复草稿会带回标题、摘要和正文，之后仍要手动保存文章。浏览器回归检查的运行方法见 [编辑器测试说明](backend/blog/browser_tests/README.md)。

## 目录

```text
backend/            Django API、后台、数据库迁移和示例内容
frontend/           Vue 页面、样式、动效与示例素材
tools/              示例素材生成、发布检查与打包工具
licenses/           第三方许可证原文
```

SQLite 数据库、上传文件、真实 `.env`、安装的依赖和构建结果都不放进模板源码，已在 `.gitignore` 中排除。

三个栏目默认叫 Articles（文章）、Projects（作品）和 Gallery（影像），可以按自己的内容安排使用。About 里的姓名、身份、介绍和联系地址都是示例，使用前记得替换。

内部标识和路径暂时保留了 `ctf`、`editing`、`games`，栏目内容不必照着这些名字来写。新安装时的页面初始内容放在 `backend/blog/migrations/`，API 的备用文案放在 `backend/blog/models.py`，前端各页面也有备用文案。已经运行的博客，直接在后台修改栏目文案即可。
