# 阶段八Agent工具增强 · 交付归档

**归档类型：** feature 交付快照
**归档日期：** 2026-08-17
**版本：** v1.0.0
**Requirement:** [../requirements/01-原始需求.md](../requirements/01-原始需求.md)
**Spec:** [../specs/01-dev-spec.md](../specs/01-dev-spec.md)

## 改动摘要

新增两个免费实用工具：`get_weather`（wttr.in 实时天气）与 `convert_currency`（open.er-api 实时汇率），模型开启“工具”后可直接调用并基于结果回答。

## 改动文件

| 操作 | 路径 |
|------|------|
| 改 | `backend/app/tools/builtin.py`（天气/汇率工具） |
| 改 | `backend/app/tools/registry.py`（注册两个新工具） |
| 改 | `backend/tests/test_tools.py`（注册列表断言） |
| 新增 | `docs/learning/阶段8/04-高级工具.md` |
| 新增 | `docs/superpowers/v1.0.0/feature/阶段八Agent工具增强/`（requirements/spec/plans/archive） |

## 验收结果

- [x] 工具列表包含 `get_weather` 与 `convert_currency`。
- [x] 聊天开启工具后能查询天气并回答。
- [x] 聊天开启工具后能换算汇率并回答。
- [x] 网络失败时不阻塞聊天。
- [x] `pytest -q`（30 passed）与 `pnpm build` 通过。

## 一致性自检

| 检查项 | 结果 | 证据（路径或说明） |
|--------|------|-------------------|
| 空态 vs 有数据 | 通过 | 参数缺省时返回友好提示；有参数返回真实数据 |
| 常量/mock/真数据 | 通过 | 天气/汇率均为真实免费 API 联调 |
| 多入口 | 通过 | 与其他工具共用 Agent 循环与 SSE 事件 |
| 失败/缺省 | 通过 | 网络/解析失败返回提示，不抛错 |

## 还原度自检

不适用：无 Figma / 非 UI 还原类需求。

## Harness 闭环

- [x] 模块目录四层齐全（requirements/specs/plans/archive）
- [x] requirements / spec / plan 链接正确
- [x] 改 `src/` 前 validate-harness 已跑（阶段 READY_TO_DEV 后开发）
- [x] spec 验收项已勾选
- [x] 一致性自检已完成并写入 archive
- [x] 还原度自检已注明不适用
- [x] archive 交付快照已写
- [x] 交付后 `pnpm harness:check` 已跑，无本模块警告

## 验证证据

- 后端测试：`pytest -q` → 30 passed。
- Docker 实测：
  - 天气：`get_weather` 返回“北京 当前天气：Patchy rain nearby，10°C...”。
  - 汇率：`convert_currency` 返回“100.0 USD = 674.8651 CNY”。
  - SSE 均输出 `tool_start/tool_done`，最终回答 200。
- 学习文档：`docs/learning/阶段8/04-高级工具.md`。

## 遗留风险

- 免费天气/汇率接口可能有频次限制或源站策略变化，生产建议加缓存与备用源。
