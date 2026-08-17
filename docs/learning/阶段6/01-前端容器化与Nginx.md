# 01 · 前端容器化与 Nginx

## 做了什么

前端新增多阶段 Dockerfile：

```text
node:22-alpine（安装依赖 + pnpm build）
        ↓ dist
nginx:1.27-alpine（托管静态资源 + /api 代理）
```

## 为什么

Vite dev server 只适合开发。生产部署需要：

- 静态资源由 Nginx 高效托管。
- `/api` 请求代理到后端容器，前端不直接暴露后端端口。
- SPA 路由（`/chat`、`/upload`）刷新时由 `try_files` 回退到 `index.html`。
- SSE 流式输出不能被 Nginx 缓冲，必须 `proxy_buffering off`。

## 原理

### 多阶段构建

构建阶段和运行阶段分开，镜像里只保留 `dist` 和 Nginx，不包含 node_modules，体积更小。

### Nginx 配置

```nginx
location /api/ {
    proxy_pass http://backend:8000;
    proxy_buffering off;
}

location / {
    try_files $uri $uri/ /index.html;
}
```

## 命令解释

```powershell
docker compose build frontend
docker compose up -d frontend
```

构建并启动前端容器，访问 http://localhost:5173。

## 避坑

- `proxy_buffering off` 不能省，否则打字机效果会变成一次性输出。
- 前端构建依赖 pnpm lockfile，Dockerfile 用 `--frozen-lockfile` 保证可复现。
- 端口映射 `5173:80`，保持和开发环境一致的访问地址。
