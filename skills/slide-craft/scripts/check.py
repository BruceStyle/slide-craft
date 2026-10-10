#!/usr/bin/env python3
"""逐页截图自查:截图 + 坏图检测 + 内容溢出提示。

用法:
  python check.py deck.html               # 检查全部页
  python check.py deck.html --page 7      # 只检查第7页(从1起)
  python check.py deck.html --out shots   # 指定截图输出目录(默认 ./check)

截图输出为 <out>/p01.png、p02.png……检查完后务必亲眼看截图,脚本只能发现坏图和溢出。
"""
import argparse
import pathlib
import sys

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _common import deck_url, goto_slide, launch  # noqa: E402

BROKEN_JS = """() => [...document.images]
  .filter(i => !i.complete || i.naturalWidth === 0)
  .map(i => i.getAttribute('src'))"""

OVERFLOW_JS = """() => {
  const s = document.querySelector('.slide.active');
  if (!s) return null;
  return { w: s.scrollWidth - s.clientWidth, h: s.scrollHeight - s.clientHeight };
}"""


def main():
    ap = argparse.ArgumentParser(description="slide deck 逐页截图自查")
    ap.add_argument("deck", help="deck 的 HTML 文件路径")
    ap.add_argument("--page", type=int, help="只检查这一页(从1起)")
    ap.add_argument("--out", default="check", help="截图输出目录")
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    problems = 0

    with sync_playwright() as p:
        b = launch(p)
        pg = b.new_page(viewport={"width": 1280, "height": 720})
        pg.goto(deck_url(a.deck))
        pg.wait_for_timeout(1200)

        n = pg.evaluate("document.querySelectorAll('.slide').length")
        if n == 0:
            sys.exit("页面里没有 .slide 元素,不是本骨架的 deck。")
        if a.page and not 1 <= a.page <= n:
            sys.exit(f"--page 超出范围,共 {n} 页。")
        pages = [a.page - 1] if a.page else range(n)

        for i in pages:
            goto_slide(pg, i)
            shot = out / f"p{i + 1:02d}.png"
            pg.screenshot(path=str(shot))
            line = f"P{i + 1:02d} -> {shot}"
            ov = pg.evaluate(OVERFLOW_JS)
            if ov and (ov["w"] > 1 or ov["h"] > 1):
                line += f"  [溢出] 横{max(ov['w'], 0)}px 纵{max(ov['h'], 0)}px"
                problems += 1
            print(line)

        broken = pg.evaluate(BROKEN_JS)
        if broken:
            problems += len(broken)
            print("坏图:")
            for src in broken:
                print("  ", src)
        else:
            print("坏图: 无")
        print(f"共 {n} 页")
        b.close()

    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
