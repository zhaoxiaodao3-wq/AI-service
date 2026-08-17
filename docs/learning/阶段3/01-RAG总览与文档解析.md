# 01 · RAG 总览与文档解析

## 做了什么

阶段 3 实现了完整 RAG 链路：文档上传 → 解析 → 切片 → 向量化 → Qdrant 入库 → 相似度检索 → 注入 Prompt → 流式问答。

文档解析部分支持三种格式：

- TXT：直接按 UTF-8 读取文本。
- MD：按纯文本读取。
- PDF：用 `pypdf` 逐页提取文字。

上传接口 `POST /api/documents` 会把文件元信息（文件名、类型、大小、切片数）保存到 PostgreSQL 的 `documents` 表。

## 为什么

大模型只能看到 Prompt 里的文字，看不到你本地的文档。RAG（Retrieval-Augmented Generation）的思路是：**先把文档切成小块并转成向量，提问时先检索最相关的片段，再把这些片段拼进 Prompt**，让模型“基于文档回答”，而不是凭空发挥。

## 原理

### RAG 五步法

```text
文档解析 → 文本切片 → Embedding 向量化 → 相似度检索 → Prompt 组装 + 生成
```

这五步对应本项目：

1. `document_service.parse_file`：把文件变成纯文本。
2. `chunker.split_text`：把长文本切成 500 字、重叠 50 字的片段。
3. `model_adapter.embed_texts`：每个片段转成 1024 维向量。
4. `vector_repo.search_documents`：问题向量与所有片段向量算相似度。
5. `chat_service` 把命中片段注入系统提示词，再走原有流式对话。

### 为什么文件元信息要落 PG

Qdrant 负责“找内容”，PostgreSQL 负责“管业务”。文档列表、删除记录、切片数量这些管理信息放 PG 更自然；向量和原文片段放 Qdrant，检索时不用扫全表。

## 命令解释

```powershell
$boundary = [guid]::NewGuid().ToString()
$content = "苹果是红色的" -join "`n"
$body = "--$boundary`r`nContent-Disposition: form-data; name=`"file`"; filename=`"知识库.txt`"`r`nContent-Type: text/plain`r`n`r`n$content`r`n--$boundary--`r`n"
Invoke-RestMethod -Uri http://localhost:8000/api/documents -Method Post -ContentType "multipart/form-data; boundary=$boundary" -Body $body
```

PowerShell 手动拼 multipart 比较啰嗦，日常建议直接使用前端上传页。

```powershell
Invoke-RestMethod -Uri http://localhost:8000/api/documents
```

列出已上传文档。

## 避坑

- PDF 扫描件没有文字层，`pypdf` 提取不到内容，接口会提示“未能从文档中提取到文本”。
- 文件大小上限 5MB，避免超大文件把请求拖死。
- 解析文本时用 `errors="replace"`，遇到无法解码的字节不会崩溃。
- 上传接口是同步解析 + 向量化，大文件会比较慢；前端上传请求需要把超时调大（本项目 120s）。
