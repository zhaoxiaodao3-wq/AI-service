# 阶段一观测随项目一键启动 · 开发规格

**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)

## 背景与目标

上一模块把 Loki/Promtail/Grafana 放在独立 `docker-compose.observability.yml`，需要额外 `-f` 参数。用户希望后端项目启动时观测栈一起起来，因此把观测文件纳入主 compose 的 `include`，一条命令启动全部服务。

## 设计

### 1. 主编排集成

在 `docker-compose.yml` 顶部增加：

```yaml
include:
  - docker-compose.observability.yml
```

`include` 会把观测栈的 loki/promtail/grafana 服务合并进主项目，`docker compose up -d --build` 同时启动：

- postgres、qdrant、backend（原有）
- aigc-loki、aigc-promtail、aigc-grafana（观测栈）

### 2. 文档更新

- README：启动命令改为单文件 `docker compose up -d --build`；端口表保留 Grafana/Loki。
- `docs/learning/阶段1/08-实时日志观测平台LokiGrafana.md`：启动命令同步为单命令。

## 验收标准

- [x] `docker compose config --quiet` 通过，且渲染结果包含 loki/promtail/grafana 三个服务。
- [x] `docker compose up -d --build` 能拉起全部服务（已实机验证：backend 构建成功，6 个容器全部 Up）。
- [x] README 与学习文档不再要求 `-f docker-compose.observability.yml`。
- [x] 观测栈配置文件保持独立，不塞进主 compose 正文。

## 非目标

- 不改后端/前端代码。
- 不改观测栈本身的采集逻辑。
