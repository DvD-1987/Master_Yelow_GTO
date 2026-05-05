#!/usr/bin/env python3
"""
精准修复：修正翻后推理中的具体错误
不重新生成，只修正已知的错误模式
"""
import re

# 读取文件
print("读取scenarios.js...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'r') as f:
    content = f.read()

print(f"文件大小：{len(content)} 字符")

# ========== 精准修复规则 ==========

# 规则1：A-high牌面（如A♠ K♦ 2♣）被误判为湿润，应改为干燥
# 模式：牌面包含A和K，但无同花/顺子听牌
def fix_a_high_board(reasoning, board_str):
    """修复A-high牌面的错误判断"""
    if 'A' in board_str and 'K' in board_str:
        # 检查是否真有听牌
        cards = board_str.split()
        suits = [c[1] for c in cards if len(c) > 1]
        suit_counts = {}
        for s in suits:
            suit_counts[s] = suit_counts.get(s, 0) + 1
        max_suit = max(suit_counts.values()) if suit_counts else 0
        
        # 如果同花牌<3张，应该是干燥牌面
        if max_suit < 3:
            reasoning = reasoning.replace('湿润牌面（连张听牌）', '干燥牌面（高牌主导，听牌很少）')
            reasoning = reasoning.replace('湿润牌面（同花+顺子双听牌）', '干燥牌面（高牌主导，听牌很少）')
            reasoning = reasoning.replace('湿润牌面（同花听牌）', '干燥牌面（高牌主导，听牌很少）')
            reasoning = reasoning.replace('湿润牌面（如connected、suited、paired）有很多听牌，需要谨慎游戏。', 
                                       '干燥牌面（如A-high、K-high）有利于翻前加注者（IP），因为范围优势明显。')
    return reasoning

# 规则2：JTs在A♠ K♦ 2♣牌面有同花听牌，不应是"未命中牌面"
def fix_jts_on_ask_board(reasoning, hand_name, board_str):
    """修复JTs在同花牌面的评估"""
    if hand_name.startswith('JT') and 'A' in board_str and 'K' in board_str:
        # JTs有同花听牌（3张♠）
        reasoning = reasoning.replace('未命中牌面，可能是最弱牌', '同花听牌（3张♠），约35%胜率')
        reasoning = reasoning.replace('胜率约70%', '胜率约35%')
        reasoning = reasoning.replace('手牌评估：JTs在A♠ K♦ 2♣牌面的胜率约70%', 
                                   '手牌评估：JTs在A♠ K♦ 2♣牌面的胜率约35%（同花听牌）')
    return reasoning

# 规则3：有同花听牌的手牌，胜率应该是35%左右，不是50%+
def fix_flush_draw_equity(reasoning, hand_name):
    """修复同花听牌的胜率"""
    if 's' in hand_name and '同花听牌' in reasoning:
        reasoning = re.sub(r'胜率约\d+%', '胜率约35%', reasoning)
    return reasoning

# ========== 主处理逻辑 ==========

print("\n开始精准修复翻后题推理...")

# 找到所有scenario块
scenario_blocks = re.finditer(r'\{\s*id:\s*(\d+)[^}]*?reasoning:\s*\'([^\']*)\'', content, re.DOTALL)

new_content = content
fixed_count = 0

for match in scenario_blocks:
    scenario_text = match.group(0)
    scenario_id = int(match.group(1))
    old_reasoning = match.group(2)
    
    # 检查是否是翻后题（通过street字段）
    street_match = re.search(r'street:\s*\'([^\']+)\'', scenario_text)
    if not street_match or street_match.group(1) == 'preflop':
        continue  # 跳过翻前题
    
    # 提取board
    board_match = re.search(r'board:\s*\[([^\]]*)\]', scenario_text)
    if board_match:
        board_str_raw = board_match.group(1)
        board = [b.strip().strip("'\"") for b in board_str_raw.split(',') if b.strip()]
        board_str = ' '.join(board)
    else:
        board = []
        board_str = ''
    
    # 提取hand_name
    hand_match = re.search(r'hand:\s*\[([^\]]+)\]', scenario_text)
    hand_name = 'Unknown'
    if hand_match:
        hand_str = hand_match.group(1)
        cards = [c.strip().strip("'\"") for c in hand_str.split(',')]
        if len(cards) >= 2:
            if cards[0][1] == cards[1][1]:
                hand_name = cards[0][0] + cards[1][0] + 's'
            elif cards[0][1] != cards[1][1]:
                hand_name = cards[0][0] + cards[1][0] + 'o'
    
    # 应用修复规则
    new_reasoning = old_reasoning
    new_reasoning = fix_a_high_board(new_reasoning, board_str)
    new_reasoning = fix_jts_on_ask_board(new_reasoning, hand_name, board_str)
    new_reasoning = fix_flush_draw_equity(new_reasoning, hand_name)
    
    # 如果推理有变化，替换
    if new_reasoning != old_reasoning:
        # 转义新推理中的单引号
        new_reasoning_escaped = new_reasoning.replace("'", "\\'")
        # 替换
        old_pattern = r'reasoning:\s*\'' + re.escape(old_reasoning) + r'\''
        new_field = "reasoning: '" + new_reasoning_escaped + "'"
        new_content = new_content.replace(scenario_text, scenario_text.replace(old_reasoning, new_reasoning_escaped), 1)
        fixed_count += 1
        
        # 每修复10题打印一次
        if fixed_count % 10 == 0:
            print(f"已修复 {fixed_count} 道题...")

print(f"\n精准修复完成：共修复 {fixed_count} 道翻后题")

# 写入新文件
print("\n写入新文件...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'w') as f:
    f.write(new_content)

print(f"完成！新文件大小：{len(new_content)} 字符")
print("\n=== 精准修复完成 ===")
print("修复内容：")
print("1. A-high牌面：从'湿润'改为'干燥'")
print("2. JTs在A♠ K♦ 2♣：从'未命中'改为'同花听牌'")
print("3. 同花听牌胜率：从50%+改为约35%")
