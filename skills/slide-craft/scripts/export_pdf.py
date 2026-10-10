#!/usr/bin/env python3
"""把 HTML deck 导出为 PDF:每页2倍分辨率 JPEG,再用 img2pdf 无重编码打包。

用法:
  python export_pdf.py deck.html                 # 输出 deck.pdf(与 HTML 同目录)
  python export_pdf.py deck.html -o out.pdf
  python export_pdf.py deck.html --scale 3 --quality 92   # 更清晰,文件更大

导出时会自动隐藏翻页控件(#nav)。默认参数下 20 页约 4-5MB。
"""
import argparse
import pathlib
import sys
import tempfile

import img2pdf
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from _common import deck_url, goto_slide, launch  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="HTML deck 导出 PDF")
    ap.add_argument("deck", help="deck 的 HTML 文件路径")
    ap.add_argument("-o", "--output", help="输出 PDF 路径")
    ap.add_argument("--scale", type=float, default=2, help="截图倍率,默认2")
    ap.add_argument("--quality", type=int, default=87, help="JPEG 质量,默认87")
    a = ap.parse_args()

    deck = pathlib.Path(a.deck).expanduser().resolve()
    out = pathlib.Path(a.output) if a.output else deck.with_suffix(".pdf")

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        b = launch(p)
        pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=a.scale)
        pg.goto(deck_url(deck))
        pg.wait_for_timeout(1800)
        pg.evaluate("() => { const n = document.getElementById('nav'); if (n) n.style.display = 'none'; }")

        n = pg.evaluate("document.querySelectorAll('.slide').length")
        if n == 0:
            sys.exit("页面里没有 .slide 元素,不是本骨架的 deck。")

        shots = []
        for i in range(n):
            goto_slide(pg, i)
            f = pathlib.Path(tmp) / f"p{i + 1:03d}.jpg"
            pg.screenshot(path=str(f), type="jpeg", quality=a.quality)
            shots.append(str(f))
        b.close()

        # 16:9 标准页面尺寸
        layout = img2pdf.get_layout_fun((img2pdf.cm_to_pt(33.867), img2pdf.cm_to_pt(19.05)))
        out.write_bytes(img2pdf.convert(shots, layout_fun=layout))

    print(f"{out}  {n} 页  {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
