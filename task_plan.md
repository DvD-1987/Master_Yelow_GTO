# 德州扑克GTO练习器 - 任务规划 v2

## 项目目标

**核心使命**：不是背答案，是教会玩家GTO思维逻辑
- 每道题 = 情境 + 决策点 + GTO推荐 + 完整推理分析
- 5000+道情境题，覆盖所有位置/阶段/筹码尺度
- 详细解释：为什么这个动作是对的，GTO频率，EV，赔率计算，范围分析
- 洗牌随机，防止记忆答案

---

## 技术架构决策（已确认）

### 文件结构
```
/master_Yelow_GTO_Pro/
├── index.html          ← 主页面（无内嵌数据和样式）
├── styles.css          ← 样式（赌场专业风格）
├── app.js              ← 核心逻辑（洗牌、评分、反馈引擎）
├── scenarios.js         ← 题库数据（独立维护，5000+条）
├── gto-engine.js        ← GTO计算引擎（赔率/MDF/EV/牌力判断）
└── assets/             ← 扑克牌图片、音效等
```

**关键原则**：scenarios.js完全独立，新增题目不需要动任何逻辑代码

### 题库数据格式（scenarios.js）
每条情境包含：
```javascript
{
  id: unique_id,
  difficulty: 'beginner' | 'intermediate' | 'advanced',
  street: 'preflop' | 'flop' | 'turn' | 'river',
  position: 'BTN' | 'SB' | 'BB' | 'UTG' | 'UTG+1' | 'MP' | 'MP+1' | 'CO',
  tableSize: 6 | 7 | 8 | 9,       // 桌型
  hand: ['As', 'Kd'],             // 玩家手牌
  board: ['Jh', '7c', '3d'],      // 公共牌（空数组=preflop）
  potSize: 150,                    // 底池（以bb为单位）
  effectiveStack: 10000,          // 有效筹码（以bb为单位）
  currentBet: 0,                   // 当前下注（0=行动轮开始）
  actionToPlayer: 'BB check',      // 对手上一步动作
  optimalAction: 'bet',            // GTO最优动作
  actionFrequency: 0.75,           // GTO执行该动作的频率（0-1）
  ev: 0.52,                        // 期望值（以底池为单位）
  potOdds: 2.5,                    // 底池赔率（:1）
  mdf: 62.5,                       // 最小防守频率%（有下注时）
  // 分析内容
  explanation: 'AKs在按钮位是顶级起手...',       // 一句话结论
  reasoning: '详细推理过程，包括牌力评估、位置分析、筹码考量...', // 完整分析
  equity: '52%',                   // 胜率评估
  opponentRange: {                 // 对手范围
    value: 'AA, KK, QQ, AK',
    bluff: 'KQs, JTs'
  },
  teaching: [                      // 教学要点数组
    '位置优势：按钮位有最后行动优势',
    '筹码深度：100bb时AK的玩法',
    'GTO频率：不是100%而是混合策略'
  ],
  commonMistakes: [               // 常见错误
    '错误1：过度3-bet导致范围失衡',
    '错误2：忽视位置因素'
  ],
  tags: ['preflop', 'open', 'BTN', 'AK']  // 标签（用于筛选/统计）
}
```

### GTO引擎功能（gto-engine.js）
- `calculateEquity(hand, board, opponentRange)` - 计算胜率
- `calculatePotOdds(pot, bet)` - 计算底池赔率
- `calculateMDF(pot, bet)` - 计算最小防守频率
- `evaluateAction(scenario, action)` - 评估动作是否GTO正确
- `generateHint(scenario)` - 生成提示（渐进式教学）
- `getOptimalRange(position, street, stack)` - 获取GTO开池范围参考

---

## UI设计方向（已确认）

### 风格：专业赌场
- **牌桌**：典型绿色毡布（#1a5f32）或深蓝（#0d2b4d）
- **边框**：木纹或金属质感
- **金色点缀**用于高亮和交互元素
- **字体**：无衬线，现代感（避免系统默认字体）
- **卡牌**：白色卡面，红色/黑色数字，花色清晰

### 布局
```
┌──────────────────────────────────────────┐
│  GTO德州扑克练习器    [初级][中级][高级]  │  ← 顶部导航+难度切换
├────────────────────────┬─────────────────┤
│                        │  📊 统计面板    │
│     牌桌可视化          │  正确率/进度    │
│   （座位+手牌+公共牌）  │                 │
│                        ├─────────────────┤
│     行动按钮组          │  📝 当前情境    │
│  Fold/Check/Call/Bet/  │  位置/阶段/底池 │
│  Raise                 │  筹码/对手动作  │
│                        ├─────────────────┤
│                        │  💡 GTO反馈     │
│                        │  （展开后显示）  │
│                        ├─────────────────┤
│                        │  📖 推理分析    │
│                        │  （完整解读）   │
└────────────────────────┴─────────────────┘
```

---

## 开发阶段（按David确认的顺序）

### Phase 1: 架构搭建
- [ ] 创建 `styles.css`（从index.html抽取CSS，进行重构）
- [ ] 创建 `scenarios.js`（把现有10条数据迁移，格式扩展）
- [ ] 创建 `gto-engine.js`（计算工具函数）
- [ ] 创建 `app.js`（游戏逻辑+洗牌+评分）
- [ ] 重构 `index.html`（引用外部文件，清空内联代码）
- [ ] **验收**：单文件index.html打开后功能完整

### Phase 2: UI重构
- [ ] 牌桌视觉升级（专业赌场风）
- [ ] 卡牌组件美化
- [ ] 座位布局优化（清晰展示位置关系）
- [ ] 响应式移动端适配
- [ ] 动效提升（发牌动画、按钮反馈）
- [ ] 使用 `frontend-design-zh` 指导设计决策

### Phase 3: 洗牌随机
- [ ] 全局洗牌算法（ Fisher-Yates ）
- [ ] 难度内随机选题
- [ ] 做完一道自动下一道（可选）
- [ ] 进度记忆（ sessionStorage ，防止刷新丢进度）

### Phase 4: 题库扩充（进行中 - David提供资料）
- [ ] 扩充初级情境（目标30-50条/级）
- [ ] 扩充中级情境（目标30-50条/级）
- [ ] 扩充高级情境（目标30-50条/级）
- [ ] 最终目标：5000+条
- [ ] 题库管理工具（可选：批量导入JSON）

---

## 题库扩充策略

David会提供GTO资料，我们负责：
1. 解析资料，提炼情境数据
2. 按统一格式写入scenarios.js
3. 验证每条情境的GTO逻辑正确性
4. 标记标签（位置/阶段/牌型/概念）

---

## Errors Encountered

| 日期 | 错误 | 解决方案 |
|---|---|---|
| 2026-05-03 | init-session.sh有CRLF问题 | 手动创建规划文件 |
| 2026-05-03 | frontend-design-zh Skill名称是mty-frontend-design-zh | 使用正确名称加载 |