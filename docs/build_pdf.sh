#!/bin/bash
# Build docs/DRAFT.pdf from docs/DRAFT.md with pandoc (pypandoc_binary) and headless Chromium.
set -e
cd "$(dirname "$0")"
python3 - <<'PY'
import pypandoc, pathlib
css = """
body{font-family:Georgia,serif;font-size:11pt;line-height:1.35;max-width:17cm;margin:1.5cm auto;color:#111}
h1{font-size:18pt;margin-top:0} h2{font-size:14pt;margin-top:1.4em} h3{font-size:12pt}
table{border-collapse:collapse;font-size:9.5pt;margin:0.6em 0} th,td{border:1px solid #999;padding:2px 6px;text-align:left}
code{font-family:Menlo,monospace;font-size:9.5pt} pre{background:#f4f4f4;padding:6px;font-size:9pt}
blockquote{border-left:3px solid #999;margin-left:0;padding-left:10px;color:#333}
"""
pathlib.Path("_draft.css").write_text(css)
pypandoc.convert_file("DRAFT.md", "html", outputfile="_draft.html",
    extra_args=["--standalone", "--mathml", "--css=_draft.css", "--metadata", "pagetitle=Recognition paths (working draft)"])
PY
CHROME=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell
$CHROME --no-sandbox --disable-gpu --headless --print-to-pdf=DRAFT.pdf --no-pdf-header-footer "file://$PWD/_draft.html" 2>/dev/null
rm -f _draft.html _draft.css
ls -la DRAFT.pdf
