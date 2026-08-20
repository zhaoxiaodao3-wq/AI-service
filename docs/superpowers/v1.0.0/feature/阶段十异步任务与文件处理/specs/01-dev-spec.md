# 阶段十异步任务与文件处理 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 设计

### 1. 基础设施

- 新增 `redis:7-alpine` 服务。
- 新增 `aigc-worker` 容器：与 backend 同一镜像，运行 `rq worker aigc-tasks`。
- 共享卷 `uploads_data`：backend 写入临时文件，worker 读取处理。

### 2. 数据模型

`DocumentTask` 表：

- `document_id`、`status`（pending/processing/completed/failed）
- `error`、`file_path`、`created_at`、`updated_at`

### 3. 上传流程

```text
POST /api/documents
  → 保存临时文件
  → 创建 Document（pending）
  → 创建 DocumentTask
  → 入队 RQ 任务 → 立即返回

worker:
  → 解析 → 切片 → Embedding → Qdrant → PG chunks
  → 更新任务 completed / failed
```

### 4. 接口

- `GET /api/documents/{id}/task`：返回任务状态。
- `GET /api/documents`：列表带最新任务状态。

### 5. 前端

上传后轮询任务状态，展示“解析中/向量化中/完成/失败”。

## 验收标准

- [x] 上传立即返回，不阻塞请求。
- [x] worker 能完成解析/切片/向量化/入库。
- [x] 任务状态可查询，失败有 error。
- [x] 前端展示处理进度。
- [x] `pytest -q`（32 passed）与 `pnpm build` 通过。
- [x] 学习文档 2 篇齐全。

## 非目标

- 不做批量导入/增量更新 UI（阶段可扩展）。
