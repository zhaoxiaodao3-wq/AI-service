# Superpowers 工作流落地指南

## 快速开始

1. **建目录（Windows 双击）**
   ```
   scripts\create-demand.bat
   ```
   按提示选择分类、输入中文模块名并确认。

   或命令行：
   ```bash
   ./scripts/create-demand.sh --type feature --name "登录注册功能"
   ```

2. **写入原始需求**
   ```
   docs/superpowers/current/feature/登录注册功能/requirements/你的需求.md
   ```

3. **开发准备与执行**
   ```
   brainstorming  → specs/01-dev-spec.md
   writing-plans  → plans/01-dev-plan.md
   开发            → src/...
   ```

正式产物路径：

```
docs/superpowers/current/feature/登录注册功能/
  requirements/figma-login-page.md   # 原始需求
  specs/01-dev-spec.md               # 开发规格
  plans/01-dev-plan.md               # 执行计划
  archive/                           # 历史与交付归档
```

---

## 目录结构

```
docs/superpowers/
├── current -> v1.0.0
├── current-version.txt    # 软链接回退
├── SUPERPOWERS_RULES.md   # AI 前置规则
├── v1.0.0/
│   ├── feature/
│   │   └── {中文模块}/
│   │       ├── requirements/   # 原始需求
│   │       ├── archive/        # 归档
│   │       ├── specs/
│   │       └── plans/
│   ├── ui-style/
│   ├── api-adapter/
│   └── fix/
└── specs/ plans/ archive/ reports/   # 存量，只读
```

---

## 版本切换

### 方式一：双击交互初始化（Windows 推荐）

双击运行：

```
scripts\init-version.bat
```

按提示逐步操作：
1. 查看当前版本
2. 输入新版本号（如 `v1.1.0`）
3. 预览将创建的目录
4. 确认创建
5. 选择是否将 `current` 切换到新版本

### 方式二：命令行

```bash
./scripts/create-demand.sh --init-version --version v1.1.0
```

然后手动更新 `docs/superpowers/current-version.txt` 为 `v1.1.0`，或创建软链接：

```bash
cd docs/superpowers && ln -sfn v1.1.0 current   # macOS/Linux
mklink /D current v1.1.0                       # Windows
```

### 归档说明

旧版本（如 `v1.0.0/`）上线后冻结，禁止新增模块。

---

## 分类选择

| 分类 | 适用场景 |
|------|----------|
| `feature` | 新页面、新业务能力 |
| `ui-style` | UI 还原、视觉改版 |
| `api-adapter` | 接口对接、字段转换 |
| `fix` | Bug、兼容性修复 |

---

## 归档操作

### 版本级（外层）

迭代上线后冻结整个 `vX.X/`，`current` 指向新版本。

### 需求级（内层）

| 时机 | 操作 |
|------|------|
| spec/plan 大改 | 旧版 → `archive/vN-{slug}/` |
| 交付验收 | 快照 → `archive/vN-delivered/` |

---

## 三套自动化方案

| 方案 | 场景 | 用法 |
|------|------|------|
| AI 对话 | 日常单人 | 见 `SUPERPOWERS_RULES.md` §3 模板 |
| Shell/Bat | 团队/CI | `./scripts/create-demand.sh` |
| create-demand-dir 技能 | 工作流嵌入 | brainstorming 前自动调用 |

---

## 风险规避

| 风险 | 处理 |
|------|------|
| Git 中文路径转义 | `git config core.quotepath false` |
| Windows 软链接权限 | 开启开发者模式，或用 `current-version.txt` |
| 终端乱码 | PowerShell UTF-8；Bat 已设 `chcp 65001` |
| AI 索引过深 | 搜索范围限定 `docs/superpowers/current/` |

---

## 常见问题

**Q: 能否继续往 `docs/superpowers/specs/` 写文档？**  
A: 不能。新需求必须写入 `vX.X/{type}/{模块}/`。

**Q: 原始需求和 spec 有什么区别？**  
A: `requirements/` 放产品/Figma 初稿；`specs/` 是 brainstorming 整理后的开发规格。

**Q: 旧目录是 `v1.0`、`v1.1` 两位格式怎么办？**  
A: 脚本会自动兼容查找；建议关闭占用文件后手动重命名为 `v1.0.0`、`v1.1.0` 等三位格式。

**Q: `current` 切换后旧链接失效？**  
A: 文档内用相对路径；禁止硬编码 `current` 或具体版本号。
