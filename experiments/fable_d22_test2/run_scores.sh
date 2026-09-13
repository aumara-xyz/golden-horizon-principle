#!/bin/zsh
cd "$(dirname "$0")"
for f in d22_cert_even_L0.4_T160_N160.json d22_cert_odd_L0.4_T160_N160.json d22_cert_even_L0.5_T160_N160.json d22_cert_odd_L0.5_T160_N160.json d22_cert_even_L0.6_T160_N160.json; do
  /private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad/weilenv/bin/python d22_score.py $f 128 256 512 2>&1 | grep -v -E "Warning|^compact" | grep -E "cutoff|SCORE DONE|Traceback|Error"
done
echo SCORES1 DONE
