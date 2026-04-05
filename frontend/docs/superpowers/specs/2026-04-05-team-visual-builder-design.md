# Team 可视化构建器 设计文档

**日期：** 2026-04-05
**状态：** 已批准

---

## 概述

为 `module_agno_manage` 模块新增一个可视化 Team 构建页面，允许用户以自由画布（Flow 图）方式查看、创建和编辑 Team 组织结构（支持 Team 相互嵌套）。

---

## 背景与约束

- 现有数据模型：`teams` 表（Team 配置）+ `team_members` 关联表（`member_type: agent | team`）
- 前端框架：Vue3 + TypeScript + Element-Plus
- 图形库：**Vue Flow**（新增依赖，MIT 协议，Vue3 原生支持）
- 现有 API：`AgTeamAPI`、`AgTeamMemberAPI` 已完整，无需后端改动

---

## 文件结构

```
src/views/module_agno_manage/team_builder/
└── index.vue                  # 主页面

src/views/module_agno_manage/teams/
├── index.vue                  # 现有列表页（新增「可视化」跳转按钮）
└── components/
    └── TeamFormFields.vue     # 抽出的表单字段组件（新增，供 index.vue Dialog 和 team_builder 右侧面板复用）

src/api/module_agno_manage/
├── teams.ts                   # 已有，无需改动
└── team_members.ts            # 已有，无需改动
```

修改文件：
- `src/views/module_agno_manage/teams/index.vue` — 操作列新增「可视化」跳转按钮；将编辑表单字段迁移到 `TeamFormFields.vue`

---

## 路由

- 路径：`/agno/team-builder`
- 可选参数：`?root_id=123`（指定根 Team ID）
- 入口：teams 列表操作列「可视化」按钮 → `router.push('/agno/team-builder?root_id={id}')`

---

## 页面布局

三栏结构：

```
┌────────────────────────────────────────────────────────────┐
│  工具栏：[根Team选择器] [新建Team] [新建Agent成员] [保存] [全屏] │
├──────────────────────────────────┬─────────────────────────┤
│                                  │                         │
│        Vue Flow 画布             │   右侧配置面板          │
│  （自由拖拽 + 连线）             │   （点击节点后展开）    │
│                                  │   宽度: 400px           │
│                                  │   默认: 收起            │
└──────────────────────────────────┴─────────────────────────┘
```

---

## 节点类型

### TeamNode
- 显示：Team 名称、mode 彩色徽章（route=蓝、coordinate=橙、collaborate=绿）、模型名称、成员数量
- Handle：左侧连入（被父 Team 包含）、右/底连出（包含子成员）
- 右下角：展开/收起子节点按钮

### AgentNode
- 显示：Agent 名称、role 描述、排序编号
- Handle：左侧连入（被 Team 包含）

### AddMemberNode（占位节点）
- 虚线边框，显示「+ 添加成员」
- 每个 TeamNode 底部自动出现
- 点击后弹出选择器（选 Agent 或子 Team）

---

## 数据流

### 加载

```
页面挂载
  ↓
读取 URL 参数 root_id
  ├─ 有 → 加载 Team 详情 + 递归加载所有 team_members
  └─ 无 → 显示"请选择根Team"LazySelect
  ↓
buildGraph(rootTeam, membersMap) → { nodes, edges }
  ↓
渲染画布，调用 fitView() 居中
```

核心转换函数签名：
```typescript
function buildGraph(
  rootTeam: AgTeamTable,
  membersMap: Map<string, AgTeamMemberTable[]>,
  agentMap: Map<string, string>   // id → name 缓存
): { nodes: Node[], edges: Edge[] }
```

### 保存（批量提交，串行执行）

维护 `pendingChanges` 队列，点击「保存」后按依赖顺序串行执行：
1. 新建 Team（临时 id 替换为真实 id）→ `createAgTeam()`，拿到真实 id 后更新节点引用
2. 修改 Team 配置 → `updateAgTeam()`
3. 删除成员关系 → `deleteAgTeamMember()`
4. 新建成员关系（使用真实 id）→ `createAgTeamMember()`

> **注意**：画布中新建的 Team 节点使用临时 id（如 `tmp_uuid`），步骤 1 完成后所有引用该节点的 member 关系自动替换为真实 id，再执行步骤 4。

---

## 右侧配置面板

### 点击 TeamNode 展开

**Tab 1：Team 配置**（el-tabs 分组）
- 基础：name、mode、model_id（LazySelect）、memory_manager_id（LazySelect）
- 行为：respond_directly、delegate_to_all_members、max_iterations、tool_call_limit
- 记忆：enable_agentic_memory、update_memory_on_run、enable_session_summaries 等
- 指令：instructions（textarea）、expected_output（textarea）

**Tab 2：成员列表**
- 展示当前 Team 所有成员
- 支持：拖拽排序 member_order、修改 role、删除成员

### 点击 AgentNode 展开

简化面板：role、member_order、status 三个字段

---

## 交互规则

| 操作 | 行为 |
|---|---|
| 拖拽节点 | 仅改变画布位置，不触发 API |
| 连线 Team→Agent/Team | 创建 team_member 关系，加入 pendingChanges |
| 断开连线 | 删除 team_member 关系，加入 pendingChanges |
| 工具栏「新建Team」 | Dialog 填写 name+mode，TeamNode 放到画布中央 |
| 节点右键菜单 | 删除节点（Team 提示连带删除成员关系） |
| 「保存」按钮 | 批量提交 pendingChanges，成功后刷新画布 |
| 循环引用检测 | 连线时 DFS 检测环，检测到则拒绝并 ElMessage.error |

---

## 循环引用防护

连线前执行 DFS：从目标节点出发，若能到达源节点，判定为循环，拒绝连线。

```typescript
function wouldCreateCycle(
  edges: Edge[],
  sourceId: string,
  targetId: string
): boolean
```

---

## 模块职责边界

| 操作 | 在哪里做 |
|---|---|
| 创建/编辑 Agent 详细配置 | `agents/` 页面（独立维护） |
| 创建/编辑 Team 详细配置 | `teams/` 页面 或 `team_builder` 右侧面板 |
| 组合 Team 结构、建立嵌套关系 | `team_builder/` 画布 |

**原则：画布只负责「组合」，不负责「从零创建 Agent」。** 画布中添加 Agent 成员时，通过 LazySelect 从已有 Agent 列表选择。

---

## 依赖变更

新增：
```bash
pnpm add @vue-flow/core @vue-flow/controls @vue-flow/minimap @vue-flow/background
```
