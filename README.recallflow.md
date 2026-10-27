# RecallFlow｜Agent 长期记忆管理系统

基于开源 Mem0 的本地长期记忆服务。本项目扩展 SDK Provider 与服务配置，打通对话事实提取、向量持久化、按实体范围检索和管理后台。核心记忆算法、认证及管理界面来自上游，不作为个人原创算法。

## 记忆链路

- 写入：对话与最近消息 → 检索已有记忆 → LLM 提取新增事实 → 向量化 → 文本哈希去重 → 持久化。当前采用上游 V3 的 ADD-only 流程，不将显式更新、删除接口描述为自动冲突消解。
- 检索：使用 `user_id`、`agent_id`、`run_id` 约束查询范围，配置 `top_k` 与相关性阈值；上游提供向量、关键词与实体信号评分，过期记忆默认不进入普通检索结果。
- 管理：通过 REST API 显式更新、删除和查询变更历史，按需设置有效期。实体 ID 过滤是数据查询范围，不等同于独立租户的授权边界。

## 本分支改动

| 改动 | 文件 |
| --- | --- |
| 新增文本 Embedding Provider，校验向量类型、维度和有限数值，保留上游 HTTP 错误 | `mem0/embeddings/ark.py` |
| 注册 Provider，统一服务端与 pgvector 的向量维度配置 | `mem0/embeddings/configs.py`、`mem0/utils/factory.py`、`server/main.py` |
| 用本地 SDK 源码构建镜像，避免部署时被上游发行包覆盖 | `server/Dockerfile.local` |
| 编排 API、Dashboard 与 pgvector，端口仅绑定本机，数据通过卷保存 | `server/docker-compose.local.yaml` |
| 增加秘密配置入口、启停脚本和离线适配测试 | `server/configure_ark_local.py`、根目录 `.command` 脚本、`tests/embeddings/ark/test_ark.py` |

## 本地启动

需要 Docker Desktop 与支持 Compose `!override` / `!reset` 标签的版本。现有部署使用 API `8890`、Dashboard `3001`；请先确认端口空闲。

1. 将 `server/.env.recallflow.example` 复制为 `server/.env`。
2. 仅在本机填写模型密钥、数据库密码、管理员 API Key 和 JWT Secret。`ADMIN_API_KEY` 用作实例管理凭据；不要把它提供给其他用户。普通客户端密钥登录后台后创建。
3. 双击 `启动.command`，或在 `server/` 运行：

```sh
docker compose -f docker-compose.yaml -f docker-compose.local.yaml up -d --build
```

打开 http://localhost:3001 注册本机管理员。API 文档为 http://localhost:8890/docs。已有实例请使用原有账号与配置，避免覆盖数据和密钥。`停止.command` 仅停止容器，保留数据卷。

`配置方舟.command` 可在终端中隐藏输入模型密钥；它更新已存在的 `server/.env`，不会创建完整初始配置。运行真实模型写入和检索会消耗供应商额度。

## 验证范围

- 5 项离线适配测试：客户端初始化、请求与向量转换、维度错误、非有限数值、鉴权错误传播。
- 已完成单样本真实模型测试：提取并保存通用饮品偏好，跨问法检索召回；更换用户 ID 后结果为空。
- 以上是功能烟测，不代表记忆准确率、冲突处理效果或大规模性能基准。尚未完成独立记忆质量评测，也未接入真实业务 Agent。

离线测试可在已构建的 API 容器中运行，不调用真实模型：

```sh
docker compose -f server/docker-compose.yaml -f server/docker-compose.local.yaml exec -T mem0 python -B - < tests/embeddings/ark/test_ark.py
```

## 来源与许可

基座：[mem0ai/mem0](https://github.com/mem0ai/mem0)，本分支起点 `2c81af3`。保留 [Apache-2.0 LICENSE](LICENSE)；本 README 上方列出本分支修改。上游文档与基准成绩不代表 RecallFlow 的实测成果。
