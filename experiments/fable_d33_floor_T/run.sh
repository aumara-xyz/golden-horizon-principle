#!/bin/zsh
cd "$(dirname "$0")"
for P in odd even; do /private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad/weilenv/bin/python d30_certify.py 0.6 240 192 48 $P > log_${P}_T240.log 2>&1; grep -E "CERT DONE|Traceback" log_${P}_T240.log; done
for P in odd even; do /private/tmp/claude-501/-Users-peterviviani-Library-Mobile-Documents-com-apple-CloudDocs-AUMARA---AURACLE-BREAK-THROUGHS----GOLDEN-HORIZON-PRINCIPLE---/473084a9-1951-40be-aa45-7ac8696063c9/scratchpad/weilenv/bin/python d30_certify.py 0.6 320 256 48 $P > log_${P}_T320.log 2>&1; grep -E "CERT DONE|Traceback" log_${P}_T320.log; done
echo RUN DONE
