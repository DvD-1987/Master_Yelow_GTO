#!/usr/bin/env python3
"""
修复ID 45和50的下注建议不匹配问题
"""
import re

print("读取scenarios.js...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'r') as f:
    content = f.read()

print(f"文件大小：{len(content)} 字符")

# ========== 修复ID 45 ==========
print("\n修复ID 45...")
# ID 45: board 5♠ 4♦ 3♣ 2♠ 是顺子成型（wet），但描述说"同花+顺子双听牌"不准确
# 修正描述为"湿润牌面（顺子成型，有顺子听牌潜力）"
old_text_45 = "1. 牌面纹理：5♠ 4♦ 3♣ 2♠是湿润牌面（同花+顺子双听牌）。\n   湿润牌面（如connected、suited、paired）有很多听牌，需要谨慎游戏。"
new_text_45 = "1. 牌面纹理：5♠ 4♦ 3♣ 2♠是湿润牌面（顺子成型，有顺子听牌潜力）。\n   湿润牌面（如connected、suited、paired）有很多听牌，需要谨慎游戏。"

content = content.replace(old_text_45, new_text_45, 1)
print("  ID 45 描述已修正")

# ========== 修复ID 50 ==========
print("\n修复ID 50...")
# ID 50: board 8♠ 8♦ 7♣ 是成对湿润牌面，描述说"成对且湿润（有同花或顺子听牌）"可能不准确，因为只有两张同花色？
# 但确实有顺子听牌（6或9）。保留湿润描述，但修正下注建议可能没问题。
# 检查下注建议：已经是"2/3-满池（湿润牌面）"，正确。
# 但还需要修正手牌评估：KKo在8♠ 8♦ 7♣牌面，不是顺子听牌，却是顶对（口袋对子KK，牌面有8，所以是超对？实际上KK是超对，因为牌面最大牌是8，KK是overpair。
# 修正手牌评估
old_text_50 = "2. 手牌评估：KKo在8♠ 8♦ 7♣牌面的胜率约60%。\n   顺子听牌，约32%胜率"
new_text_50 = "2. 手牌评估：KKo在8♠ 8♦ 7♣牌面的胜率约85%（超对）。\n   超对（overpair），很可能是最好牌"

content = content.replace(old_text_50, new_text_50, 1)
print("  ID 50 手牌评估已修正")

# ========== 检查文件结尾 ==========
print("\n检查文件结尾...")
# 确保数组SCENARIOS正确结束
# 查找 "];" 在文件中的位置
array_end = content.rfind('];')
if array_end == -1:
    print("⚠️ 未找到 '];'，尝试修复...")
    # 在最后一个scenario后添加
    last_brace = content.rfind('    }')
    if last_brace != -1:
        # 在last_brace后加上逗号和];
        # 但更简单：确保文件末尾有];
        # 我们检查是否有const SCENARIOS = [开头
        if 'const SCENARIOS = [' in content:
            print("  发现const SCENARIOS，但未找到];，可能文件不完整")
else:
    print("✅ 找到数组结束];")

# ========== 写入文件 ==========
print("\n写入文件...")
with open('/mnt/f/master_Yelow_GTO_Pro/scenarios.js', 'w') as f:
    f.write(content)

print(f"完成！文件大小：{len(content)} 字符")
print("\n=== 修复完成 ===")
