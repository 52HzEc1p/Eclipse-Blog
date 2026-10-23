# 第三方组件与素材

本文件用于区分模板业务代码、第三方动效和安装依赖，不代表所有文件都使用同一种许可证。

## 动效来源核对中

`frontend/src/components/effects/` 中的 Galaxy、GooeyNav 等组件与 [Vue Bits](https://github.com/DavidHDev/vue-bits) / [React Bits](https://github.com/DavidHDev/react-bits) 有代码对应关系，部分包含本项目的调整。

2026-10-19 查看时，上游采用 **MIT + Commons Clause**，当前条款包含对组件本身及模板等形式再分发的限制，不能直接等同于普通 MIT。本地项目没有附带最初引入时的 commit 和许可证，因此当前抓取的许可证仅作为核对材料，不能替代引入版本的证据。

- [Vue Bits 当前条款](https://github.com/DavidHDev/vue-bits/blob/main/LICENSE.md)，本地副本：`licenses/vue-bits.txt`。
- [React Bits 当前条款](https://github.com/DavidHDev/react-bits/blob/main/LICENSE.md)，本地副本：`licenses/react-bits.txt`。
- 在公开发布这个模板前，需要确认原始引入版本的许可、取得适用授权，或独立重写/替换涉及的组件。仅添加署名不自动解决分发范围问题。

## 后台编辑器

`backend/blog/static/blog/vendor/easymde/` 保留 EasyMDE v2.21.0 的原始头部声明。许可证副本位于 `licenses/easymde.txt`，上游为 [EasyMDE](https://github.com/Ionaru/easy-markdown-editor)。其捆绑内容也保留文件内的上游声明。

## 安装依赖

Vue、Vite、Pinia、Three.js、Axios、markdown-it、highlight.js、OGL、Django 等依赖通过包管理器安装，依各自许可证使用。依赖目录不随源码仓库上传。

GSAP 使用其 [Standard License](https://gsap.com/community/standard-license/)，不要把 GSAP 重新标记为 MIT。具体版本以 `frontend/package-lock.json` 为准。

## 模板素材

`frontend/public/demo/` 的三张几何配图和一段无声渐变动画由 `tools/generate_demo_assets.py` 生成。

`frontend/public/wallpaper/aboutme.mp4` 与 `elden-ring-wallpaper.mp4` 由维护者从原站选入，分别用于 About 与 Gallery 背景。两段视频原样保留；素材自身的权利不因本项目的 Unlicense 声明而改变。

字体通过 Google Fonts 获取，没有在本仓库重新分发字体文件。

## 项目本身的许可证

维护者已选择 **Unlicense**，对自己拥有版权的原创部分不要求署名或保留版权声明，也不要求衍生版本开放源码。完整声明见根目录 `LICENSE`，范围见 `LICENSE_SCOPE.md`。

这一选择不改变上述第三方组件的许可。当前目录仍是可编辑的发布准备稿，不能笼统声明“整套无版权限制”；公开分发前仍需处理动效组件的许可问题。
