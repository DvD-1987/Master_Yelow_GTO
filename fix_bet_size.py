#!/usr/bin/env python3
"""
修复下注建议与牌面类型不匹配的问题
批量检查所有翻后题，确保下注建议与牌面类型一致
"""
import re

# 读取文件
print("读取scenarios.js...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'r') as f:
    content = f.read()

print(f"文件大小：{len(content)} 字符")

# ========== 牌面分析函数（复制）==========
def analyze_board_texture(board):
    """精确分析牌面纹理"""
    if not board or len(board) < 3:
        return 'unknown', '未知牌面'
    
    cards = []
    for card in board:
        if card == '?':
            continue
        rank = card[0]
        suit = card[1] if len(card) > 1 else '?'
        cards.append((rank, suit))
    
    if len(cards) < 3:
        return 'unknown', '未知牌面'
    
    ranks = [c[0] for c in cards]
    suits = [c[1] for c in cards]
    
    is_paired = len(set(ranks)) < len(ranks)
    
    suit_counts = {}
    for s in suits:
        suit_counts[s] = suit_counts.get(s, 0) + 1
    max_suit_count = max(suit_counts.values()) if suit_counts else 0
    has_flush_draw = max_suit_count >= 3
    
    rank_order = {'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'T':10,'J':11,'Q':12,'K':13,'A':14}
    rank_nums = sorted([rank_order.get(r, 0) for r in ranks])
    
    has_straight_draw = False
    if len(rank_nums) >= 3:
        for i in range(len(rank_nums) - 2):
            if rank_nums[i+2] - rank_nums[i] <= 4:
                has_straight_draw = True
    
    if is_paired:
        if has_flush_draw or has_straight_draw:
            return 'wet', '成对湿润牌面（有听牌）'
        else:
            return 'dry', '成对干燥牌面（无听牌）'
    else:
        if has_flush_draw and has_straight_draw:
            return 'wet', '湿润牌面（同花+顺子双听牌）'
        elif has_flush_draw:
            return 'wet', '湿润牌面（同花听牌）'
        elif has_straight_draw:
            return 'wet', '湿润牌面（顺子听牌）'
        else:
            return 'dry', '干燥牌面（高牌主导，听牌很少）'

# ========== 主修复逻辑 ==========

print("\n开始修复下注建议与牌面类型不匹配的问题...")

# 找到所有翻后题的reasoning字段
reasoning_pattern = r'(id:\s*(\d+)[^}]*?street:\s*\'(?!preflop)([^\']+)\'[^}]*?board:\s*\[([^\]]*)\][^}]*?reasoning:\s*\')([^\']*)(\')'
matches = list(re.finditer(reasoning_pattern, content, re.DOTALL))

print(f"找到 {len(matches)} 个翻后题reasoning字段")

new_content = content
fixed_count = 0

for match in matches:
    full_match = match.group(0)
    scenario_id = match.group(2)
    street = match.group(3)
    board_str_raw = match.group(4)
    reasoning_text = match.group(5)
    
    # 解析牌面
    if board_str_raw.strip():
        board = [b.strip().strip("'\"") for b in board_str_raw.split(',') if b.strip()]
    else:
        board = []
    
    # 分析牌面类型
    board_type, board_desc = analyze_board_texture(board)
    
    # 检查reasoning中是否有不匹配的下注建议
    # 如果牌面是干燥，但reasoning中有"湿润牌面"的下注建议，则替换
    if board_type == 'dry':
        # 替换湿润牌面的下注建议为干燥牌面
        new_reasoning = reasoning_text
        
        # 替换1：下注大小建议
        new_reasoning = re.sub(r'下注大小建议：2/3-满池（湿润牌面）', '下注大小建议：1/2-2/3底池（干燥牌面）', new_reasoning)
        new_reasoning = re.sub(r'下注大小建议：2/3-满池（湿润牌面）\n', '下注大小建议：1/2-2/3底池（干燥牌面）\n', new_reasoning)
        
        # 替换2：策略部分（如果包含湿润牌面描述）
        new_reasoning = re.sub(r'湿润牌面（如connected、suited、paired）有很多听牌，需要谨慎游戏。', 
                              '干燥牌面（如A-high、K-high）有利于翻前加注者（IP），因为范围优势明显。', 
                              new_reasoning)
        
        # 替换3：IP/OOP策略（湿润->干燥）
        new_reasoning = re.sub(r'IP应该降低持续下注频率（50-60%），更多采用check-call策略。下注大小2/3-满池，保护听牌。', 
                              'IP（有位置）应该高频持续下注（70-80%），下注大小1/2-2/3底池。目标是让弱牌跟注，强牌弃牌。', 
                              new_reasoning)
        new_reasoning = re.sub(r'OOP应该更激进，用check-raise保护范围。湿润牌面check范围应该平衡：包含价值牌（慢打）和诈唬牌。', 
                              'OOP（无位置）应该check更多，用check-raise保护范围。如果check，IP通常会下注。', 
                              new_reasoning)
        
        if new_reasoning != reasoning_text:
            # 替换原内容
            new_reasoning_escaped = new_reasoning.replace("'", "\\'")
            old_full = reasoning_text
            new_full = new_reasoning_escaped
            
            # 构建新的完整匹配
            new_full_match = full_match.replace(old_full, new_full)
            new_content = new_content.replace(full_match, new_full_match, 1)
            fixed_count += 1
    
    elif board_type == 'wet':
        # 确保使用湿润牌面的下注建议
        new_reasoning = reasoning_text
        
        # 替换干燥牌面的下注建议为湿润牌面
        new_reasoning = re.sub(r'下注大小建议：1/2-2/3底池（干燥牌面）', '下注大小建议：2/3-满池（湿润牌面）', new_reasoning)
        
        if new_reasoning != reasoning_text:
            new_reasoning_escaped = new_reasoning.replace("'", "\\'")
            new_full_match = full_match.replace(reasoning_text, new_reasoning_escaped)
            new_content = new_content.replace(full_match, new_full_match, 1)
            fixed_count += 1

print(f"修复完成：共修复 {fixed_count} 道题的下注建议")

# 写入新文件
print("\n写入新文件...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'w') as f:
    f.write(new_content)

print(f"完成！新文件大小：{len(new_content)} 字符")
print("\n=== 下注建议修复完成 ===")
