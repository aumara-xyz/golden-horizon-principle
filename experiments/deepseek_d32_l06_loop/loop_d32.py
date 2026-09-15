#!/usr/bin/env python3
"""D28 Task 2: construction-rule loop.

Protocol (per Astra's directive):
  - up to 8 iterations; the proposer edits ONLY construct_candidate.py;
  - the court scores the output; the ratio, the diff and the model call are
    receipted; keep the edit only if the ratio improves.
  - frozen surface: court_frozen_dojo.py, court_frozen_score.py, court_score.py,
    PREDICTIONS.md are hash-checked before and after every iteration; any change
    is a tombstone with the diff, never an apply.
  - loop receipts are court runs at T=160 (the affordable cutoff, declared);
    the winning candidate is certified at the metric cutoff T=1024 once.
  - escalation ladder when two consecutive iterations fail to improve:
    deepseek/deepseek-v4.1-flash -> z-ai/glm-5.3-flash -> qwen/qwen3.8-27b.
Budget: --court-min budget (default 45), --wall-min (default 90).
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

HERE = Path(__file__).parent
FROZEN = ['../deepseek_d28_construction_loop/court_frozen_dojo.py', '../deepseek_d28_construction_loop/court_frozen_score.py', '../deepseek_d28_construction_loop/court_score.py', 'PREDICTIONS.md']
CASES = ['l06-odd', 'l06-even']
CRED = Path.home() / '.dsh' / '.credentials.yaml'
LADDER = ['deepseek/deepseek-v4.1-flash', 'z-ai/glm-5.3-flash', 'qwen/qwen3.8-27b']
KEY_FOR = {'deepseek/deepseek-v4.1-flash': 'OPENROUTER_API_KEY',
           'z-ai/glm-5.3-flash': 'OPENROUTER_KEY_GLM',
           'qwen/qwen3.8-27b': 'OPENROUTER_KEY_QWEN'}

def load_keys():
    keys = {}
    for line in CRED.read_text().splitlines():
        m = re.match(r'^\s*([A-Z_]+):\s*(\S+)', line)
        if m:
            keys[m.group(1)] = m.group(2).strip().strip('"')
    return keys

def frozen_hashes():
    return {f: hashlib.sha256((HERE / f).resolve().read_bytes()).hexdigest() for f in FROZEN}

def llm_call(model, messages, keys, timeout=300):
    key = keys[KEY_FOR[model]]
    body = json.dumps({'model': model, 'messages': messages, 'temperature': 0.4,
                       'max_tokens': 32000, 'reasoning': {'max_tokens': 3000}}).encode()
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=body,
                                 headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read())
    return data, round(time.time() - t0, 1)

def extract_code(text):
    import ast
    blocks = re.findall(r'```(?:python)?\s*\n(.*?)(?:\n```|\Z)', text, re.S)
    valid = []
    for b in blocks:
        try:
            ast.parse(b)
            valid.append(b.rstrip())
        except SyntaxError:
            pass
    return valid[-1] if valid else None

def run_iteration_source(src, iter_dir, timeout=420):
    iter_dir.mkdir(exist_ok=True)
    f = iter_dir / 'construct_candidate.py'
    f.write_text(src)
    r = subprocess.run([sys.executable, str(f)], cwd=iter_dir, capture_output=True, text=True, timeout=timeout)
    saved = re.findall(r'\[saved\] (\S+)  proxy_ratio=([0-9.]+)', r.stdout)
    return r.returncode, r.stdout, r.stderr, saved

def court_T160(case, cand_path):
    t0 = time.time()
    r = subprocess.run([sys.executable, str(HERE.parent / 'deepseek_d28_construction_loop' / 'court_score.py'), case, str(cand_path), '--T', '160'],
                       cwd=HERE, capture_output=True, text=True, timeout=1800)
    secs = time.time() - t0
    m = re.search(r'inf_ratio=\[?([0-9.]+) wave_lo_ratio=\[?([0-9.]+) gate\(lo<1\.1\)=(\w+)', r.stdout)
    if not m:
        return None
    return {'inf_ratio_T160': float(m.group(1)), 'wave_lo_ratio_T160': float(m.group(2)),
            'gate_lo_T160': m.group(3) == 'True', 'seconds': round(secs, 1), 'court_min': secs / 60}

def proposer_prompt(current_src, state, case_results, iteration, escalated):
    return f"""You are a construction-rule proposer for a certified numerical optimization loop.

CONTEXT
Two open cases sit exactly at the method's located edge (L=0.6), where the incumbent
construction rule's candidate sits 22 percent above the certified floor on the compact
term alone (W_lo/ell = 1.221), so no tail improvement can close them:
- l06-odd: L=0.6, parity odd, certified floor ell=4.89029307909781e-7, incumbent certified ratio 1.2869 (gate needs < 1.1)
- l06-even: L=0.6, parity even, certified floor ell=1.31162554371630e-9, incumbent certified ratio 1.3383 (gate needs < 1.1)
The metric is ratio = W_hi(candidate, T=1024 mass-conditioned tail) / ell. Lower is better. A gate passes when the certified wave-lower endpoint ratio W_lo/ell < 1.1.

You may rewrite the FILE BELOW however you like, but ONLY this file. This round's specific
levers (per the round's directive): the CONSTRAINT ORDER (which boundary/orthogonality
constraints apply, in what sequence, at which mode counts) and the PENALTY FORM (different
smoothness/mass/endpoint operators, staged or annealed schedules). Also available: basis/family
choices, mode count, damping schedules, eigenvalue selection strategy.
FORBIDDEN (would be tombstoned): changing the scoring, the tail machinery, floors, L or T; writing or reading files other than the candidates this script itself emits; anything outside this file.

LATEST MEASUREMENTS (proxy at T=1024 from the current file; court receipts at T=160)
{json.dumps(case_results, indent=1)[:2000]}

CURRENT FILE (iteration {iteration}, {'ESCALATED' if escalated else 'cheap model'}):
{current_src}

Return ONLY one fenced python code block containing the complete replacement file -- no prose before or after, and do not truncate it (the file is small). Keep it runnable as-is: `python3 construct_candidate.py` must run to completion in under 6 minutes and, for EACH case, must write a JSON named candidate_<case>_vN.json (case tokens l05_odd, l04_even) and print `[saved] <that filename>  proxy_ratio=<value>`. File naming and the proxy_ratio JSON field are the harness contract; the construction rule is yours. Improve the proxy while honestly reducing the certified ratio: penalize tail mass (boundary jump, derivative norm), and prefer candidates whose wave enclosure is tight."""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--iters', type=int, default=8)
    ap.add_argument('--court-min', type=float, default=45)
    ap.add_argument('--wall-min', type=float, default=90)
    ap.add_argument('--start', type=int, default=1)
    args = ap.parse_args()
    keys = load_keys()
    hashes_before = frozen_hashes()
    receipts = []
    state = {}
    # incumbents at T=160 (baseline court receipts for comparison)
    for case, cand in [('l06-odd', '../deepseek_d30_edge/candidate_l06_odd_d30.json'),
                       ('l06-even', '../deepseek_d30_edge/candidate_l06_even_d30.json')]:
        c = court_T160(case, HERE / cand)
        state[case] = {'proxy': None, 'court': c}
        print(f"[incumbent {case}] {c}", flush=True)
    current_src = (HERE / 'construct_candidate.py').read_text()
    court_used = 0.0
    wall0 = time.time()
    fails = 0
    for it in range(args.start, args.start + args.iters):
        if court_used > args.court_min or (time.time() - wall0) / 60 > args.wall_min:
            print(f"[budget] court_min={court_used:.1f} wall_min={(time.time()-wall0)/60:.1f} -- stop", flush=True)
            break
        model = LADDER[0] if fails < 2 else LADDER[min(2, fails - 1)]
        iter_dir = HERE / f'iter{it:02d}'
        prompt = proposer_prompt(current_src, state, state, it, model != LADDER[0])
        try:
            data, secs = llm_call(model, [{'role': 'user', 'content': prompt}], keys)
            content = data['choices'][0]['message']['content']
            usage = data.get('usage', {})
        except Exception as e:
            rec = {'iter': it, 'model': model, 'action': 'tombstone', 'reason': f'llm-failed: {e}'}
            receipts.append(rec); fails += 1
            (HERE / 'loop-receipts.jsonl').write_text('\n'.join(json.dumps(r) for r in receipts) + '\n')
            print(f"[iter {it}] LLM call failed: {e}", flush=True)
            continue
        code = extract_code(content or '')
        rec = {'iter': it, 'model': model, 'call_seconds': secs, 'usage': usage,
               'content_chars': len(content or '')}
        if not code:
            rec.update({'action': 'tombstone', 'reason': 'no code block'})
            receipts.append(rec); fails += 1
            (HERE / 'loop-receipts.jsonl').write_text('\n'.join(json.dumps(r) for r in receipts) + '\n')
            print(f"[iter {it}] tombstone: no code block (content_chars={rec['content_chars']})", flush=True)
            continue
        rec['proposal_sha256'] = hashlib.sha256(code.encode()).hexdigest()
        # guard: run in isolated dir, frozen files untouched
        try:
            rc, out, err, saved = run_iteration_source(code, iter_dir)
        except Exception as e:
            rec.update({'action': 'tombstone', 'reason': f'run failed: {e}'})
            receipts.append(rec); fails += 1
            (HERE / 'loop-receipts.jsonl').write_text('\n'.join(json.dumps(r) for r in receipts) + '\n')
            continue
        after = frozen_hashes()
        if after != hashes_before:
            rec.update({'action': 'tombstone', 'reason': 'frozen file changed', 'frozen_diff': {k: [hashes_before[k], after[k]] for k in FROZEN if hashes_before[k] != after[k]}})
            receipts.append(rec); fails += 1
            print(f"[iter {it}] TOMBSTONE frozen file changed", flush=True)
            continue
        rec['saved'] = saved
        rec['rc'] = rc
        rec['stderr_tail'] = (err or '')[-400:]
        if rc != 0 and err:
            state['last_error'] = err[-600:]
        improved = False
        if rc == 0 and saved:
            for case in CASES:
                token = case.replace('-', '_')
                cands = sorted(iter_dir.glob(f'*{token}*.json'), key=lambda q: q.stat().st_mtime)
                if not cands:
                    continue
                cand = cands[-1]
                proxy = None
                for name, val in saved:
                    if name == cand.name:
                        proxy = float(val)
                if proxy is None:
                    try:
                        proxy = float(json.loads(cand.read_text()).get('proxy_ratio'))
                    except Exception:
                        proxy = None
                c = court_T160(case, cand)
                if c:
                    court_used += c['court_min']
                incumbent = state[case]['court']
                better_proxy = proxy is not None and (state[case]['proxy'] is None or proxy < state[case]['proxy'])
                better_court = c is not None and (incumbent is None or c['inf_ratio_T160'] < incumbent['inf_ratio_T160'])
                rec.setdefault('cases', {})[case] = {'proxy': proxy, 'court_T160': c,
                                                     'better_proxy': better_proxy, 'better_court': better_court}
                if better_court and better_proxy:
                    improved = True
                    state[case] = {'proxy': proxy, 'court': c}
        if improved:
            rec['action'] = 'keep'
            current_src = code
            fails = 0
        else:
            rec['action'] = 'tombstone' if rc != 0 or not saved else 'reject-no-improvement'
            fails += 1
        receipts.append(rec)
        (HERE / 'loop-receipts.jsonl').write_text('\n'.join(json.dumps(r) for r in receipts) + '\n')
        print(f"[iter {it}] model={model} action={rec['action']} court_min_total={court_used:.1f} fails={fails}", flush=True)
    print(f"[loop] done; court minutes used ~{court_used:.1f}", flush=True)

if __name__ == '__main__':
    main()
