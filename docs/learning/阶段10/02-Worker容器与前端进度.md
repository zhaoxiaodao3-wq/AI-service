# 02 · Worker 容器与前端进度

## 做了什么

- `docker-compose.yml` 新增 `aigc-worker` 容器与 `redis`。
- 新增 `GET /api/documents/{id}/task` 查询状态。
- 前端上传后轮询任务状态，展示“等待/解析中/完成/失败”。

## 为什么

任务队列必须“有人干活”：worker 容器就是干活的人；前端轮询让用户知道后台没卡住。

## 原理

```text
frontend
  → POST /api/documents → task pending
  → 每 2s GET /documents/{id}/task
  → completed → 刷新列表
```

## 命令解释

```powershell
docker compose logs -f worker
```

观察 worker 消费日志。

## 避坑

- 轮询要设超时上限，避免永久等待。
- worker 失败要写 error 字段，前端显示失败原因。
- 处理成功后删除临时文件，避免上传目录膨胀。
