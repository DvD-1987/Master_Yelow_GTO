#!/usr/bin/env python3
"""
复查全部500道题，统计生成情况和问题
"""
import re

# 读取文件
print("读取scenarios.js...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'r') as f:
    content = f.read()

print(f"文件大小：{len(content)} 字符")
print(f"总行数：{content.count(chr(10))} 行")

# ========== 统计信息 ==========
print("\n=== 基本统计 ===")

# 统计总题数
total_matches = list(re.finditer(r'id:\s*(\d+)', content))
total_count = len(total_matches)
print(f"总题数：{total_count}")

# 统计翻前/翻后
preflop_count = 0
postflop_count = 0
flop_count = 0
turn_count = 0
river_count = 0

for match in total_matches:
    id_pos = match.start()
    # 向后查找street字段
    chunk = content[id_pos:id_pos+200]
    street_match = re.search(r'street:\s*\'([^\']+)\'', chunk)
    if street_match:
        street = street_match.group(1)
        if street == 'preflop':
            preflop_count += 1
        else:
            postflop_count += 1
            if street == 'flop':
                flop_count += 1
            elif street == 'turn':
                turn_count += 1
            elif street == 'river':
                river_count += 1

print(f"翻前题（preflop）：{preflop_count}")
print(f"翻后题（postflop）：{postflop_count}")
print(f"  - flop：{flop_count}")
print(f"  - turn：{turn_count}")
print(f"  - river：{river_count}")

# 统计难度分布
print("\n=== 难度分布 ===")
for diff in ['beginner', 'intermediate', 'advanced']:
    count = len(re.findall(r'difficulty:\s*\'' + diff + r'\'', content))
    print(f"{diff}：{count} 题")

# 统计位置分布
print("\n=== 位置分布 ===")
for pos in ['UTG','UTG+1','MP','MP+1','LJ','HJ','CO','BTN','SB','BB']:
    count = len(re.findall(r'position:\s*\'' + pos + r'\'', content))
    print(f"{pos}：{count} 题")

# ========== 推理质量检查 ==========
print("\n=== 推理质量检查 ===")

# 检查推理长度
reasoning_lengths = []
reasoning_matches = re.finditer(r'reasoning:\s*\'([^\']*)\'', content, re.DOTALL)
for match in reasoning_matches:
    reasoning_text = match.group(1)
    reasoning_lengths.append(len(reasoning_text))

if reasoning_lengths:
    avg_len = sum(reasoning_lengths) / len(reasoning_lengths)
    min_len = min(reasoning_lengths)
    max_len = max(reasoning_lengths)
    print(f"推理长度：平均 {avg_len:.0f} 字符，最短 {min_len}，最长 {max_len}")
    
    # 检查是否有简短推理（可能是模板）
    short_count = sum(1 for l in reasoning_lengths if l < 100)
    print(f"简短推理（<100字符）：{short_count} 题")
    
    # 检查是否有详细推理（>500字符）
    detailed_count = sum(1 for l in reasoning_lengths if l > 500)
    print(f"详细推理（>500字符）：{detailed_count} 题")

# 检查常见错误模式
print("\n=== 错误模式检查 ===")

# 1. 检查是否还有"未命中牌面"的错误描述
missed_count = len(re.findall(r'未命中牌面', content))
print(f"仍存在'未命中牌面'描述：{missed_count} 处")

# 2. 检查是否还有牌面类型与下注建议不匹配
# 简化检查：找干燥牌面但建议2/3-满池的
dry_wet_bet = len(re.findall(r'干燥牌面.*2/3-满池', content))
print(f"干燥牌面但建议2/3-满池：{dry_wet_bet} 处")

wet_dry_bet = len(re.findall(r'湿润牌面.*1/2-2/3底池', content))
print(f"湿润牌面但建议1/2-2/3底池：{wet_dry_bet} 处")

# 3. 检查翻后推理是否包含5段结构
print("\n=== 结构完整性检查 ===")
has_all_sections = 0
for match in re.finditer(r'reasoning:\s*\'([^\']*)\'', content, re.DOTALL):
    reasoning = match.group(1)
    if all(x in reasoning for x in ['1. 牌面纹理', '2. 手牌评估', '3. GTO频率', '4. 具体策略', '5. 翻后计划']):
        has_all_sections += 1

print(f"包含完整5段结构的推理：{has_all_sections} 题")

# ========== 生成质量总结 ==========
print("\n=== 生成质量总结 ===")

# 翻前题质量（抽查）
preflop_good = 0
preflop_bad = 0
for match in total_matches:
    id_pos = match.start()
    chunk = content[id_pos:id_pos+500]
    if 'preflop' in chunk:
        if '翻前范围表' in chunk or '位置范围' in chunk:
            preflop_good += 1
        else:
            preflop_bad += 1

print(f"翻前题质量：良好（含详细内容）约 {preflop_good} 题，可能有问题约 {preflop_bad} 题")

# 翻后题质量（抽查）
postflop_good = 0
postflop_bad = 0
for match in total_matches:
    id_pos = match.start()
    chunk = content[id_pos:id_pos+500]
    if 'preflop' not in chunk:
        if '牌面纹理' in chunk and '手牌评估' in chunk:
            postflop_good += 1
        else:
            postflop_bad += 1

print(f"翻后题质量：良好（含详细内容）约 {postflop_good} 题，可能有问题约 {postflop_bad} 题")

print("\n=== 复查完成 ===")
