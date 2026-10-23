# 编辑与发布

当前目录独立于个人博客，是用于修改和审阅的模板准备稿。维护者原创部分已确定采用 Unlicense；公开上传前，还需要处理 `THIRD_PARTY_NOTICES.md` 中的动效来源问题。

## 先编辑这些文件

1. `README.md`：项目介绍、运行方式和想展示的功能。
2. `frontend/.env.example` 和 `frontend/src/config/site.js`：公开默认站点名、标语和配置。
3. `backend/demo/posts.json`：别人首次运行时看到的示例文章。
4. `frontend/public/demo/`：公开示例素材；`frontend/public/wallpaper/`：选入的 About 与 Gallery 背景视频。
5. `LICENSE` / `LICENSE_SCOPE.md`：原创部分采用 Unlicense，第三方代码保留各自许可，不要删除第三方版权声明。

后台编辑的数据存在本地数据库中，不会自动变成源码里的示例。想让别人首次安装也看到你的新示例，需要修改 `backend/demo/posts.json`，不要提交数据库。

## 文件检查

在项目根目录执行：

```bash
python tools/check_release.py
git status --short
git diff --cached --stat
```

检查脚本会报告数据库、真实环境文件、私钥和常见凭据模式。忽略目录仍然留在自己的电脑上，不能把整个运行目录直接压缩上传。脚本不能代替查看自己新加的图片、视频和文章。

## 打包本地审阅稿

```bash
python tools/package_release.py
```

这会在项目的上一级目录生成 `Eclipse-template-review.zip`，只打包源码和公开示例，排除数据库、上传文件、依赖、构建产物及 Git 历史。该压缩包仍是待审阅稿，生成它不表示第三方分发条件已经确认。

## 上传仓库

等内容和第三方分发条件确认后，在 GitHub 新建空仓库，再使用 GitHub Desktop 的 Add local repository，或在当前目录执行：

```bash
git add .
git diff --cached --stat
git commit -m "Initial template release"
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY.git
git push -u origin main
```

仓库地址换成自己的地址。这里不会预先设置远程仓库、执行推送，或把个人博客的历史记录带过来。

后续只有这个目录作为模板仓库维护；不要把个人博客数据库、文章图片、部署密钥和私有备份同步进来。
