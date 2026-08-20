# 03 · CI/CD 流水线与 GHCR 镜像（push 一下，测试构建全自动）

## 这一步做了什么

新增 GitHub Actions 流水线（`.github/workflows/ci.yml`），三个 Job 分工：

| Job | 干什么 | 触发 |
|-----|--------|------|
| `backend-test` | 装依赖 + 跑 pytest 全部单测 | 每次 push / PR |
| `frontend-build` | pnpm 装依赖 + 类型检查 + vite 构建 | 每次 push / PR |
| `docker-push` | 构建 backend/frontend 镜像 → 推 GHCR | push 到 main/master |

**镜像仓库用 GHCR（GitHub Container Registry）**：镜像存在你的 GitHub 账号下，推送权限由 GitHub 自动注入的 `GITHUB_TOKEN` 控制，**不需要手动配置任何 Secrets**。

## 为什么要这么做（用"出厂质检流水线"打比方）

没有 CI 时，代码合并靠人肉：

```text
本地改了代码 → 忘了跑测试 → push 上去 → 同事一跑就崩
```

CI 就是给代码加了一条**出厂质检流水线**：

```text
你 git push
  → 自动：装环境 → 跑测试 → 前端构建（质检）
  → 质检通过 → 自动构建镜像 → 推到 GHCR（出厂入库）
  → 全绿，你才放心部署
```

好处：

- **测试必跑**：每次提交自动全量测试，坏代码进不了主线（或者一眼看到红了）。
- **构建必验**：前端类型错误、依赖缺失，push 时就暴露，而不是部署时才炸。
- **镜像自动产出**：部署服务器直接拉 GHCR 镜像，不用每台机器都装编译环境。

## 底层原理

### 1. 流水线文件结构（.github/workflows/ci.yml）

GitHub Actions 流水线 = YAML 文件，核心是 `jobs`（多个任务，可并行）：

```yaml
name: CI
on:
  push:
    branches: [main, master]   # push 到主分支触发
  pull_request:                # 开 PR 也触发

jobs:
  backend-test:
    runs-on: ubuntu-latest     # 跑在 GitHub 的 Linux 虚拟机上
    defaults:
      run:
        working-directory: backend   # 后续命令都在 backend/ 下执行
    steps:
      - name: Checkout
        uses: actions/checkout@v4    # 把仓库代码拉到虚拟机
      - name: Setup Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run pytest
        run: python -m pytest -q
```

拆解关键概念：

- **`on`**：触发条件。`push` 到 main/master 或 `pull_request` 都触发。
- **`jobs`**：任务组，多个 job 并行跑（backend 测试和 frontend 构建同时进行，互不等待）。
- **`steps`**：一个 job 里按顺序执行的小步骤，每步要么是 `uses`（用现成 action）要么是 `run`（跑命令）。
- **`actions/*`**：GitHub 官方提供的现成动作（checkout 拉代码、setup-python 装 Python），不用自己写脚本。

### 2. 测试为什么能在 CI 跑（不依赖 Docker）

CI 虚拟机里**没有** PostgreSQL / Redis / Qdrant，为什么 pytest 能过？

因为测试从设计上就隔离了外部依赖：

```python
@pytest.fixture()
def db_session():
    engine = create_engine("sqlite:///:memory:", ...)   # 用内存 SQLite，不碰 PG
    ...
    app.dependency_overrides[get_db] = override_get_db  # 覆盖数据库依赖
```

- 数据库：测试用 SQLite 内存库 + `dependency_overrides` 替换
- Redis（限流/缓存）：中间件有"连不上就降级内存"的兜底
- Qdrant / LLM：测试里全部 monkeypatch 成假实现

所以 CI 里 `pip install -r requirements.txt && pytest` 就能全量跑，不需要起任何容器。

### 3. 构建并推送 GHCR（docker-push Job）

```yaml
docker-push:
  if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || ...)
  runs-on: ubuntu-latest
  permissions:
    packages: write                 # 关键：授予推送镜像的权限
  steps:
    - name: Login to GHCR
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}   # GitHub 自动注入，无需手动配置
    - name: Build and push backend
      uses: docker/build-push-action@v6
      with:
        context: ./backend
        push: true
        tags: |
          ghcr.io/${{ github.repository_owner }}/aigc-backend:latest
          ghcr.io/${{ github.repository_owner }}/aigc-backend:${{ github.sha }}
```

几个关键点：

- **`permissions: packages: write`**：告诉 GitHub 这个 Job 有权限写容器镜像。
- **`secrets.GITHUB_TOKEN`**：每次运行自动生成的临时令牌，**不需要你去 Settings 里配**（这是 GHCR 相比 Docker Hub 最大的便利）。
- **双 tag 策略**：`latest`（最新版，部署用）+ `${{ github.sha }}`（本次提交的哈希，精确定位版本，回滚用）。
- **`github.repository_owner`**：你的 GitHub 用户名，镜像名自动变成 `ghcr.io/你的用户名/aigc-backend`。

## 你要做的操作步骤（GitHub 侧，约 10 分钟）

### 第 1 步：注册 GitHub 并创建仓库

```text
1. 打开 https://github.com ，注册账号（没有的话）
2. 右上角 + → New repository
   - Repository name: 随便起，比如 aigc-ai
   - 建议选 Private（私有仓库，代码不公开）
   - 不要勾选 "Add a README"（避免和本地冲突）
3. 创建完成后，页面会显示远程地址：https://github.com/你的用户名/aigc-ai.git
```

### 第 2 步：本地关联并推送（在本项目目录执行）

```powershell
# 1) 关联远程仓库（替换成你自己的地址）
git remote add origin https://github.com/你的用户名/aigc-ai.git

# 2) 确认当前分支名（git branch 显示 * master 或 * main）
git branch

# 3) 推送（如果分支是 main，把 master 换成 main）
git push -u origin master

# 4) 推送前确保工作区干净：git status 无未提交改动
```

### 第 3 步：看流水线跑起来

```text
1. 打开 GitHub 仓库页面 → 顶部 "Actions" 标签
2. 能看到刚推送触发的 CI 运行：
   - Backend Tests：pytest 全绿 ✓
   - Frontend Build：构建通过 ✓
   - Build & Push Images：镜像已推 GHCR ✓
3. 点进 "Build & Push Images" 展开日志，能看到：
   ghcr.io/你的用户名/aigc-backend:latest 推送成功
```

### 第 4 步：验证镜像在 GHCR 里

```text
GitHub 仓库页面 → 右侧 "Packages" 区块
→ 能看到 aigc-backend / aigc-frontend 两个镜像包
（首次可能需要点 "Make public" 或保持 private——private 时部署服务器拉取需要登录，
  建议部署时在服务器上用 PAT 登录，或直接选 public）
```

## 常见问题与避坑

1. **push 后 Actions 没触发**：检查分支名。`.github/workflows/ci.yml` 监听 `main/master`，如果你本地分支叫别的名字，push 不会触发——改 `on.push.branches` 或把分支改名。
2. **docker-push 报权限错**：检查 Job 里有没有 `permissions: packages: write`，少了这行 GHCR 推送会被拒。
3. **测试在 CI 红但本地绿**：大概率是测试依赖了本机服务。检查测试有没有连真实 Redis/PG——正确做法是像现有测试那样 mock/隔离（SQLite 内存 + dependency_overrides）。
4. **`git push` 前必须提交**：CI 跑的是仓库里的代码，本地未提交的改动不会进流水线。开发节奏：改完 → `git add` → `git commit` → `git push` → 看 Actions。
5. **GHCR 私有包部署时拉取**：服务器 `docker pull ghcr.io/...` 对私有包要登录。简单方案：仓库 → Packages → 镜像 → Settings → 选 Public；或者用 Personal Access Token 登录（见 04 篇）。

## 小结

一句话记住：**CI = push 自动跑"测试+构建"质检，通过后自动把镜像推到 GHCR（GITHUB_TOKEN 自动授权，无需配 Secrets）；你要做的只有建仓库、关联、push、看 Actions 变绿。**
