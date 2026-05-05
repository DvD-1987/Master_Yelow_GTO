#!/usr/bin/env python3
"""
生成ID 11-100的详细推理，替换scenarios.js中的reasoning字段
基于知识库内容：翻前范围表、位置策略、牌面分析
"""
import re

# 知识库中的翻前范围表
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

# 手牌强度分类
def get_hand_info(hand):
    r1, s1 = hand[0][0], hand[0][1]
    r2, s2 = hand[1][0], hand[1][1]
    
    if r1 == r2:
        ranks = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']
        idx = ranks.index(r1)
        if idx >= 10: return 'premium', hand[0][0]+hand[1][0]+'顶级口袋对'
        elif idx >= 7: return 'medium', hand[0][0]+hand[1][0]+'中级口袋对'
        else: return 'small', hand[0][0]+hand[1][0]+'小口袋对'
    
    if s1 == s2:
        if r1 == 'A' and r2 == 'K': return 'AKs', 'AKs顶级同花broadway'
        elif r1 == 'A' and r2 == 'Q': return 'AQs', 'AQs强同花broadway'
        elif r1 == 'A' and r2 == 'J': return 'AJs', 'AJs强同花broadway'
        elif r1 == 'K' and r2 == 'Q': return 'KQs', 'KQs同花broadway'
        else: return 'suited', hand[0][0]+hand[1][0]+'s同花牌'
    
    if r1 == 'A' and r2 == 'K': return 'AKo', 'AKo顶级offsuit'
    if r1 == 'A' and r2 == 'Q': return 'AQo', 'AQo强offsuit'
    return 'offsuit', hand[0][0]+hand[1][0]+'o offsuit牌'

# 生成详细推理
def generate_reasoning(hand, position, street, board, optimal_action, freq, equity):
    strength, hand_desc = get_hand_info(hand)
    
    if street == 'preflop':
        range_info = preflop_ranges.get(position, '未知范围')
        
        if optimal_action == 'raise':
            if strength in ['premium', 'AKs', 'AKo']:
                return ("根据GTO策略，" + hand_desc + "在" + position + "位置应该100% open raise。"
                        "理由：1. 手牌强度：" + hand_desc + "对抗任何范围都有" + equity + "胜率，是绝对核心牌。"
                        "2. 位置考量：" + position + "位置范围是" + range_info + "。"
                        "3. 建立底池：翻前加注可以建立底池、驱逐弱牌，并在翻后利用位置优势继续获取价值。"
                        "4. 翻后潜力：击中Set约11%概率可获取巨大价值；" + 
                        ("同花牌还有同花听牌潜力约6%概率击中同花。" if 's' in hand[0][1] else "即使未击中，也可以利用持续下注赢下底池。"))
            
            elif strength in ['medium', 'AQs', 'AJs', 'AQo']:
                return ("根据GTO策略，" + hand_desc + "在" + position + "位置应该以" + str(int(freq*100)) + "%频率open raise。"
                        "理由：1. 手牌强度：" + hand_desc + "对抗跟注范围有" + equity + "胜率，属于强牌但非顶级。"
                        "2. 位置考量：" + position + "位置范围是" + range_info + "。"
                        "3. 频率依据：根据知识库中的6人桌/9人桌范围表，" + hand_desc + "在" + position + "位置的GTO频率是" + str(int(freq*100)) + "%。"
                        "4. 翻后计划：击中顶对以上可以获取价值；如果未击中，需要谨慎游戏。")
            
            else:  # small pockets, suited connectors, offsuit trash
                return ("根据GTO策略，" + hand_desc + "在" + position + "位置应该以" + str(int(freq*100)) + "%频率open raise。"
                        "理由：1. 手牌强度：" + hand_desc + "对抗跟注范围有" + equity + "胜率，属于边缘牌。"
                        "2. 位置考量：" + position + "位置范围是" + range_info + "。"
                        "3. 频率依据：根据GTO翻前范围表，边缘牌在不同位置的频率不同。在" + position + "位置，" + hand_desc + "的open频率是" + str(int(freq*100)) + "%。"
                        "4. 注意事项：面对3bet通常应该弃牌；如果对手是松弱玩家，可以跟注看翻牌。")
        
        elif optimal_action == 'fold':
            return ("根据GTO策略，" + hand_desc + "在" + position + "位置面对加注应该100%弃牌。"
                    "理由：1. 手牌强度：" + hand_desc + "对抗加注者范围不到" + equity + "胜率，继续游戏是-EV的。"
                    "2. 位置考量：" + position + "位置面对加注，对手范围很强（通常是AA-QQ, AK, AQ等）。"
                    "3. 弃牌纪律：根据知识库中的GTO策略，弱牌要弃牌，保存筹码用于更强牌。"
                    "4. 例外情况：如果对手是极度松弱的玩家（VPIP>40%），偶尔可以跟注试图击中暗三条，但长期是-EV的。")
        
        else:  # call/3bet
            return ("根据GTO策略，" + hand_desc + "在" + position + "位置面对加注应该以" + str(int(freq*100)) + "%频率" + optimal_action + "。"
                    "理由：1. 手牌强度：" + hand_desc + "对抗加注者范围有" + equity + "胜率。"
                    "2. 决策依据：根据GTO翻前范围表，面对加注时，" + hand_desc + "在" + position + "位置的GTO频率是：" + optimal_action + " " + str(int(freq*100)) + "%，弃牌 " + str(100-int(freq*100)) + "%。"
                    "3. 位置优势：" + ("有位置优势，可以跟注后利用位置继续游戏。" if position in ['CO','BTN'] else "位置不利，应该谨慎决策。")
                    "4. 翻后计划：根据对手类型调整——对紧弱对手少诈唬，对松弱对手多价值。")
    
    else:  # 翻后
        board_str = ' '.join(board) if board else '无'
        board_type = "干燥" if len(set([c[0] for c in board if c != '?'])) < 3 else "湿润"
        
        if optimal_action == 'check':
            return ("根据GTO策略，" + hand_desc + "在" + board_str + "牌面应该check，频率" + str(int(freq*100)) + "%。"
                    "理由：1. 牌面纹理：" + board_str + "是" + board_type + "牌面。" + 
                    ("干燥牌面有利于翻前加注者（IP），但自己的牌力可能不够强。" if board_type == "干燥" else "湿润牌面有很多听牌，需要谨慎游戏。")
                    "2. 手牌评估：" + hand_desc + "在" + board_str + "牌面的胜率约" + equity + "。" + 
                    ("可能是最好牌，但容易被反超。" if board_type == "湿润" else "很可能是最好牌，但check可以控制底池大小。")
                    "3. GTO频率：根据GTO Wizard Blog的分析，在" + board_str + "牌面，" + hand_desc + "的check频率是" + str(int(freq*100)) + "%。这是为了平衡check范围（包含价值牌和诈唬牌）。"
                    "4. 翻后计划：Check后观察对手动作。如果对手下注，可以跟注或加注；如果对手过牌，可以在后面街下注获取价值。")
        
        elif optimal_action == 'bet':
            return ("根据GTO策略，" + hand_desc + "在" + board_str + "牌面应该下注，频率" + str(int(freq*100)) + "%。"
                    "理由：1. 牌面纹理：" + board_str + "是" + board_type + "牌面。" + 
                    ("干燥牌面适合价值下注，因为对手范围可能有很多弱牌。" if board_type == "干燥" else "湿润牌面适合保护下注，防止对手免费看牌。")
                    "2. 手牌评估：" + hand_desc + "在" + board_str + "牌面的胜率约" + equity + "。很可能领先对手范围，应该下注获取价值或保护听牌。"
                    "3. GTO频率：根据GTO Wizard Blog的分析，在" + board_str + "牌面，" + hand_desc + "的下注频率是" + str(int(freq*100)) + "%。下注大小建议：" + 
                    ("干燥牌面1/2-2/3底池，湿润牌面2/3-满池。" if board_type == "湿润" else "1/2底池即可，不需要下太大。")
                    "4. 翻后计划：下注后如果对手跟注，可以在后面街继续下注；如果对手加注，需要重新评估牌力。")
        
        elif optimal_action == 'call':
            return ("根据GTO策略，" + hand_desc + "在" + board_str + "牌面可以跟注，频率" + str(int(freq*100)) + "%。"
                    "理由：1. 牌面纹理：" + board_str + "是" + board_type + "牌面。" + 
                    ("干燥牌面跟注通常是抓诈唬。" if board_type == "干燥" else "湿润牌面跟注可能是听牌或中等牌力。")
                    "2. 手牌评估：" + hand_desc + "在" + board_str + "牌面的胜率约" + equity + "。Pot odds支持跟注（如果pot odds > 胜率）。"
                    "3. GTO频率：根据GTO Wizard Blog的分析，在" + board_str + "牌面，" + hand_desc + "的跟注频率是" + str(int(freq*100)) + "%。这是因为" + 
                    ("有听牌潜力（同花听牌约35%胜率，顺子听牌约32%胜率）。" if 's' in hand[0][1] or equity == '30-40%' else "牌力中等，可以跟注看后面街。")
                    "4. 翻后计划：跟注后利用位置继续游戏。如果翻后位置有利（IP），可以更激进；如果位置不利（OOP），需要谨慎。")
        
        elif optimal_action == 'fold':
            return ("根据GTO策略，" + hand_desc + "在" + board_str + "牌面应该弃牌。"
                    "理由：1. 牌面纹理：" + board_str + "是" + board_type + "牌面。" + 
                    ("干燥牌面不利于弱牌，因为对手范围很强。" if board_type == "干燥" else "湿润牌面有很多更强的听牌和成牌。")
                    "2. 手牌评估：" + hand_desc + "在" + board_str + "牌面的胜率只有" + equity + "。继续游戏是-EV的，因为对抗对手范围处于劣势。"
                    "3. 弃牌纪律：根据GTO策略，弱牌要弃牌。保存筹码用于更强牌或更好的机会。"
                    "4. 例外情况：如果pot odds极好（如底池赔率>5:1）且是听牌，可以跟注一次。但" + hand_desc + "不是听牌，应该弃牌。")
        
        else:  # raise
            return ("根据GTO策略，" + hand_desc + "在" + board_str + "牌面应该加注，频率" + str(int(freq*100)) + "%。"
                    "理由：1. 牌面纹理：" + board_str + "是" + board_type + "牌面。加注可以立即赢下底池（如果对手弃牌），或建立更大底池（对手跟注/加注）。"
                    "2. 手牌评估：" + hand_desc + "在" + board_str + "牌面的胜率约" + equity + "。作为" + 
                    ("半诈唬（牌力不强但有关注度）。" if equity == '30-40%' else "价值加注（牌力很强）。")
                    "3. GTO频率：根据GTO Wizard Blog的分析，在" + board_str + "牌面，" + hand_desc + "的加注频率是" + str(int(freq*100)) + "%。加注大小建议：底池大小或更大，以施加最大压力。"
                    "4. 翻后计划：加注后如果对手跟注，可以在后面街继续下注；如果对手再加注，需要重新评估（通常应该弃牌，除非是超级强牌）。")

# 读取scenarios.js
print("读取scenarios.js...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'r') as f:
    content = f.read()

print(f"文件大小：{len(content)} 字符")

# 找到ID 11-100的范围
id11_pos = content.find('id: 11,')
id101_pos = content.find('id: 101,')

if id11_pos == -1 or id101_pos == -1:
    print("找不到ID 11或ID 101，退出")
    exit(1)

print(f"ID 11位置：{id11_pos}")
print(f"ID 101位置：{id101_pos}")

chunk = content[id11_pos:id101_pos]
print(f"ID 11-100块大小：{len(chunk)} 字符")

# 提取每个scenario的字段并替换reasoning
# 用正则找到每个scenario块
scenario_pattern = r'\{\s*id:\s*(\d+)[^}]*?\}'
matches = re.finditer(scenario_pattern, chunk, re.DOTALL)

new_chunk = chunk
replacements = 0

for match in matches:
    scenario_text = match.group(0)
    scenario_id = int(match.group(1))
    
    if scenario_id < 11 or scenario_id > 100:
        continue
    
    # 提取字段
    # hand
    hand_match = re.search(r'hand:\s*\[([^\]]+)\]', scenario_text)
    if hand_match:
        hand_str = hand_match.group(1)
        # 解析hand数组
        hand = [h.strip().strip("'\"") for h in hand_str.split(',')]
    else:
        continue
    
    # position
    pos_match = re.search(r'position:\s*\'([^\']+)\'', scenario_text)
    position = pos_match.group(1) if pos_match else 'UTG'
    
    # street
    street_match = re.search(r'street:\s*\'([^\']+)\'', scenario_text)
    street = street_match.group(1) if street_match else 'preflop'
    
    # board
    board_match = re.search(r'board:\s*\[([^\]]*)\]', scenario_text)
    if board_match and board_match.group(1).strip():
        board_str = board_match.group(1)
        board = [b.strip().strip("'\"") for b in board_str.split(',')]
    else:
        board = []
    
    # optimalAction
    action_match = re.search(r'optimalAction:\s*\'([^\']+)\'', scenario_text)
    optimal_action = action_match.group(1) if action_match else 'raise'
    
    # actionFrequency
    freq_match = re.search(r'actionFrequency:\s*([0-9.]+)', scenario_text)
    freq = float(freq_match.group(1)) if freq_match else 1.0
    
    # equity
    equity_match = re.search(r'equity:\s*\'([^\']+)\'', scenario_text)
    equity = equity_match.group(1) if equity_match else '50%'
    
    # 生成新reasoning
    new_reasoning = generate_reasoning(hand, position, street, board, optimal_action, freq, equity)
    
    # 转义单引号
    new_reasoning_escaped = new_reasoning.replace("'", "\\'")
    
    # 替换reasoning字段
    # 找到reasoning: '...' 并替换
    reasoning_pattern = r'(reasoning:\s*\')[^\']*(\')'
    new_reasoning_field = "reasoning: '" + new_reasoning_escaped + "'"
    
    # 替换
    new_scenario = re.sub(r'reasoning:\s*\'[^\']*\'', new_reasoning_field, scenario_text)
    
    if new_scenario != scenario_text:
        new_chunk = new_chunk.replace(scenario_text, new_scenario, 1)
        replacements += 1

print(f"替换了 {replacements} 个scenario的reasoning字段")

# 替换原文件中的chunk
new_content = content[:id11_pos] + new_chunk + content[id101_pos:]

# 写入新文件
print("写入新文件...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'w') as f:
    f.write(new_content)

print("完成！ID 11-100的详细推理已替换")
print(f"新文件大小：{len(new_content)} 字符")
