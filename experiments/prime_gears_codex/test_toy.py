"""Independent elementary identities checking the implementation."""
import unittest
from fractions import Fraction
from math import prod
import numpy as np
from run import mask, wheel, exponents, reconstruct, spaces

class Checks(unittest.TestCase):
    def test_sieve_against_gcd(self):
        from math import gcd
        for ps in ([2,3], [2,3,5], [2,3,5,7]):
            M = prod(ps)
            self.assertEqual(mask(ps, np.arange(M)).tolist(), [gcd(n,M)==1 for n in range(M)])
            self.assertEqual(sum(mask(ps,np.arange(M))), prod(p-1 for p in ps))

    def test_composite_density_and_fft(self):
        ps = [4,9,25]
        row = wheel(ps)
        self.assertEqual(Fraction(row['survivors_per_period'],900), prod(Fraction(p-1,p) for p in ps))
        n = np.arange(900)
        a = mask(ps,n).astype(float)
        direct = abs(sum((a-a.mean()) * np.exp(-2j*np.pi*n/4))/900)**2
        self.assertAlmostEqual(direct, row['fft_top'][0]['power'], places=12)

    def test_multiplication_is_coordinate_addition(self):
        for a in range(1,40):
            for b in range(1,40):
                v = exponents(a)
                for p,e in exponents(b).items():
                    v[p] = v.get(p,0)+e
                self.assertEqual(reconstruct(v), a*b)
                self.assertEqual(v, exponents(a*b))

    def test_collapse_and_ternary_carry(self):
        self.assertEqual(sum(exponents(4).values()), sum(exponents(6).values()))
        self.assertNotEqual(exponents(4),exponents(6))
        self.assertEqual(spaces(3,3)['label_range'],[-13,13])
        self.assertEqual((13+1+13)%27-13,-13)
        # Cyclic repeated addition of 1 visits all 27 states.
        self.assertEqual(len({n%27 for n in range(27)}),27)
        # Coordinatewise repeated addition of (1,1,1) visits only 3.
        self.assertEqual(len({(n%3,n%3,n%3) for n in range(27)}),3)

if __name__ == '__main__':
    unittest.main()
