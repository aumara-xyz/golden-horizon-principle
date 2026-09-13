#!/bin/zsh
cd "$(dirname "$0")"
export TRUNC=0
for f in d22_cand2_even_L0.4.json d22_cand2_odd_L0.4.json d22_cand2_even_L0.5.json d22_cand2_odd_L0.5.json d22_cand2_even_L0.6.json d22_cand2_odd_L0.6.json d22_cand2_even_L0.7.json d22_cand2_odd_L0.7.json; do
  echo "== $f"; /private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad/weilenv/bin/python d22_score.py $f 128 256 512 2>&1 | grep -v -E "Warning|^compact" | grep -E "cutoff|SCORE DONE|Traceback|Error"
done
echo "== control R160<=R240<=W on even L0.5"; /private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad/weilenv/bin/python d22_score.py d22_cand2_even_L0.5.json 160 240 2>&1 | grep -v -E "Warning|^compact" | grep -E "cutoff|SCORE DONE|Traceback|Error"
echo SCORES4 DONE
