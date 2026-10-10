# HTML Deck 技术配方

单文件HTML是高品质slide的最佳载体:排版精度是前端级的,放映零依赖,还能导出PDF。以下配方按需取用。脚本都在本skill的 `scripts/` 目录下,下文的 `scripts/xxx.py` 均相对于skill根目录。

## 0. 环境与依赖

脚本需要 Python 3.9+ 和一个 headless Chromium。首次使用前安装:

```bash
pip install -r scripts/requirements.txt
python -m playwright install chromium
```

装不上或没有命令行时,不要硬闯,走第7节的降级方案。

## 1. 放映框架骨架(单文件)

关键设计:1280×720固定舞台+JS等比缩放(任何屏幕自适应);每页一个 `<section class="slide">`;方向键/点击翻页;设计token全部收进 `:root` CSS变量;自带打印样式,浏览器"打印为PDF"时每页一张。

```html
<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>DECK</title>
<style>
  :root{ --bg:#FAFAF8; --ink:#1A1A1A; --muted:#6B6B6B; --line:#DCDCD6;
         --accent:#B4532A; --hl:#F3D9C8; --hl2:#F8ECE3; }  /* 占位配色,按阶段三选定的替换 */
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;background:#111;overflow:hidden;
    font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",sans-serif}
  #stage{position:absolute;left:50%;top:50%;width:1280px;height:720px;transform-origin:center}
  .slide{position:absolute;inset:0;display:none;overflow:hidden;
    background:var(--bg);color:var(--ink);padding:56px 68px}
  .slide.active{display:block}
  .mono{font-family:Menlo,Consolas,"DejaVu Sans Mono",monospace}
  .serif{font-family:Georgia,"Times New Roman",serif}  /* 中文自动回退宋体,数字衬线感 */
  .hd{display:flex;justify-content:space-between;align-items:baseline;
    border-bottom:2px solid var(--ink);padding-bottom:14px}
  .ft{position:absolute;left:68px;right:68px;bottom:22px;display:flex;
    justify-content:space-between;font-size:11px;color:var(--muted);
    letter-spacing:.1em;font-family:Menlo,Consolas,monospace}
  #nav{position:fixed;right:22px;bottom:16px;display:flex;gap:10px;z-index:99;
    font-family:Menlo,Consolas,monospace;color:#888;font-size:13px;align-items:center}
  #nav .btn{width:34px;height:34px;border:1px solid #555;border-radius:8px;
    display:flex;align-items:center;justify-content:center;cursor:pointer;
    color:#ccc;background:rgba(0,0,0,.55)}
  @media print{
    @page{size:1280px 720px;margin:0}
    html,body{height:auto;overflow:visible;background:none}
    #stage{position:static;width:auto;height:auto;transform:none!important}
    .slide{display:block!important;position:relative;width:1280px;height:720px;
      break-after:page;-webkit-print-color-adjust:exact;print-color-adjust:exact}
    #nav{display:none!important}
  }
</style></head><body>
<div id="stage">
  <section class="slide active"><!-- P1 --></section>
  <!-- 更多页 -->
</div>
<div id="nav"><div class="btn" onclick="go(-1)">&lsaquo;</div><span id="pg"></span><div class="btn" onclick="go(1)">&rsaquo;</div></div>
<script>
  const slides=[...document.querySelectorAll('.slide')];let cur=0;
  function show(i){cur=Math.max(0,Math.min(slides.length-1,i));
    slides.forEach((s,j)=>s.classList.toggle('active',j===cur));
    document.getElementById('pg').textContent=(cur+1)+' / '+slides.length}
  function go(d){show(cur+d)}
  addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))go(1);
    if(['ArrowLeft','PageUp'].includes(e.key))go(-1);
    if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1)});
  addEventListener('click',e=>{if(e.target.closest('#nav'))return;
    go(e.clientX>innerWidth/2?1:-1)});
  function fit(){const s=Math.min(innerWidth/1280,innerHeight/720);
    document.getElementById('stage').style.transform=`translate(-50%,-50%) scale(${s})`}
  addEventListener('resize',fit);fit();show(0);
</script></body></html>
```

注意:
- 页脚右侧留空,避免与#nav控件重叠。
- 素材一律相对路径(logo/xx.png、assets/xx.jpg),终稿与素材文件夹同级打包。
- 字体只用系统字体回退栈,不内嵌字体文件。不同系统上中文字形会有差异(macOS是苹方,Windows是微软雅黑),对外交付以PDF为准。
- 脚本靠 `.slide` 类名和 `show(i)` 函数翻页,改骨架时保留这两样。

## 2. 截图自查(每页必做)

```bash
python scripts/check.py deck.html --page 7     # 做完第7页后查这一页
python scripts/check.py deck.html              # 整稿走查,全部页
```

截图存到 `check/p07.png`。脚本会报两类问题:坏图(加载失败的图片路径)和内容溢出(内容超出1280×720的像素数)。遮挡、层级、间距节奏脚本看不出来,必须打开截图亲眼看,对照 SKILL.md 阶段四的自查清单。

有问题时脚本退出码为1,便于串在别的命令后面。

## 3. PDF导出(清晰且小)

```bash
python scripts/export_pdf.py deck.html             # 输出 deck.pdf
python scripts/export_pdf.py deck.html -o 交付.pdf
```

原理:每页2倍分辨率JPEG(质量87)→ img2pdf无重编码打包成16:9页面。20页约4-5MB,192dpi有效精度。脚本会自动隐藏翻页控件。要更清晰加 `--scale 3 --quality 92`,文件相应变大。

导出后抽一两页回看清晰度:直接打开PDF看,或用 `pdftoppm -png -r 100 -f 1 -l 2 deck.pdf preview`(需要poppler,可选)。

## 4. 旧PPT素材提取

```bash
python scripts/extract_pptx.py old.pptx
```

输出到 `old_extract/`:`text.txt`(逐页文字)、`media/`(内嵌的全部图片)、`index.jpg`(滤掉小图标后的带文件名缩略索引图)。把索引图交给用户圈选要用的素材。

只支持 .pptx;旧版 .ppt 请用户先另存为 .pptx。

## 5. Logo处理

- 透明底logo含文字时需裁纯图形部分:按alpha通道找内容行,行间空隙即图形与文字分界,PIL crop。
- 深色logo放浅色页可直接用;白底jpg logo统一放"白底衬片+1px细线边框"的规格卡内,杂色logo也显整齐。
- 中文文件名/空格文件名在file://下有兼容风险,复制为ASCII短名再引用。

## 6. 交付包结构

```
项目文件夹/
├── 1-终稿-交付/     ← deck.html + deck.pdf + 其引用的全部素材文件夹(相对路径成立)
├── 2-大纲历史/      ← v1..vN
├── 3-设计过程稿/    ← 风格比稿、配色比稿、旧版归档
└── 4-原始资料/      ← 源PPT、思维导图、原始图片
```
终稿文件夹必须自洽:整体拷贝或压缩后HTML照常放映。

## 7. 降级方案(没有命令行或装不了浏览器时)

流程照走,只是把机器做的检查换成人做:

- **截图自查** → 把当前HTML交给用户在浏览器里打开,请用户看这一页并回传截图;收到截图后按同一份自查清单检查。没有截图就不要声称"已自查"。
- **PDF导出** → 请用户在Chrome/Edge里打开deck,打印 → 另存为PDF,勾选"背景图形"、边距选"无"。骨架自带的打印样式会让每页slide占一张。
- **旧PPT提取** → 请用户直接把要用的文字和图片贴进对话或上传。

降级时在交付说明里写明哪些检查是用户代做的。

## 8. 故障排查

- **提示未安装浏览器**:`python -m playwright install chromium`。
- **Linux 上报缺系统库**(libnss3、libXdamage 等):有root时 `python -m playwright install-deps chromium`。没有root的容器环境里,可以 `apt-get download <包名>` 后 `dpkg -x <包>.deb <目录>`,再用 `LD_LIBRARY_PATH=<目录>/usr/lib/<架构>` 运行脚本。macOS 和 Windows 不会遇到这个问题。
- **截图里中文是方块**:系统缺中文字体,多见于精简的Linux容器。装一个Noto Sans CJK(如 `apt-get install fonts-noto-cjk`)即可。
- **本地图片不显示**:检查是否用了相对路径、文件名是否含中文或空格(见第5节)。
