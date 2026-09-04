import json
import unittest
from pathlib import Path
from flint import arb, ctx
from certify import ldl
from parity_tail import sector


class ParityTailChecks(unittest.TestCase):
    def setUp(self):
        ctx.prec=512
        self.root=Path(__file__).parent

    def test_saved_sector_certificates(self):
        data=json.loads((self.root/'parity_tail_results.json').read_text())
        for row in data['rows']:
            w=[[arb(v) for v in r] for r in row['entries']]
            self.assertTrue(all(w[i][j].is_zero() for i in range(32) for j in range(32) if (i+j)%2))
            for N in (16,24,32):
                for p,label in [(0,'even'),(1,'odd')]:
                    expected=row['restrictions'][str(N)][label]
                    actual=ldl(sector(w,N,p))
                    self.assertEqual(actual['positive'],expected['positive'])
                    for power,result in expected.get('lower_bound_tests',{}).items():
                        actual=ldl(sector(w,N,p),'1e-'+power)
                        self.assertEqual(actual.get('positive'),result.get('positive'))

    def test_tail_balls(self):
        rows=json.loads((self.root/'pure_tail_results.json').read_text())
        for r in rows:
            self.assertTrue(arb(r['even_lower'])>arb('1/2'))
            self.assertTrue(arb(r['odd_lower'])>arb('3/10'))
            self.assertTrue(arb(r['eta'])<1)
        for model in ['arch_only','shift_plus','shift_minus','authentic']:
            small=next(r for r in rows if r['model']==model and r['N']==4096)
            large=next(r for r in rows if r['model']==model and r['N']==8192)
            self.assertTrue(arb(large['even_lower'])>arb(small['even_lower']))
            self.assertTrue(arb(large['odd_lower'])>arb(small['odd_lower']))


if __name__=='__main__':
    unittest.main()
