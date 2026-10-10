"""check.py 与 export_pdf.py 共用的小工具。"""
import os
import pathlib
import sys


def deck_url(path):
    p = pathlib.Path(path).expanduser().resolve()
    if not p.is_file():
        sys.exit(f"找不到 deck 文件: {p}")
    return p.as_uri()


def launch(playwright):
    """启动 headless Chromium。以 root 运行(常见于容器)时才加 --no-sandbox。"""
    args = ["--disable-dev-shm-usage"]
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        args.append("--no-sandbox")
    try:
        return playwright.chromium.launch(args=args)
    except Exception as e:  # 浏览器未安装或缺系统库
        sys.exit(
            "无法启动 Chromium: %s\n"
            "先运行: python -m playwright install chromium\n"
            "仍失败见 references/html-deck-kit.md 的「故障排查」。" % str(e).splitlines()[0]
        )


def goto_slide(page, index):
    """跳到第 index 页(从0起)。优先用骨架自带的 show(),否则直接切 class。"""
    page.evaluate(
        """i => {
            if (typeof show === 'function') { show(i); return; }
            document.querySelectorAll('.slide').forEach((s, j) => s.classList.toggle('active', j === i));
        }""",
        index,
    )
    page.wait_for_timeout(200)
