#!/usr/bin/env python3
"""
修复"未命中牌面"错误描述
根据手牌在牌面的实际强度，替换为正确描述
"""
import re

# 读取文件
print("读取scenarios.js...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'r') as f:
    content = f.read()

print(f"文件大小：{len(content)} 字符")

# ========== 精准修复"未命中牌面" ==========

# 分析手牌在牌面的强度，返回正确描述
def get_correct_description(hand_name, board):
    """根据手牌和牌面，返回正确的强度描述"""
    if not hand_name or len(hand_name) < 2:
        return '未知手牌'
    
    # 解析手牌
    hand_ranks = [c for c in hand_name if c in '23456789TJQKA']
    board_ranks = [c[0] for c in board if c != '?']
    
    # 检查是否命中牌面（成对）
    made_pair = any(r in board_ranks for r in hand_ranks)
    made_top_pair = any(r in board_ranks and r in ['A','K','Q'] for r in hand_ranks)
    
    # 检查听牌
    has_suit = 's' in hand_name
    board_suits = [c[1] for c in board if c != '?']
    has_flush_draw = has_suit and sum(1 for s in board_suits if s == hand_name[1]) >= 2  # 简化：手牌同花且牌面有2+张同花色
    
    has_connect = False
    if len(hand_ranks) >= 2:
        rank_order = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
        hand_nums = [rank_order.get(r,0) for r in hand_ranks]
        board_nums = [rank_order.get(r,0) for r in board_ranks]
        all_nums = sorted(hand_nums + board_nums)
        for i in range(len(all_nums)-1):
            if all_nums[i+1] - all_nums[i] <= 4:  # 简化：有顺子潜力
                has_connect = True
                break
    
    # 返回正确描述
    if made_top_pair:
        return '顶对或更好，很可能是最好牌'
    elif made_pair:
        return '中间对，可能是最好牌，但容易被反超'
    elif has_flush_draw and has_connect:
        return '同花+顺子双听牌，约45%胜率'
    elif has_flush_draw:
        return '同花听牌，约35%胜率'
    elif has_connect:
        return '顺子听牌，约32%胜率'
    else:
        return '未命中牌面，可能是最弱牌'  # 只有这里才保留"未命中牌面"

# 修复"未命中牌面"的主逻辑
print("\n开始修复'未命中牌面'错误描述...")

# 找到所有包含"未命中牌面"的scenario
pattern = r'(\{\s*id:\s*(\d+)[^}]*?hand:\s*\[([^\]]+)\][^}]*?board:\s*\[([^\]]*)\][^}]*?reasoning:\s*\'[^\']*未命中牌面[^\']*\')'
matches = list(re.finditer(pattern, content, re.DOTALL))

print(f"找到 {len(matches)} 个包含'未命中牌面'的scenario")

new_content = content
fixed_count = 0

for match in matches:
    scenario_text = match.group(0)
    scenario_id = match.group(2)
    hand_str = match.group(3)
    board_str_raw = match.group(4)
    
    # 解析hand_name
    cards = [c.strip().strip("'\"") for c in hand_str.split(',')]
    if len(cards) >= 2:
        if cards[0][1] == cards[1][1]:
            hand_name = cards[0][0] + cards[1][0] + 's'
        elif cards[0][1] != cards[1][1]:
            hand_name = cards[0][0] + cards[1][0] + 'o'
        else:
            hand_name = cards[0][0] + cards[1][0]
    else:
        continue
    
    # 解析board
    if board_str_raw.strip():
        board = [b.strip().strip("'\"") for b in board_str_raw.split(',') if b.strip()]
    else:
        board = []
    
    # 获取正确描述
    correct_desc = get_correct_description(hand_name, board)
    
    # 如果还是"未命中牌面"，跳过（真的未命中）
    if '未命中牌面' in correct_desc:
        continue
    
    # 替换reasoning中的"未命中牌面"部分
    old_reasoning_match = re.search(r'reasoning:\s*\'([^\']*未命中牌面[^\']*)\'', scenario_text)
    if not old_reasoning_match:
        continue
    
    old_reasoning = old_reasoning_match.group(1)
    
    # 替换描述部分（在reasoning中找到"未命中牌面，..."并替换）
    new_reasoning = re.sub(r'未命中牌面，可能是最弱牌', correct_desc, old_reasoning)
    new_reasoning = re.sub(r'未命中牌面', correct_desc, new_reasoning)  # 更通用的替换
    
    if new_reasoning != old_reasoning:
        # 转义
        new_reasoning_escaped = new_reasoning.replace("'", "\\'")
        new_scenario_text = scenario_text.replace(old_reasoning, new_reasoning_escaped)
        
        if new_scenario_text != scenario_text:
            new_content = new_content.replace(scenario_text, new_scenario_text, 1)
            fixed_count += 1
            
            if fixed_count % 20 == 0:
                print(f"已修复 {fixed_count} 处...")

print(f"\n修复完成：共修复 {fixed_count} 处'未命中牌面'错误描述")

# 验证还有多少处残留
remaining = len(re.findall(r'未命中牌面', new_content))
print(f"残留'未命中牌面'：{remaining} 处（这些是真未命中的牌）")

# 写入新文件
print("\n写入新文件...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'w') as f:
    f.write(new_content)

print(f"完成！新文件大小：{len(new_content)} 字符")
print("\n=== '未命中牌面'修复完成 ===")
