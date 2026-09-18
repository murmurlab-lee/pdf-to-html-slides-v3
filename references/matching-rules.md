# Template Matching Rules

PDF页面 → 模板匹配决策树。规则引擎按优先级匹配，LLM处理模糊情况。

## 匹配决策树

```
页面特征
│
├─ 第1页? ──→ cover (confidence: 95)
│
├─ 0张图 + 有文字? ──→ text-center (confidence: 90)
│
├─ 1张图 + 文字<80字? ──→ image-full (confidence: 85)
│
├─ 1张图 + 文字≥80字? ──→ split (confidence: 85)
│
├─ 2-4张图? ──→ image-grid (confidence: 75)
│
├─ 5+张图? ──→ image-grid (confidence: 75)
│
└─ (fallback) ──→ text-center (confidence: 60)
```

## 特殊关键词映射

| 关键词/上下文 | 倾向模板 |
|---|---|
| 平面图/剖面图/分析图/日照分析 | image-draw |
| 效果图/渲染图/透视图 | image-full |
| 封面/标题页/项目名称 | cover |
| 公司介绍/团队/成立/建筑师 | about |
| 艺术家/策展/展览/人物 | dark-text-image |
| 材料/色卡/样板/策略 | split |
| 引言/致谢/结语/理念 | text-center |

## LLM介入时机

当规则引擎 confidence < 80 时，标记为ambiguous，由agent通过vision能力查看缩略图后决定。

agent的输入：
- 页面缩略图路径
- 提取的文字前200字
- 图片数量
- 规则引擎的初步判断

agent的输出：
- 确认或修改模板类型
- 置信度评分
- 理由
