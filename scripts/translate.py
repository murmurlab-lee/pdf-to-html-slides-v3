#!/usr/bin/env python3
"""Simple CN->EN translation for architectural terms.

Rules:
- If text is Chinese -> translate to English
- If text is English -> keep as-is, no Chinese translation
- If text already has CN\nEN format -> parse as-is
- Translation happens at build time, stored in titleEn field
"""

import re

# Common architectural terms dictionary
# Sorted by length (longest first) for greedy matching
DICT = {
    '新功能主义': 'Neo-Functionalism',
    '功能主义': 'Functionalism',
    '构造骨架化': 'Structural Skeletonization',
    '新功能': 'Neo-Functional',
    '城市考古学': 'Urban Archaeology',
    '短暂逃离': 'A Brief Escape',
    '积蓄能量': 'To Gather Energy',
    '慢慢攀': 'Climbing Slowly',
    '自由行走': 'Free Movement',
    '仔细聆听': 'Listen Carefully',
    '没有屋顶': 'A Roofless',
    '围墙参考': 'Enclosure Reference',
    '柔性材料': 'Flexible Materials',
    '老木板': 'Reclaimed Wood',
    '木蜡油': 'Wood Wax Oil',
    '薄木条': 'Thin Wood Slats',
    '水杉林': 'Metasequoia Forest',
    '围墙': 'Enclosure',
    '围合': 'Enclosure',
    '考古学': 'Archaeology',
    '考古': 'Archaeology',
    '界面': 'Interface',
    '对望': 'Gazing Across',
    '漂浮': 'Floating',
    '改造': 'Renovation',
    '设计': 'Design',
    '概念': 'Concept',
    '方案': 'Proposal',
    '策略': 'Strategy',
    '分析': 'Analysis',
    '研究': 'Research',
    '探索': 'Exploration',
    '材料': 'Materials',
    '柔性': 'Flexible',
    '着色': 'Stained',
    '构造': 'Tectonic',
    '骨架化': 'Skeletonization',
    '骨架': 'Skeleton',
    '结构': 'Structure',
    '空间': 'Space',
    '室内': 'Interior',
    '功能': 'Function',
    '关系': 'Relationships',
    '底层': 'Ground Floor',
    '城市': 'Urban',
    '参考': 'Reference',
    '场地': 'Site',
    '低语': 'Whispers',
    '想象': 'Imagine',
    '房间': 'Room',
    '空旷': 'Open',
    '草地': 'Meadow',
    '安顿': 'Settle',
    '收纳': 'Embrace',
    '情绪': 'Emotions',
    '空中': 'Into the Air',
    '树屋': 'Treehouse',
    '自由': 'Free',
    '林间': 'In the Woods',
    '掩映': 'Nestled',
    '小房子': 'Cottage',
    '一组': 'A Set of',
    '留下': 'Leaving Behind',
    '土地': 'Earth',
    '静物': 'Still Life',
    '疗愈所': 'A Place of Healing',
    '从树上': 'From the Trees',
    '长出来': 'Growing',
    '无序': 'Disorder',
    '藏着': 'Hides',
    '秩序': 'Order',
    '误入': 'Stumbling Into',
    '安静': 'Quiet',
    '热闹是他们的': 'The Bustle Is Theirs',
    '致力于': 'Dedicated to',
    '建筑学': 'Architecture',
    '回归': 'Returning to',
    '常识': 'Common Sense',
    '走向': 'Towards',
    '大众': 'The Public',
    '序': 'Preface',
}


def is_chinese(text):
    """Check if text contains Chinese characters."""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def translate(text):
    """Translate Chinese text to English.
    
    Returns:
        (cn_text, en_text) tuple
        - If input has CN\nEN format: returns (cn, en) as-is
        - If input is English only: returns ("", en)
        - If input is Chinese: returns (cn, en_translated)
    """
    if not text or not text.strip():
        return "", ""
    
    text = text.strip()
    
    # Already has newline = pre-formatted bilingual
    if '\n' in text:
        parts = [p.strip() for p in text.split('\n') if p.strip()]
        if len(parts) >= 2:
            if is_chinese(parts[0]):
                return parts[0], parts[1]
            else:
                return "", parts[0]
        elif parts:
            return ("", parts[0]) if not is_chinese(parts[0]) else (parts[0], "")
        return "", ""
    
    # Pure English
    if not is_chinese(text):
        return "", text
    
    # Pure Chinese -> translate
    if text in DICT:
        return text, DICT[text]
    
    # Segment-based translation
    sorted_keys = sorted(DICT.keys(), key=len, reverse=True)
    remaining = text
    
    for key in sorted_keys:
        if key in remaining:
            remaining = remaining.replace(key, DICT[key] + ' ')
    
    en = remaining.strip()
    if en and en != text:
        en = ' '.join(en.split())
        # Remove any remaining Chinese characters (unmatched particles like 的/在/了)
        en = re.sub(r'[\u4e00-\u9fff]', '', en)
        en = ' '.join(en.split())
        en = en[0].upper() + en[1:] if en else en
        return text, en
    
    return text, text


if __name__ == "__main__":
    test_cases = [
        "围墙参考",
        "城市考古学",
        "构造骨架化",
        "柔性材料",
        "Thx",
        "After the Winter",
        "城市考古学\nUrban Archaeology",
    ]
    for t in test_cases:
        cn, en = translate(t)
        print(f"'{t}' -> cn='{cn}', en='{en}'")
