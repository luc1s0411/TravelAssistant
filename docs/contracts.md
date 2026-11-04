# 公共接口契约（骨架版）

本轮仅提供 DTO、路由和请求封装，不实现业务。权威类型入口是 `backend/app/*/schemas.py`，机器可读快照是 `docs/openapi.json`。前端 `generated.ts` 由快照生成，不手动修改。

## 通用规则

- 前缀 `/api/v1`；字段 snake_case；ID 是不透明字符串。
- 日期 YYYY-MM-DD，活动按 `timezone` 解释；首批时区固定 Asia/Shanghai。
- 金额是严格非负整数分，币种 CNY。`null`=未知，`unlimited:true`=不限，`0`=明确为零。
- 价格使用 `price_min_minor`、`price_max_minor`；未知上下限均为 null，明确免费为上下限均 0，单一已知价格上下限相同。reference 至少有下限，quoted 和 user_entered 必须同时有上下限。
- 坐标字段 longitude / latitude / coordinate_system，当前接口约定 GCJ02。
- 返回 code、message、data、request_id；列表 data 为 items、next_cursor、has_more。默认 20，上限 50。
- Authorization: Bearer <token>；用户 ID 不属于任何资源写入请求体。认证尚未实现，任意 bearer 令牌都不被接受。
- 草稿改动 expected_revision，计划改动 expected_version。业务实现时必须用原子条件更新，不能只在 Python 中比较。
- 添加选择、生成计划、确认修改使用 `Idempotency-Key` 请求头（8—128 字符）。前端生成一次后复用到同一次提交的重试；禁止每次重试生成新键。
- 业务实现时：相同用户、操作范围、键和输入返回同一结果；键相同但输入不同返回 409。
- 当前接口占位返回 501 NOT_IMPLEMENTED，保护接口缺身份返回 401，格式错误返回 422。501 是骨架阶段新增的状态，不能被 UI 当成业务成功。

## 路由分组

| 模块 | 接口 | 负责人 |
| --- | --- | --- |
| 身份 | POST /auth/login、POST /auth/logout、GET /auth/me | A |
| 草稿 | POST /drafts、GET/PATCH /drafts/{draft_id} | A |
| 选择 | POST /drafts/{draft_id}/selections、DELETE /drafts/{draft_id}/selections/{selection_id} | A |
| 候选 | GET /catalog/search、GET /catalog/items/{item_ref} | B |
| 草稿助手 | POST /drafts/{draft_id}/assistant/messages | B，C 整合路由 |
| 确认 | POST /drafts/{draft_id}/confirm | C |
| 计划 | POST/GET /plans、GET/PATCH/DELETE /plans/{plan_id}、GET /plans/{plan_id}/items、GET /planning-requests/{planning_request_id} | C |
| 计划助手 | POST /plans/{plan_id}/assistant/messages | B，C 整合路由 |
| 修改 | POST /plans/{plan_id}/revisions/preview、POST /plans/{plan_id}/revisions/{preview_id}/confirm | C |
| 外部能力 | POST /routes/estimate、GET /weather | B |

## 样例

以下是契约示例，除健康检查和错误响应之外，业务成功示例目前不会由骨架生成。

存活检查 GET /health（不验证 MySQL）：

```json
{"code":"OK","message":"成功","data":{"status":"alive","stage":"scaffold"},"request_id":"example-request"}
```

候选空结果（未来实现）：

```json
{"code":"OK","message":"成功","data":{"items":[],"next_cursor":null,"has_more":false},"request_id":"example-request"}
```

新建草稿：POST /drafts 可提交 `{"trip":{}}`，也可提交 `{"trip": <fixtures/trip_input.json 内容>}`。草稿允许缺少目的地和日期；确认时必须补齐。修改草稿 PATCH /drafts/{id}，提交完整的当前 trip（可以含未补齐的字段）和 expected_revision；不进行不明确的深层字段合并。

确认选择：

```json
{"expected_revision":3,"selection_ids":["selection-example"],"accepted_missing_categories":["dining"]}
```

生成：POST /plans，`Idempotency-Key: example-generate-001`：

```json
{"draft_id":"draft-example","confirmation_id":"confirmation-example"}
```

业务实现后返回 202 和任务数据，例如 `{"request_id":"planning-example","status":"pending","plan_id":null,"error_code":null}`；其中 `data.request_id` 是规划任务 ID，不是响应顶层的跟踪 ID。通过 GET `/planning-requests/{planning_request_id}` 查询本人任务；状态为 `succeeded` 时取得 `plan_id` 再读取计划。相同键和输入的重试须返回同一任务；响应丢失时用相同请求和同一键重试，不生成新任务。

重命名使用 PATCH `/plans/{plan_id}`，请求体为 `{"title":"新名称","expected_version":1}`；DELETE `/plans/{plan_id}?expected_version=1` 表示从用户列表归档，保留历史，确认操作由调用方在提交前完成。两者均须检查归属和当前版本；计划生成版本号只代表行程版本，重命名和归档之间的并发处理仍须业务层明确定义。

版本冲突（未来实现）：

```json
{"code":"VERSION_CONFLICT","message":"草稿已改变，请刷新并重新确认","data":{"expected_revision":3,"current_revision":4},"request_id":"example-request"}
```

当前占位错误：

```json
{"code":"NOT_IMPLEMENTED","message":"该能力尚未实现，当前仅为工程骨架","data":{"feature":"planner.list_owned"},"request_id":"example-request"}
```

其他预留错误：400 请求错误、404 不存在或不可访问、409 版本/幂等冲突、429 并发限制、502 上游失败、503 数据库不可用、504 超时。尚未实现的限流、幂等和权限业务校验不得据此视为已完成。

## 后续冻结事项

真实认证方案与退出失效机制、候选引用有效期和可保存字段、模型供应商、价格有效期、营业时段、天气与路线数据结构细节、计划助手的结构化查询结果、修改范围表达。

这些是后续业务开发的契约扩展点，当前骨架不假定最终产品能力已经齐备。

## ORM 映射及仍受限事项

数据库模型以用户提供的 `backend/app/db/models.py` 为准。分类、坐标类型和价格已提供纯转换函数，业务服务仍未实现：

- 分类：API 使用 `dining`，ORM 使用 `food`；坐标系 API 为 `GCJ02`，ORM 使用 `gcj02`。需要双向转换。
- 价格：API 的上下限、计价单位及 JSON 条件对应 ORM 的 `price_min_minor`、`price_max_minor`、`price_unit` 和 `price_conditions`。每餐或每次等具体计价口径在条件中明确标记，不能自行推测；已知小计区间和未知项目分开表达。
- 计划项目：API 支持 `rest` 和 `free_time`、可空 `selection_id` 及价格；不能将未确认的商家作为用户选择加入。
- 状态、时间、偏好：草稿状态不是 ORM 枚举的一一映射；实现须结合输入完整性、确认和规划任务状态推导并测试。API 本地日期及时间须结合 `Asia/Shanghai` 转为带时区 UTC；偏好列表与 ORM JSON 的映射需要保持可逆。
- 固定开始时间：选择接口已有 `start_time`，但 ORM 没有明确字段。用户要求暂不改数据库结构，**不得声称该字段已持久保存**；实现前需另定可验证的持久化方案。
- 幂等：规划请求可考虑将完整键按操作范围生成 SHA-256 摘要后存入 64 字符字段，并另以 `request_hash` 校验输入；但选择及修改确认缺少通用的持久化幂等记录。用户要求暂不改数据库结构，三类操作的完整持久化幂等尚无经过验证的实现，不能截断键或仅依赖进程内缓存。

服务层须实际调用转换函数，其余状态转换和并发语义仍须实现与测试；模型和初始迁移保持原样。详见 [后端开发基线](backend-baseline.md)。
