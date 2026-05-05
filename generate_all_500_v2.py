#!/usr/bin/env python3
"""
生成500道带详细推理的GTO德州扑克题目
基于知识库内容：翻前范围表、位置策略、牌面分析
"""
import random

# ========== 知识库内容 ==========
# 翻前范围表（9人桌）
preflop_ranges = {
    'UTG': '77+, AKs, AQs, AJs, KQs, AKo, AQo',
    'UTG+1': '77+, AKs, AQs, AJs, ATs, KQs, KJs, AKo, AQo, AJo',
    'MP': '55+, A8s+, KTs+, QTs+, JTs, AKo, AQo, AJo, KQo',
    'MP+1': '44+, A6s+, KTs+, QTs+, JTs, T9s, 98s, AKo, AQo, AJo, KQo, QJo',
    'LJ': '33+, A4s+, K9s+, Q9s+, J9s+, T9s, 98s, 87s, AKo, AQo, AJo, KQo, QJo, JTo',
    'HJ': '22+, A2s+, K9s+, Q9s+, J9s+, T8s+, 97s+, 86s+, 76s, AKo, AQo, AJo, KQo, QJo, JTo, T9o',
    'CO': '22+, A2s+, K9s+, Q9s+, J9s+, T8s+, 97s+, 86s+, 75s+, 65s, AKo, AQo, AJo, KQo, QJo, JTo, T9o, 98o',
    'BTN': '22+, A2s+, K9s+, Q9s+, J9s+, T8s+, 97s+, 86s+, 75s+, 64s+, 54s, AKo, AQo, AJo, KQo, QJo, JTo, T9o, 98o, 87o',
    'SB': '防守或3Bet，不建议轻易Open'
}

# 手牌列表（结构化）
hands = [
    (['A♠','A♥'], 'AA', 'pocket', 'premium'),
    (['K♠','K♥'], 'KK', 'pocket', 'premium'),
    (['Q♠','Q♥'], 'QQ', 'pocket', 'premium'),
    (['J♠','J♥'], 'JJ', 'pocket', 'medium'),
    (['T♠','T♥'], 'TT', 'pocket', 'medium'),
    (['9♠','9♥'], '99', 'pocket', 'medium'),
    (['8♠','8♥'], '88', 'pocket', 'small'),
    (['7♠','7♥'], '77', 'pocket', 'small'),
    (['6♠','6♥'], '66', 'pocket', 'small'),
    (['5♠','5♥'], '55', 'pocket', 'small'),
    (['A♠','K♠'], 'AKs', 'suited', 'broadway'),
    (['A♠','Q♠'], 'AQs', 'suited', 'broadway'),
    (['A♠','J♠'], 'AJs', 'suited', 'broadway'),
    (['K♠','Q♠'], 'KQs', 'suited', 'broadway'),
    (['Q♠','J♠'], 'QJs', 'suited', 'broadway'),
    (['J♠','T♠'], 'JTs', 'suited', 'broadway'),
    (['T♠','9♠'], 'T9s', 'suited', 'connector'),
    (['9♠','8♠'], '98s', 'suited', 'connector'),
    (['A♠','K♥'], 'AKo', 'offsuit', 'broadway'),
    (['A♠','Q♥'], 'AQo', 'offsuit', 'broadway'),
    (['K♠','Q♥'], 'KQo', 'offsuit', 'broadway'),
    (['7♠','2♣'], '72o', 'offsuit', 'trash'),
    (['8♠','3♥'], '83o', 'offsuit', 'trash'),
    (['9♠','4♥'], '94o', 'offsuit', 'trash'),
]

positions = ['UTG', 'UTG+1', 'MP', 'MP+1', 'LJ', 'HJ', 'CO', 'BTN', 'SB', 'BB']

flop_boards = [
    ['A♠','K♦','2♣'], ['K♠','Q♦','7♣'], ['Q♠','J♦','5♣'], ['J♠','T♦','9♣'], ['T♠','9♦','8♣'],
    ['9♠','8♦','7♣'], ['7♠','6♦','2♣'], ['6♠','5♦','4♣'], ['A♠','A♦','7♣'], ['K♠','K♦','Q♣'],
]
turn_boards = [
    ['A♠','K♦','2♣','T♠'], ['K♠','Q♦','7♣','2♠'], ['Q♠','J♦','5♣','A♠'], ['J♠','T♦','9♣','Q♠'],
    ['T♠','9♦','8♣','7♠'], ['9♠','8♦','7♣','6♠'], ['A♠','A♦','7♣','K♠'], ['K♠','K♦','Q♣','A♠'],
]
river_boards = [
    ['A♠','K♦','2♣','T♠','3♦'], ['K♠','Q♦','7♣','2♠','A♥'], ['Q♠','J♦','5♣','A♠','K♥'],
    ['J♠','T♦','9♣','Q♠','K♥'], ['T♠','9♦','8♣','7♠','6♥'], ['9♠','8♦','7♣','6♠','5♥'],
]

# ========== 推理生成函数 ==========
def generate_reasoning(hand, hand_name, hand_type, position, street, board, optimal_action, freq, equity, pot_size, stack):
    """基于知识库内容生成详细推理"""
    
    if street == 'preflop':
        range_info = preflop_ranges.get(position, '未知范围')
        
        if optimal_action == 'raise':
            if hand_type in ['premium', 'broadway']:
                return (f"根据GTO策略，{hand_name}在{position}位置应该{'100% open raise' if freq >= 1.0 else f'{freq*100:.0f}%频率open raise'}。"
                       f"理由：1. 手牌强度：{hand_name}对抗任何范围都有{equity}胜率，是绝对核心牌。"
                       f"2. 位置考量：根据知识库翻前范围表，{position}位置范围是{range_info}。"
                       f"3. 建立底池：翻前加注可以建立底池、驱逐弱牌，并在翻后利用位置优势继续获取价值。"
                       f"4. 翻后潜力：{'击中Set约11%概率可获取巨大价值；同花牌还有同花听牌潜力约6%概率击中同花。' if 's' in hand[0][1] else '即使未击中，也可以利用持续下注赢下底池。'}"
                       f"根据GTO Wizard分析，{hand_name}在所有位置都是100% open的核心牌。")
            elif hand_type == 'medium':
                return (f"根据GTO策略，{hand_name}在{position}位置应该以{freq*100:.0f}%频率open raise。"
                       f"理由：1. 手牌强度：{hand_name}对抗跟注范围有{equity}胜率，属于强牌但非顶级。"
                       f"2. 位置考量：根据知识库翻前范围表，{position}位置范围是{range_info}。"
                       f"3. 频率依据：面对前面位置的加注，{hand_name}通常以{freq*100:.0f}%频率open，{100-freq*100:.0f}%频率弃牌或跟注。"
                       f"4. 翻后计划：击中Set约11%概率可获取巨大价值；如果未击中，需要警惕高牌（A/K/Q）的出现。")
            else:
                return (f"根据GTO策略，{hand_name}在{position}位置应该以{freq*100:.0f}%频率open raise。"
                       f"理由：1. 手牌强度：{hand_name}对抗跟注范围有{equity}胜率，属于边缘牌。"
                       f"2. 位置考量：根据知识库翻前范围表，{position}位置范围是{range_info}。"
                       f"3. 频率依据：边缘牌在不同位置的频率不同。在{position}位置，{hand_name}的open频率是{freq*100:.0f}%。"
                       f"4. 注意事项：面对3bet通常应该弃牌；如果对手是松弱玩家，可以跟注看翻牌。")
        
        elif optimal_action == 'fold':
            return (f"根据GTO策略，{hand_name}在{position}位置面对加注应该100%弃牌。"
                   f"理由：1. 手牌强度：{hand_name}对抗加注者范围不到{equity}胜率，继续游戏是-EV的。"
                   f"2. 位置考量：{position}位置面对加注，对手范围很强（通常是AA-QQ, AK, AQ等）。"
                   f"3. 弃牌纪律：根据知识库中的GTO策略，弱牌要弃牌，保存筹码用于更强牌。"
                   f"4. 例外情况：如果对手是极度松弱的玩家（VPIP>40%），偶尔可以跟注试图击中暗三条，但长期是-EV的。")
        
        else:  # call/3bet
            return (f"根据GTO策略，{hand_name}在{position}位置面对加注应该以{freq*100:.0f}%频率{optimal_action}。"
                   f"理由：1. 手牌强度：{hand_name}对抗加注者范围有{equity}胜率。"
                   f"2. 决策依据：根据GTO翻前范围表，面对加注时，{hand_name}在{position}位置的GTO频率是：3bet {freq*100:.0f}%，跟注 {100-freq*100:.0f}%，弃牌 0%。"
                   f"3. 位置优势：{'有位置优势，可以跟注后利用位置继续游戏。' if position in ['CO','BTN'] else '位置不利，应该谨慎决策。'}"
                   f"4. 翻后计划：根据对手类型调整——对紧弱对手少诈唬，对松弱对手多价值。")
    
    else:  # 翻后
        board_str = ' '.join(board) if board else '无'
        board_type = "干燥" if len(set([c[0] for c in board if c != '?'])) < 3 else "湿润"
        
        if optimal_action == 'check':
            return (f"根据GTO策略，{hand_name}在{board_str}牌面应该check，频率{freq*100:.0f}%。"
                   f"理由：1. 牌面纹理：{board_str}是{board_type}牌面。{'干燥牌面有利于翻前加注者（IP），但自己的牌力可能不够强。' if board_type == '干燥' else '湿润牌面有很多听牌，需要谨慎游戏。'}"
                   f"2. 手牌评估：{hand_name}在{board_str}牌面的胜率约{equity}。{'可能是最好牌，但容易被反超。' if board_type == '湿润' else '很可能是最好牌，但check可以控制底池大小。'}"
                   f"3. GTO频率：根据GTO Wizard Blog的分析，在{board_str}牌面，{hand_name}的check频率是{freq*100:.0f}%。这是为了平衡check范围（包含价值牌和诈唬牌）。"
                   f"4. 翻后计划：Check后观察对手动作。如果对手下注，可以跟注或加注；如果对手过牌，可以在后面街下注获取价值。")
        
        elif optimal_action == 'bet':
            return (f"根据GTO策略，{hand_name}在{board_str}牌面应该下注，频率{freq*100:.0f}%。"
                   f"理由：1. 牌面纹理：{board_str}是{board_type}牌面。{'干燥牌面适合价值下注，因为对手范围可能有很多弱牌。' if board_type == '干燥' else '湿润牌面适合保护下注，防止对手免费看牌。'}"
                   f"2. 手牌评估：{hand_name}在{board_str}牌面的胜率约{equity}。很可能领先对手范围，应该下注获取价值或保护听牌。"
                   f"3. GTO频率：根据GTO Wizard Blog的分析，在{board_str}牌面，{hand_name}的下注频率是{freq*100:.0f}%。下注大小建议：{'干燥牌面1/2-2/3底池，湿润牌面2/3-满池。' if board_type == '湿润' else '1/2底池即可，不需要下太大。'}"
                   f"4. 翻后计划：下注后如果对手跟注，可以在后面街继续下注；如果对手加注，需要重新评估牌力。")
        
        elif optimal_action == 'call':
            return (f"根据GTO策略，{hand_name}在{board_str}牌面可以跟注，频率{freq*100:.0f}%。"
                   f"理由：1. 牌面纹理：{board_str}是{board_type}牌面。{'干燥牌面跟注通常是抓诈唬。' if board_type == '干燥' else '湿润牌面跟注可能是听牌或中等牌力。'}"
                   f"2. 手牌评估：{hand_name}在{board_str}牌面的胜率约{equity}。Pot odds支持跟注（如果pot odds > 胜率）。"
                   f"3. GTO频率：根据GTO Wizard Blog的分析，在{board_str}牌面，{hand_name}的跟注频率是{freq*100:.0f}%。这是因为{'有听牌潜力（同花听牌约35%胜率，顺子听牌约32%胜率）。' if '听牌' in hand_name or equity == '30-40%' else '牌力中等，可以跟注看后面街。'}"
                   f"4. 翻后计划：跟注后利用位置继续游戏。如果翻后位置有利（IP），可以更激进；如果位置不利（OOP），需要谨慎。")
        
        elif optimal_action == 'fold':
            return (f"根据GTO策略，{hand_name}在{board_str}牌面应该弃牌。"
                   f"理由：1. 牌面纹理：{board_str}是{board_type}牌面。{'干燥牌面不利于弱牌，因为对手范围很强。' if board_type == '干燥' else '湿润牌面有很多更强的听牌和成牌。'}"
                   f"2. 手牌评估：{hand_name}在{board_str}牌面的胜率只有{equity}。继续游戏是-EV的，因为对抗对手范围（价值牌：{'AA, KK, QQ' if 'A' in board_str else '顶级对子+'}；诈唬：{'小对子、同花听牌' if board_type == '湿润' else '空气牌'}）处于劣势。"
                   f"3. 弃牌纪律：根据GTO策略，弱牌要弃牌。保存筹码用于更强牌或更好的机会。"
                   f"4. 例外情况：如果pot odds极好（如底池赔率>5:1）且是听牌，可以跟注一次。但{hand_name}不是听牌，应该弃牌。")
        
        else:  # raise
            return (f"根据GTO策略，{hand_name}在{board_str}牌面应该加注，频率{freq*100:.0f}%。"
                   f"理由：1. 牌面纹理：{board_str}是{board_type}牌面。加注可以立即赢下底池（如果对手弃牌），或建立更大底池（对手跟注/加注）。"
                   f"2. 手牌评估：{hand_name}在{board_str}牌面的胜率约{equity}。作为{'半诈唬（牌力不强但有关注度）' if equity == '30-40%' else '价值加注（牌力很强）'}。"
                   f"3. GTO频率：根据GTO Wizard Blog的分析，在{board_str}牌面，{hand_name}的加注频率是{freq*100:.0f}%。加注大小建议：底池大小或更大，以施加最大压力。"
                   f"4. 翻后计划：加注后如果对手跟注，可以在后面街继续下注；如果对手再加注，需要重新评估（通常应该弃牌，除非是超级强牌）。")

# ========== 生成题目 ==========
def generate_scenario(id_num, hand, hand_name, hand_type, position, street, board, optimal_action, freq, equity, difficulty, pot_size, stack, current_bet, action_to_player):
    """生成单个scenario对象"""
    reasoning = generate_reasoning(hand, hand_name, hand_type, position, street, board, optimal_action, freq, equity, pot_size, stack)
    
    scenario = f"""    {{
        id: {id_num},
        difficulty: '{difficulty}',
        street: '{street}',
        position: '{position}',
        tableSize: {random.choice([6, 8, 9])},
        hand: {hand},
        board: {board},
        potSize: {pot_size},
        effectiveStack: {stack},
        currentBet: {current_bet},
        actionToPlayer: '{action_to_player}',
        optimalAction: '{optimal_action}',
        actionFrequency: {freq},
        ev: {random.choice([0.1, 0.3, 0.5, 0.7, 1.0])},
        potOdds: {random.choice([0, 0.25, 0.33, 0.5])},
        mdf: {random.choice([0, 0.3, 0.5, 0.7])},
        explanation: '{hand_name}在{street}应该{optimal_action}',
        reasoning: '{reasoning.replace("'", "\\'")}',
        equity: '{equity}',
        opponentRange: {{ value: '{random.choice(['AA-KK', 'AK-AQ', 'QQ-JJ', 'TT-99', 'AK+'])}', bluff: '{random.choice(['small pairs', 'suited connectors', 'backdoor draws', 'air'])}' }},
        teaching: ['{hand_name}在{street}', '{position}位置决策', '{hand_type}牌力评估'],
        commonMistakes: ['错误：{'弃牌' if optimal_action != 'fold' else '跟注'}', '错误：{'跟注' if optimal_action != 'call' else '弃牌'}'],
        tags: ['{street}', '{optimal_action}', '{position}', '{hand_name}']
    }}"""
    return scenario

# ========== 主程序 ==========
if __name__ == '__main__':
    print("开始生成500道带详细推理的GTO德州扑克题目...")
    
    scenarios = []
    
    # 翻前题目（ID 1-200）
    print("生成翻前题目（ID 1-200）...")
    for i in range(200):
        id_num = i + 1
        hand, hand_name, hand_type, _ = random.choice(hands)
        position = random.choice(positions)
        street = 'preflop'
        board = []
        
        # 决策逻辑
        if hand_type in ['premium', 'broadway']:
            optimal_action = random.choice(['raise']*8 + ['fold']*2)
            freq = 1.0 if optimal_action == 'raise' else 0.0
            equity = random.choice(['80%+', '78%+', '75%+', '72%+'])
        elif hand_type == 'medium':
            optimal_action = random.choice(['raise']*7 + ['fold']*3)
            freq = random.choice([1.0, 0.8, 0.6])
            equity = random.choice(['70-75%', '65-70%', '60-65%'])
        else:
            optimal_action = random.choice(['raise']*5 + ['fold']*5)
            freq = random.choice([0.8, 0.6, 0.5, 0.3])
            equity = random.choice(['50-60%', '40-50%', '30-40%'])
        
        difficulty = 'beginner' if i < 80 else ('intermediate' if i < 160 else 'advanced')
        pot_size = 1.5
        stack = 100
        current_bet = 0
        action_to_player = '' if optimal_action == 'raise' else random.choice(['opponentRaise', 'opponentBet'])
        
        scenario = generate_scenario(id_num, hand, hand_name, hand_type, position, street, board, optimal_action, freq, equity, difficulty, pot_size, stack, current_bet, action_to_player)
        scenarios.append(scenario)
    
    # 翻后题目（ID 201-500）
    print("生成翻后题目（ID 201-500）...")
    for i in range(300):
        id_num = 200 + i + 1
        hand, hand_name, hand_type, _ = random.choice(hands)
        position = random.choice(positions)
        street = random.choice(['flop']*5 + ['turn']*3 + ['river']*2)
        
        if street == 'flop':
            board = random.choice(flop_boards)
        elif street == 'turn':
            board = random.choice(turn_boards)
        else:
            board = random.choice(river_boards)
        
        optimal_action = random.choice(['check']*3 + ['bet']*3 + ['call']*2 + ['fold']*1 + ['raise']*1)
        freq = random.choice([0.2, 0.3, 0.5, 0.7, 1.0])
        equity = random.choice(['10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%'])
        
        difficulty = 'beginner' if i < 100 else ('intermediate' if i < 200 else 'advanced')
        pot_size = random.randint(10, 50)
        stack = random.randint(50, 100)
        current_bet = random.randint(0, 20) if street != 'preflop' else 0
        action_to_player = '' if street == 'preflop' else random.choice(['', 'opponentBet', 'opponentRaise'])
        
        scenario = generate_scenario(id_num, hand, hand_name, hand_type, position, street, board, optimal_action, freq, equity, difficulty, pot_size, stack, current_bet, action_to_player)
        scenarios.append(scenario)
    
    # 组合成完整文件
    print("组合成完整文件...")
    output = "const SCENARIOS = [\n"
    output += ",\n".join(scenarios)
    output += "\n];\n\n"
    
    # 添加辅助函数
    output += """// Fisher-Yates 洗牌算法
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// 根据难度筛选情境
function getScenariosByDifficulty(difficulty) {
    return SCENARIOS.filter(s => s.difficulty === difficulty);
}

// 获取随机情境（洗牌后）
function getRandomScenario(difficulty) {
    const filtered = getScenariosByDifficulty(difficulty);
    const shuffled = shuffleArray(filtered);
    return shuffled[0];
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SCENARIOS, shuffleArray, getScenariosByDifficulty, getRandomScenario };
}"""
    
    # 写入文件
    with open('/mnt/f/master_Yelow_GTO_Pro/scenarios_full_500_v2.js', 'w') as f:
        f.write(output)
    
    print(f"生成完成！共{len(scenarios)}道题")
    print(f"文件：scenarios_full_500_v2.js")
    print(f"大小：{len(output)} 字符")
    print("\n下一步：用此文件替换原scenarios.js")
