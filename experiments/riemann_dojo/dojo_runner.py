# AUKORA Riemann Dojo Runner
import json, urllib.request, time, re, sys
sys.path.insert(0, '/Users/peterviviani/golden-horizon-principle/experiments/riemann_dojo')
from dojo_court import evaluate_wave

VLLM_ENDPOINT = 'http://localhost:8010/v1/chat/completions'

SYSTEM_PROMPT = """You are the Adversarial Breaker in the AUKORA Riemann Dojo.
Your task is to search for a counterexample or near-zero wave f(x) for the Weil quadratic functional W(f).
Under Weil (1952), RH is equivalent to W(f) >= 0 for all admissible f. If any wave has W(f) < 0, RH is disproven.

Conventions:
- Support [-L, L], extended by zero.
- Basis: Legendre polynomials P_n(x/L) with odd parity: degrees [1, 3, 5, 7, 9, 11, 13, 15].
- Pole term for odd real f is -2*S^2 where S = integral f(x) sinh(x/2) dx (DESTRUCTIVE, pushes W negative).
- Primes visible at L=0.7 are {2, 3, 4}.

IMPORTANT:
Keep your internal reasoning concise (under 250 words). Focus directly on balancing the pole integral S vs prime overlap, conclude your reasoning, and immediately output the final JSON candidate.
"""

def query_auma(prompt, max_tokens=2048, temperature=0.6):
    payload = {
        'model': 'auma-gen-8',
        'messages': [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': max_tokens,
        'temperature': temperature
    }
    req = urllib.request.Request(
        VLLM_ENDPOINT,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            elapsed = time.time() - t0
            choice = data['choices'][0]['message']
            content = choice.get('content') or ''
            reasoning = choice.get('reasoning') or choice.get('reasoning_content') or ''
            return content, reasoning, elapsed
    except Exception as e:
        return None, str(e), time.time() - t0

def run_hunt_round(L_target='0.7', parity_target='odd', round_num=1, prev_data=None):
    print('=' * 75)
    print(f'RIEMANN DOJO: ADVERSARIAL HUNT ROUND {round_num} (L={L_target}, parity={parity_target})')
    print('=' * 75)
    
    if prev_data is None:
        context_prompt = f"""Adversarial Challenge Round {round_num}:
Target Room: L = {L_target}
Parity: {parity_target}
The known safety margin at L={L_target} is approximately 1e-10 (odd parity).
Propose an odd-parity wave using degrees [1, 3, 5, 7, 9, 11, 13, 15] designed to exploit the destructive pole term -2S^2.
Keep your thinking under 200 words, conclude your thought process quickly, and output ONLY valid JSON matching this schema:
{{
  "hypothesis": "Description of why this wave concentrates mass to maximize -2S^2 while canceling prime correlations",
  "degrees": [1, 3, 5, 7, 9, 11, 13, 15],
  "coefficients": ["1.0", "-0.45", "0.12", "0.05", "-0.02", "0.01", "-0.005", "0.002"]
}}
"""
    else:
        context_prompt = f"""Adversarial Challenge Round {round_num} (RECURSIVE FEEDBACK):
Target Room: L = {L_target}
Parity: {parity_target}

In Round {round_num - 1}, your proposed wave had:
- Coefficients: {prev_data['coefficients']}
- Hypothesis: {prev_data['hypothesis']}
- Certified Arb Court Receipt:
    Norm squared ||f||^2:  {prev_data['receipt']['norm2'][:25]}
    Pole term:             {prev_data['receipt']['pole'][:25]}
    Prime visible sum:     {prev_data['receipt']['prime_visible_sum'][:25]}
    W(f) lower bound:      {prev_data['receipt']['W_lower'][:25]}
    W(f) upper bound:      {prev_data['receipt']['W_upper'][:25]}

Result: The wave remained strictly POSITIVE (W(f) >= {prev_data['receipt']['W_lower'][:15]}).
Your objective in Round {round_num}:
Analyze why the Archimedean dispersion or prime terms counterbalanced your pole term.
Adjust the coefficients across degrees [1, 3, 5, 7, 9, 11, 13, 15] to depress W(f) further toward zero, or break the barrier W(f) < 0.

Keep your thinking under 200 words and output ONLY valid JSON matching this schema:
{{
  "hypothesis": "Explanation of adjustment based on Round {round_num-1} Arb court receipt",
  "degrees": [1, 3, 5, 7, 9, 11, 13, 15],
  "coefficients": ["...", "...", "...", "...", "...", "...", "...", "..."]
}}
"""

    print('Dispatching challenge to Auma Gen-8 on Nebius H200...')
    content, reasoning, elapsed = query_auma(context_prompt)
    if content is None:
        print(f'Error querying Auma: {reasoning}')
        return None
        
    print(f'Response received in {elapsed:.2f}s.')
    if reasoning:
        print(f'--- Internal Reasoning Summary ({len(reasoning)} chars) ---')
        print(reasoning[:500] + '...' if len(reasoning) > 500 else reasoning)
        print('---------------------------------------------------------')
        
    cand_data = None
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        try:
            cand_data = json.loads(content[start_idx:end_idx+1])
        except Exception as e:
            print(f'JSON parsing error from content: {e}')
            
    if not cand_data and reasoning:
        start_idx = reasoning.find('{')
        end_idx = reasoning.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            try:
                cand_data = json.loads(reasoning[start_idx:end_idx+1])
            except Exception:
                pass
                
    if not cand_data:
        print('Failed to extract valid candidate JSON.')
        print('Raw output content:', content[:300])
        return None
        
    hypothesis = cand_data.get('hypothesis', 'N/A')
    degrees = [int(d) for d in cand_data.get('degrees', [])]
    coeffs = [str(c) for c in cand_data.get('coefficients', [])]
    
    print(f'Strategy: {hypothesis}')
    print(f'Degrees ({len(degrees)}): {degrees}')
    print(f'Coefficients: {coeffs}')
    
    print('\nPassing candidate into Arb Interval Court...')
    court_receipt = evaluate_wave(L_target, parity_target, degrees, coeffs, T_cutoff=128)
    
    print('-' * 75)
    print('COURT RECEIPT:')
    print(f'  Norm squared ||f||^2:  {court_receipt["norm2"][:35]}...')
    print(f'  Pole term:             {court_receipt["pole"][:35]}...')
    print(f'  Prime visible sum:     {court_receipt["prime_visible_sum"][:35]}...')
    print(f'  W(f) lower bound:      {court_receipt["W_lower"][:35]}...')
    print(f'  W(f) upper bound:      {court_receipt["W_upper"][:35]}...')
    print(f'  Certified Positive:    {court_receipt["is_certified_positive"]}')
    print(f'  COUNTEREXAMPLE FOUND:  {court_receipt["is_counterexample_negative"]}')
    print('=' * 75)
    
    round_result = {
        'round': round_num,
        'L': L_target,
        'parity': parity_target,
        'hypothesis': hypothesis,
        'degrees': degrees,
        'coefficients': coeffs,
        'reasoning': reasoning,
        'receipt': court_receipt
    }
    return round_result

def run_recursive_dojo(total_rounds=3, L_target='0.7', parity_target='odd'):
    hunt_log = []
    prev_data = None
    for r in range(1, total_rounds + 1):
        res = run_hunt_round(L_target, parity_target, round_num=r, prev_data=prev_data)
        if res is None:
            print(f"Round {r} failed to return a valid candidate.")
            break
        hunt_log.append(res)
        prev_data = res
        if res['receipt']['is_counterexample_negative']:
            print("\n*** CRITICAL ALERT: POTENTIAL COUNTEREXAMPLE FOUND! ***\n")
            break
            
    log_path = '/Users/peterviviani/golden-horizon-principle/experiments/riemann_dojo/hunt_log.json'
    with open(log_path, 'w') as f:
        json.dump(hunt_log, f, indent=2)
    print(f"\nHunt log saved to: {log_path}")
    return hunt_log

if __name__ == '__main__':
    run_recursive_dojo(total_rounds=3)
