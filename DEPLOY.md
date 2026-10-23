# 部署示例

以下以 Linux、Nginx、Gunicorn 和 SQLite 为例。将项目放到 `/srv/eclipse`，域名 `example.com` 需要换成自己的域名。

## 后端

```bash
cd /srv/eclipse
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(64))"
```

把生成的密钥写入 `backend/.env` 的 `DJANGO_SECRET_KEY`，并填写：

```dotenv
DJANGO_ENV=prod
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
DJANGO_CORS_ORIGINS=
```

同源部署时不需要额外 CORS 来源。真实密钥和 `.env` 不提交仓库。

```bash
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py collectstatic --noinput
.venv/bin/python backend/manage.py createsuperuser
.venv/bin/python backend/manage.py check --deploy
```

开发版数据库不要复制到生产环境，按需在后台录入文章。首次演示时可运行 `seed_demo`。

## 前端与进程

```bash
cd /srv/eclipse/frontend
npm ci
npm run build
cd /srv/eclipse/backend
/srv/eclipse/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

使用 systemd 等进程管理工具保持后端运行；工作目录设为 `/srv/eclipse/backend`。后台用户需要对数据库和 `media` 目录有写权限。

## Nginx 与 HTTPS

项目附带 `nginx.conf.example`，用于已配置 HTTPS 的站点。先设置自己的证书路径和域名，再通过 `nginx -t` 检查后加载。生产配置会强制 HTTPS，并使用安全 Cookie。

网页资源来自 `frontend/dist`，API 和后台转发给 Gunicorn，上传文件由 `/media/` 提供。这里不配置对其他目录的静态访问。

上线后检查首页、三个分区、About、文章配图、后台登录和图片上传。运行数据应单独备份，不能通过提交 Git 的方式备份。
