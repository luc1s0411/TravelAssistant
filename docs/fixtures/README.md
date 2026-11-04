# 固定契约样例

`trip_input.json` 是人工构造的请求样例，用于类型校验与联调讨论，不是已保存草稿或供应商数据。

两人、一间房、三天两晚：住宿分类上限应为 100000 分，美食 60000 分，景点 60000 分。此处仅说明未来规划服务的计算目标，骨架未实现费用计算。

未知价格示例：`{"amount_minor":null,"currency":"CNY","nature":"unknown","unit":"per_person_visit"}`。

免费项目示例：`{"amount_minor":0,"currency":"CNY","nature":"reference","unit":"per_person_visit"}`。
