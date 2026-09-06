"""Finite, controlled prime-gears experiment; no zeta data or network access."""
from pathlib import Path
from itertools import product
from math import gcd, lcm, isqrt, sqrt
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
PHI = (1 + sqrt(5)) / 2

def prime(n):
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))

def mask(periods, n):
    return np.all(np.array([n % d != 0 for d in periods]), axis=0)

def wheel(periods):
    period = lcm(*periods)
    a = mask(periods, np.arange(period))
    minimal = next(d for d in range(1, period + 1)
                   if period % d == 0 and np.array_equal(a, np.roll(a, d)))
    power = abs(np.fft.rfft(a.astype(float) - a.mean())) ** 2 / period ** 2
    top = sorted(range(1, len(power)), key=lambda k: (-power[k], k))[:5]
    return {'periods': periods, 'configuration_period': period,
            'mask_minimal_period': minimal, 'survivors_per_period': int(a.sum()),
            'density': float(a.mean()),
            'fft_top': [{'cycles_per_tick': k / period, 'power': float(power[k])} for k in top]}

def exponents(n):
    result = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            result[d] = result.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        result[n] = result.get(n, 0) + 1
    return result

def reconstruct(v):
    result = 1
    for p, a in v.items():
        result *= p ** a
    return result

def spaces(base, digits):
    half = base // 2
    states = list(product(range(-half, half + 1), repeat=digits))
    labels = [sum(x * base ** (digits - j - 1) for j, x in enumerate(s)) for s in states]
    size = base ** digits
    cyclic_orders = [size // gcd(x, size) for x in range(size)]
    coordinate_orders = [lcm(*(base // gcd(x, base) for x in s)) for s in states]
    return {'base': base, 'digits': digits, 'states': size,
            'label_range': [min(labels), max(labels)],
            'bijection': len(set(labels)) == size,
            'max_cyclic_order': max(cyclic_orders),
            'max_coordinatewise_order': max(coordinate_orders)}

def main():
    # All designated controls evaluated before authentic-prime results.
    composite = wheel([4, 9, 25])
    redundant = wheel([2, 3, 5, 4])
    base_controls = [spaces(3, 2), spaces(5, 2)]
    u = np.linspace(0, 30, 301)
    periods = np.array([2., 3., 5.])
    ref = np.exp(2j * np.pi * u[:, None] / periods)
    scales = {}
    for name, c in [('one', 1), ('sqrt2', sqrt(2)), ('two', 2), ('phi', PHI)]:
        scaled = np.exp(2j * np.pi * (c * u[:, None]) / (c * periods))
        scales[name] = float(abs(scaled - ref).max())
    relative = {name: float(abs(np.exp(2j * np.pi * 30 / (5 * c)) - 1))
                for name, c in [('sqrt2', sqrt(2)), ('phi', PHI)]}
    signed_errors = sum((1 if n > 0 else -1) * reconstruct(exponents(abs(n))) != n
                        for n in range(-1000, 1001) if n)
    prime_sets = [[2, 3], [2, 3, 5], [2, 3, 5, 7], [2, 3, 5, 7, 11]]
    rows = []
    for ps in prime_sets:
        row = wheel(ps)
        survivors = [n for n in range(2, 10001) if all(n % p for p in ps)]
        false = [n for n in survivors if not prime(n)]
        nextp = next(n for n in range(ps[-1] + 1, 100) if prime(n))
        after = next(n for n in range(nextp + 1, 100) if prime(n))
        mutated_false = next(n for n in range(2, 10001)
                             if all(n % p for p in ps + [nextp]) and not prime(n))
        row.update(survivors_2_to_10000=len(survivors), false_positives=len(false),
                   first_false_positive=false[0], predicted_first_false_positive=nextp ** 2,
                   mutation_first_false_positive=mutated_false,
                   mutation_predicted_first_false_positive=after ** 2,
                   prime_survivors=len(survivors) - len(false))
        rows.append(row)
    coords = [exponents(n) for n in range(1, 1001)]
    omega = [sum(v.values()) for v in coords]
    data = {'status': 'MEASURED finite toy, not RH evidence',
            'execution_order': 'controls before prime wheels',
            'controls': {'composite': composite, 'redundant': redundant, 'base': base_controls},
            'prime_wheels': rows,
            'coordinates': {'range': [1, 1000],
                            'reconstruction_errors': sum(reconstruct(v) != n for n, v in enumerate(coords, 1)),
                            'distinct_vectors': len({tuple(v.items()) for v in coords}),
                            'distinct_collapsed_labels': len(set(omega)),
                            'signed_reconstruction_errors': signed_errors,
                            'sign_erasure_collision_pairs': 1000},
            'ternary': spaces(3, 3),
            'global_scale_max_phase_error': scales,
            'relative_scale_return_distance_at_t30': relative}
    checks = {
        'prime_mask_periods': [r['mask_minimal_period'] for r in rows] == [6, 30, 210, 2310],
        'composite_period': composite['mask_minimal_period'] == 900,
        'composite_nonzero_fourier_peaks': composite['fft_top'][0]['power'] > 0,
        'redundant_mask': np.array_equal(mask([2, 3, 5], np.arange(120)), mask([2, 3, 5, 4], np.arange(120))),
        'first_surviving_composites': all(r['first_false_positive'] == r['predicted_first_false_positive'] for r in rows),
        'next_prime_mutations': all(not mask(ps + [next(n for n in range(ps[-1]+1,100) if prime(n))], np.array([r['first_false_positive']]))[0] for ps,r in zip(prime_sets, rows)),
        'next_square_survives_mutation': all(r['mutation_first_false_positive'] == r['mutation_predicted_first_false_positive'] for r in rows),
        'coordinate_reconstruction': data['coordinates']['reconstruction_errors'] == 0 and signed_errors == 0,
        'axis_collapse_loses_information': len(set(omega)) < 1000,
        'ternary_and_controls': all(s['bijection'] and s['max_cyclic_order'] == s['states'] and s['max_coordinatewise_order'] == s['base'] for s in base_controls + [data['ternary']]),
        'global_scale_invariance': max(scales.values()) < 1e-12,
        'relative_irrational_scaling_breaks_old_return': min(relative.values()) > 1e-6,
    }
    data['prediction_ledger'] = {k: 'HELD' if bool(v) else 'FAILED' for k, v in checks.items()}
    (ROOT / 'results.json').write_text(json.dumps(data, indent=2) + '\n')
    assert all(checks.values()), data['prediction_ledger']

    fig, axes = plt.subplots(2, 1, figsize=(11, 7), constrained_layout=True)
    x = np.arange(2, 101)
    for j, ps in enumerate(prime_sets[:3]):
        yes = mask(ps, x)
        axes[0].scatter(x[yes], np.full(yes.sum(), j), color='#2476a8', s=24,
                        label='Prime survivor' if j == 0 else None)
        bad = yes & np.array([not prime(int(n)) for n in x])
        axes[0].scatter(x[bad], np.full(bad.sum(), j), color='#bd4d30', marker='x', s=55,
                       label='Composite survivor' if j == 0 else None)
    axes[0].set(yticks=[0, 1, 2], yticklabels=['2 and 3 gears', '+ 5 gear', '+ 7 gear'],
                xlabel='Integer n (base primes excluded)', ylabel='Divisibility filter',
                title='New gears remove false positives; they do not create new primes', xlim=(0, 102), ylim=(-.5, 2.85))
    axes[0].legend(loc='upper right')
    colors = ['#2476a8', '#bd4d30']
    for ps, label, color in [([2, 3, 5], 'Prime periods: 2, 3, 5', colors[0]),
                              ([4, 9, 25], 'Composite control: 4, 9, 25', colors[1])]:
        L = lcm(*ps)
        a = mask(ps, np.arange(L)).astype(float)
        power = abs(np.fft.rfft(a-a.mean()))**2/L**2
        freq = np.fft.rfftfreq(L)
        axes[1].vlines(freq[1:], 0, power[1:], color=color, alpha=.8, label=label)
    axes[1].set(xlabel='Frequency (cycles per integer tick)', ylabel='Normalized Fourier power',
                title='Fourier peaks occur in both prime and composite clocks', xlim=(0, .51))
    axes[1].legend(loc='upper center')
    fig.savefig(ROOT / 'prime-gears.png', dpi=150)
    print(json.dumps(data, indent=2))

if __name__ == '__main__':
    main()
