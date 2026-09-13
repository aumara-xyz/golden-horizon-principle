#!/bin/zsh
cd "$(dirname "$0")"
for L in 0.4 0.5 0.6 0.7; do for P in even odd; do /private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad/weilenv/bin/python d22_certify.py $L 160 160 48 $P > cert_${P}_L${L}_T160_N160.log 2>&1; grep -E "CERT DONE|Traceback" cert_${P}_L${L}_T160_N160.log; done; done
for P in even odd; do /private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad/weilenv/bin/python d22_certify.py 0.7 240 192 48 $P > cert_${P}_L0.7_T240_N192.log 2>&1; grep -E "CERT DONE|Traceback" cert_${P}_L0.7_T240_N192.log; done
echo BATCH DONE
