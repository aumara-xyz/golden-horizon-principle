#!/bin/bash
# Observatory v3 self-check: run before every commit.
#   1. node --check on every non-JSON inline script
#   2. the frozen-fixture math harness (must be byte-identical to origin/main)
#   3. zh-math / zh-fixtures / fenceInner byte-identity against origin/main
#   4. claim-boundary lint: no NEW banned phrase may appear vs. the baseline
set -e
REPO="$1"
cd "$REPO"
HTML=instruments/zeta_harp_v2/public/observatory.html
TD=$(mktemp -d)

python3 - "$HTML" "$TD" <<'PY'
import re, sys, pathlib
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
out = pathlib.Path(sys.argv[2])
for m in re.finditer(r'<script id="([\w-]+)"([^>]*)>', html):
    sid, attrs = m.group(1), m.group(2)
    if 'application/json' in attrs:
        continue
    start = m.end()
    end = html.index('</script>', start)
    (out / (sid + '.js')).write_text(html[start:end], encoding='utf-8')
    print('extracted', sid)
PY

for f in "$TD"/*.js; do
  node --check "$f"
  echo "node --check $(basename "$f"): OK"
done

echo "--- fixture harness ---"
( cd instruments/zeta_harp_v2 && node reference/check_inline_math.mjs | tail -14 )

echo "--- byte identity vs origin/main ---"
git show origin/main:$HTML > "$TD/base.html"
python3 - "$TD/base.html" "$HTML" <<'PY'
import sys, pathlib, hashlib
def grab(t, a, b):
    i = t.index(a); j = t.index(b, i); return t[i:j+len(b)]
base = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
new  = pathlib.Path(sys.argv[2]).read_text(encoding='utf-8')
specs = [
    ('zh-math',     '<script id="zh-math">',       '</script>'),
    ('zh-fixtures', '<script id="zh-fixtures"',    '</script>'),
    ('fenceInner',  '<div id="fenceInner">',       '<h2>The Riemann fence</h2>'),
]
bad = 0
for name, a, b in specs:
    x, y = grab(base, a, b), grab(new, a, b)
    hx = hashlib.sha256(x.encode()).hexdigest()[:16]
    hy = hashlib.sha256(y.encode()).hexdigest()[:16]
    ok = x == y
    bad += 0 if ok else 1
    print(f"  {name:12s} base {hx}  new {hy}  {'IDENTICAL' if ok else 'CHANGED'}")
sys.exit(1 if bad else 0)
PY

echo "--- claim-boundary lint (no NEW banned phrase) ---"
python3 - "$TD/base.html" "$HTML" <<'PY'
import sys, pathlib, re
BANNED = [
    r'\bTrinity\b', r'54[- ]observers?', r'\bholograph', r'\bGHP\b',
    r'golden ratio', r'\bphi\b(?!\w)', r'φ-horizon',
    r'prove[sd]?\s+(the\s+)?RH', r'supports?\s+(the\s+)?RH',
    r'evidence\s+for\s+RH', r'first[- ]ever', r'\bfirst ever\b',
]
base = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
new  = pathlib.Path(sys.argv[2]).read_text(encoding='utf-8')
fail = 0
for pat in BANNED:
    b = len(re.findall(pat, base, re.I))
    n = len(re.findall(pat, new, re.I))
    flag = 'OK' if n <= b else 'NEW OCCURRENCE'
    if n > b:
        fail = 1
        print(f"  {pat:34s} base {b}  new {n}  {flag}")
        for m in re.finditer(pat, new, re.I):
            s = max(0, m.start()-70)
            print('      ...', new[s:m.end()+70].replace('\n', ' '))
    else:
        print(f"  {pat:34s} base {b}  new {n}  {flag}")
sys.exit(fail)
PY

echo "--- font-size floor (owner rule 9: nothing below 14px) ---"
python3 - "$HTML" <<'PY'
import sys, pathlib, re
html = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')
css = html[html.index('<style>'):html.index('</head>')]
bad = [m.group(0) for m in re.finditer(r'font-size:\s*([\d.]+)px', css)
       if float(m.group(1)) < 14]
print('  css declarations below 14px:', len(bad), bad[:8])
sys.exit(1 if bad else 0)
PY

rm -rf "$TD"
echo "SELF-CHECK PASS"
