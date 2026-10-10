# Slide Craft · slide 工艺

一个 Agent Skill：让 Claude 按"访谈 → 叙事大纲 → 风格比稿 → 逐页制作 → 整稿交付"的流程，和你一起把一份要讲给特定观众听的 deck 做出来。

> **先看这两点，再决定要不要装**
>
> 1. **产出是单文件 HTML 放映稿 + PDF，不是可编辑的 .pptx。** 需要在 PowerPoint 里继续改的，这个 skill 不合适（访谈和大纲两个阶段仍然可以单独用）。
> 2. **它是慢流程。** 每个阶段都要你确认才往下走，一页一审。只想快速出几页的，不要用它。

*English summary below.*

## 它做什么

| 阶段 | 做什么 | 过关条件 |
|---|---|---|
| 一 · 访谈与盘点 | 分轮提问，弄清观众、场合、目的、口径红线；盘点已有素材 | 能用三句话说清"观众 × 目的 × 希望对方会后转述的话" |
| 二 · 叙事与大纲 | 从"对方为什么需要你"倒推每页的存在理由，写逐页大纲 | 你认可大纲 |
| 三 · 风格定调 | 同一页做 5-6 种风格样稿，再做 5-6 种配色，翻页对比 | 你选定风格与配色 |
| 四 · 逐页制作 | 写一页、截图自查一页、给你看一页 | 每页你认可 |
| 五 · 整稿与交付 | 全稿走查，导出 HTML + PDF，整理交付包 | — |

贯穿全程的是八条审美律（每页一个视觉主角、标题自解释、图表形状即结论……）和四条协作律，详见 [`SKILL.md`](skills/slide-craft/SKILL.md)。

## 运行环境

| 环境 | 能用到什么程度 |
|---|---|
| 有命令行的 agent 环境（如 Claude Code） | 完整流程，含自动截图自查和 PDF 导出 |
| 没有命令行的对话环境 | 阶段一至三完整可用；阶段四、五走降级方案：由你在浏览器里打开 HTML 回传截图、用浏览器"打印为 PDF"导出 |

完整流程需要：

- Python 3.9+
- 依赖包：`playwright`、`img2pdf`、`python-pptx`、`Pillow`
- 一个 headless Chromium（由 playwright 安装）
- 可选：poppler（`pdftoppm`，导出后回看 PDF 用）

不需要安装任何字体，页面只使用系统字体。

## 安装

```bash
git clone https://github.com/BruceStyle/slide-craft.git

# 以 Claude Code 为例：拷到个人 skills 目录
cp -r slide-craft/skills/slide-craft ~/.claude/skills/

# 装脚本依赖
pip install -r ~/.claude/skills/slide-craft/scripts/requirements.txt
python -m playwright install chromium
```

其他支持 Agent Skills 的环境，把 `skills/slide-craft/` 整个文件夹按该环境的方式装入即可。

## 使用

直接说你要做什么，例如：

- "下周要给一家产业基金做 20 分钟路演，帮我做 deck。"
- "这是我们去年的公司介绍 PPT，想重做一版给渠道方看的。"

**触发范围是刻意收窄的**：明确要 .pptx、只是改现有 PPT 文件、或只想快速出几页时，它不会接手，这些请求会留给其他工具。如果你想让它在更多场合触发，改 `SKILL.md` 开头的 `description` 即可。

## 仓库结构

```
skills/slide-craft/
├── SKILL.md                     方法论主体：五阶段、审美律、协作律
├── references/
│   ├── aesthetics.md            版式细则与前后对照案例（案例为虚构场景）
│   └── html-deck-kit.md         HTML 骨架、脚本用法、降级方案、故障排查
└── scripts/
    ├── check.py                 逐页截图 + 坏图与溢出检测
    ├── export_pdf.py            HTML → PDF
    ├── extract_pptx.py          旧 PPT 的文字与图片提取
    └── requirements.txt
```

脚本也可以脱离 skill 单独使用：

```bash
python scripts/check.py deck.html --page 7
python scripts/export_pdf.py deck.html
python scripts/extract_pptx.py old.pptx
```

## 已知限制

- 不产出 .pptx，也不提供 HTML 转 .pptx。
- 不同操作系统上中文字形不同（macOS 苹方、Windows 微软雅黑），对外发送以 PDF 为准。
- PDF 是逐页图片打包，文字不可选中、不可搜索。
- 旧素材提取只支持 .pptx，不支持老的 .ppt。

## 许可证

- 代码(`scripts/` 与文档中的代码片段):[MIT](LICENSE)
- 方法论文档(`SKILL.md`、`references/`):[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans),改编和再发布请署名并附本仓库链接

---

## English

**Slide Craft** is an Agent Skill that walks Claude through building a presentation deck with you in five gated stages: interview, narrative outline, style bake-off, page-by-page build, and delivery.

- **Output is a single-file HTML deck plus a PDF, not an editable .pptx.** If you need a PowerPoint file, this is the wrong tool (the interview and outline stages are still usable on their own).
- **It is deliberately slow.** Every stage waits for your sign-off, and pages are reviewed one at a time.
- The skill text is written in Chinese; it works for decks in any language, but the instructions and examples are Chinese.
- The full workflow needs a shell, Python 3.9+, and headless Chromium (`pip install -r scripts/requirements.txt && python -m playwright install chromium`). Without a shell, stages 1-3 work as-is and stages 4-5 fall back to you opening the HTML and printing to PDF from the browser.
- License: MIT for code, CC BY 4.0 for the methodology text.
