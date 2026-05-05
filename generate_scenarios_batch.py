#!/usr/bin/env python3
"""
批量生成GTO德州扑克题目脚本
目标：生成ID 26-500的475道题
基于知识库内容和标准GTO策略
"""

# 题目模板生成函数
def gen_preflop_scenario(id_num, diff, pos, hand, table_size, pot, stack, bet, action_to, opt, freq, ev, odds, mdf, expl, reasoning, equity, opp_val, opp_bluff, teach, mistakes, tags):
    """生成翻前题目"""
    opp_range = f"value: '{opp_val}',\n            bluff: '{opp_bluff}'" if opp_val else "value: null,\n            bluff: null"
    return f"""
    {{
        id: {id_num},
        difficulty: '{diff}',
        street: 'preflop',
        position: '{pos}',
        tableSize: {table_size},
        hand: {hand},
        board: [],
        potSize: {pot},
        effectiveStack: {stack},
        currentBet: {bet},
        actionToPlayer: '{action_to}',
        optimalAction: '{opt}',
        actionFrequency: {freq},
        ev: {ev},
        potOdds: {odds},
        mdf: {mdf},
        explanation: '{expl}',
        reasoning: '{reasoning}',
        equity: '{equity}',
        opponentRange: {{
            {opp_range}
        }},
        teaching: {teach},
        commonMistakes: {mistakes},
        tags: {tags}
    }}"""

def gen_postflop_scenario(id_num, diff, street, pos, ip_oop, table_size, hand, board, pot, stack, bet, action_to, opt, freq, ev, odds, mdf, expl, reasoning, equity, opp_val, opp_bluff, teach, mistakes, tags):
    """生成翻后题目"""
    opp_range = f"value: '{opp_val}',\n            bluff: '{opp_bluff}'" if opp_val else "value: null,\n            bluff: null"
    return f"""
    {{
        id: {id_num},
        difficulty: '{diff}',
        street: '{street}',
        position: '{pos}',
        tableSize: {table_size},
        hand: {hand},
        board: {board},
        potSize: {pot},
        effectiveStack: {stack},
        currentBet: {bet},
        actionToPlayer: '{action_to}',
        optimalAction: '{opt}',
        actionFrequency: {freq},
        ev: {ev},
        potOdds: {odds},
        mdf: {mdf},
        explanation: '{expl}',
        reasoning: '{reasoning}',
        equity: '{equity}',
        opponentRange: {{
            {opp_range}
        }},
        teaching: {teach},
        commonMistakes: {mistakes},
        tags: {tags}
    }}"""

# 批量生成题目
scenarios = []

# 翻前题目（ID 26-175，共150道）
preflop_setups = [
    # (id, diff, pos, hand, table_size, pot, stack, bet, action_to, opt, freq, ev, odds, mdf, expl, reasoning, equity, opp_val, opp_bluff, teach, mistakes, tags)
    (26, 'beginner', 'UTG+1', 8, ['A♠','K♠'], 1.5, 100, 0, '', 'raise', 1.0, 0.82, 0, 0, 'AKs在UTG+1应该100% open', 'AKs对抗范围55-58%胜率，UTG+1身后6对手', '55-58%', None, None, ['UTG+1位置', 'AKs顶级牌', '100% open'], ['弃牌不可取', '平跟失去价值'], ['preflop','open','UTG+1','AKs','suited']),
    (27, 'beginner', 'UTG+1', 8, ['A♦','Q♦'], 1.5, 100, 0, '', 'raise', 1.0, 0.72, 0, 0, 'AQs在UTG+1应该100% open', 'AQs是顶级broadway牌+同花，UTG+1 100% open', '53-55%', None, None, ['UTG+1位置', 'AQs强度高', '100% open'], ['弃牌不可取', '平跟失去价值'], ['preflop','open','UTG+1','AQs','suited']),
    (28, 'beginner', 'MP', 8, ['K♠','Q♠'], 1.5, 100, 0, '', 'raise', 1.0, 0.68, 0, 0, 'KQs在MP应该100% open', 'KQs是broadway连张+同花，MP位置100% open', '52-54%', None, None, ['MP位置', 'KQs价值高', '100% open'], ['弃牌不可取', '平跟失去价值'], ['preflop','open','MP','KQs','suited']),
]

print(f"准备了 {len(preflop_setups)} 个翻前模板")
print("开始生成题目...")

# 这里只生成少量测试，完整版需要循环生成
for setup in preflop_setups:
    id_num, diff, pos, table_size, hand, pot, stack, bet, action_to, opt, freq, ev, odds, mdf, expl, reasoning, equity, opp_val, opp_bluff, teach, mistakes, tags = setup
    scenario = gen_preflop_scenario(id_num, diff, pos, hand, table_size, pot, stack, bet, action_to, opt, freq, ev, odds, mdf, expl, reasoning, equity, opp_val, opp_bluff, teach, mistakes, tags)
    scenarios.append(scenario)

print(f"已生成 {len(scenarios)} 道题目")
print("前100字符预览:")
print(scenarios[0][:200] + "...")
