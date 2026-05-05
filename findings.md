# 发现与研究

## 现有框架分析

### index.html 架构
- 纯前端单文件，约1454行（HTML+CSS+JS内联）
- 扑克牌用Unicode符号（♠♥♦♣）+CSS渲染
- 情境数据 `gtoScenarios[]` 硬编码在JS里（10条）
- 难度切换函数`setDifficulty()`实现有bug：它找第一个匹配的index加载，
  但total是全部10条，所以会出现"选初级但显示高级题"的问题

### 当前UI问题
1. **卡牌花色渲染**：`card-suit` span没有字体大小，导致大字符花色显示很小
2. **牌桌视觉**：椭圆形绿桌+木边框，较为传统
3. **反馈区域**：文字挤在一起，无层次感
4. **座位标注**：只有位置名称，缺少筹码量显示
5. **难度过滤bug**：实际切换难度时行为不正确

### 10条现有情境清单
| ID | 难度 | 阶段 | 位置 | 手牌 | 动作 |
|---|---|---|---|---|---|
| 1 | 初级 | preflop | BTN | AKs | raise |
| 2 | 初级 | preflop | BB | 77 | call |
| 3 | 初级 | flop | IP | QJ | check |
| 10 | 初级 | preflop | UTG | QQ | raise |
| 4 | 中级 | flop | IP | AKo | raise |
| 5 | 中级 | turn | IP | 98s | bet |
| 6 | 中级 | river | IP | QQ | call |
| 7 | 高级 | flop | OOP | A5s | bet |
| 8 | 高级 | turn | IP | T9o | fold |
| 9 | 高级 | river | IP | JJ | check |

---

## 技能应用笔记

### frontend-design-zh
- 禁止使用：Inter字体、紫渐变白底、陈词滥调配色
- 方向建议：扑克/赌场主题可以走「深邃午夜蓝+金色点缀」或「复古赌桌绿+铜色」
- 卡牌组件：考虑立体阴影、微妙动画

### planning-with-files
- 三文件：task_plan.md（总览）/ findings.md（调研）/ progress.md（日志）
- 项目根目录创建，不在skill目录

### code-review-pro
- Phase 2/3代码完成后使用
- 逻辑Agent：重点检查情境匹配逻辑、牌力判断
- 安全Agent：检查XSS（用户输入场景）
- 性能Agent：检查重复DOM操作
- 风格Agent：JS命名规范

---

## 微信文章关键启发

1. **RTK工具**：Coding时git status/test输出压80-90%，省钱
2. **GenericAgent**：分层记忆架构值得参考（练习器可否加用户学习轨迹？）
3. **mattpocock/skills**：`/grill-me`追问需求 — 开案前先想清楚再动手
4. **memory-tencentdb**：L0-L3分层 — 可以借鉴来做"情境完成度"分层记忆