# 03 · Qdrant 向量库原理

## 这一步做了什么

在 Qdrant 里创建了两个专属 Collection（集合）：

- `document_vectors`：阶段 3 存文档知识库切片向量
- `memory_vectors`：阶段 4 存 AI 长期记忆向量

并写好了两个脚本：

- `python -m scripts.init_qdrant`：幂等创建集合，已存在则跳过
- `python -m scripts.check_connections`：一键检查 PostgreSQL 和 Qdrant 连通性

## 为什么要这么做

普通数据库（PostgreSQL）擅长存「文字/数字」并按条件查询，但它不适合做「语义相似度搜索」。

AI 问答需要这种能力：

> 用户问「课程怎么退款」，系统要在上千个文档片段里找出语义上最接近的几个片段。

如果只靠关键词匹配，「怎么退钱」「refund」这类同义表达就找不到了。向量库把文本变成数学向量，用「距离」衡量语义远近，才能解决这个问题。

## 底层原理

### 什么是向量

一段文本经过 Embedding 模型，会变成一个数字数组，例如 `[0.12, -0.34, 0.87, ...]`。这个数组叫向量，维度通常是几百到几千，我们配置为 1536 维。

**关键点**：语义相近的文本，向量在空间里的距离也近。

### 什么是 Collection

Collection 相当于 SQL 数据库里的「表」，是一组向量的集合。每个 Collection 有固定配置：

```python
vectors_config={
    "size": 1536,        # 向量维度
    "distance": "Cosine" # 距离算法
}
```

- `size=1536`：每个向量必须有 1536 个数字
- `distance=Cosine`：用余弦相似度衡量两个向量多「像」

### 为什么分成两个集合

文档知识库和用户记忆是两种完全不同用途的数据：

| 集合 | 存什么 | 什么时候用 |
|------|--------|-----------|
| `document_vectors` | 上传文档的切片 | 文档问答（阶段 3） |
| `memory_vectors` | 历史对话记忆 | 跨会话回忆（阶段 4） |

分开存，检索时互不干扰，按集合名精确定位。

### 幂等是什么

同样的操作执行一次和一百次，结果一样，不会重复创建。脚本里先查「集合是否已存在」，存在就跳过，所以连续运行两次都是安全的。

## 关键命令逐条解释

| 命令 | 含义 |
|------|------|
| `python -m scripts.init_qdrant` | 初始化/确认两个集合存在 |
| `python -m scripts.check_connections` | 检查 PG 和 Qdrant 是否可连接 |
| `python -m scripts.init_qdrant`（再跑一次） | 验证幂等，不报错、不重复创建 |

> 为什么是 `python -m scripts.xxx` 而不是 `python scripts/xxx.py`：后者会把脚本所在目录当作根目录，找不到 `app` 包；用 `-m` 会从 `backend/` 根目录找包，能正确导入 `app.db.qdrant`。

## 常见问题与避坑

1. **客户端/服务端版本警告**：Qdrant 客户端与 Docker 镜像版本要匹配，本项目镜像 `v1.12.4`，客户端锁 `1.12.1`。
2. **集合重复创建报错**：不要直接 `create_collection` 而不检查，脚本里已做幂等处理。
3. **连不上 Qdrant**：先确认 `docker compose ps` 里 `aigc-qdrant` 是 `healthy`，再看 `backend/.env` 的 `QDRANT_URL` 是否是 `http://localhost:6333`。
4. **维度配置要一致**：阶段 3 实际用哪个 Embedding 模型，就必须用它的输出维度，届时会调整 `VECTOR_SIZE`。
