import unittest
import json
from pathlib import Path
from flint import arb, ctx
from certify import corr, ldl


class CertificateChecks(unittest.TestCase):
    def setUp(self):
        ctx.prec=384

    def test_orthonormality(self):
        for i in range(1,17):
            for j in range(1,17):
                self.assertTrue(corr(i,j,arb(0),arb('7/10')).contains(int(i==j)))

    def test_ldl_controls(self):
        self.assertTrue(ldl([[arb(2),arb(1)],[arb(1),arb(2)]])['positive'])
        self.assertTrue(ldl([[arb(1),arb(2)],[arb(2),arb(1)]])['negative_direction'])
        self.assertEqual(ldl([[arb(1),arb(1)],[arb(1),arb(1)]])['status'],'UNVERIFIED')

    def test_saved_entry_balls(self):
        data=json.loads(Path(__file__).with_name('certified_results.json').read_text())
        for row in data['rows']:
            w=[[arb(v) for v in r] for r in row['entries']]
            if row['model']=='authentic':
                self.assertTrue(ldl(w,'1e-12')['positive'])
            else:
                self.assertTrue(ldl(w)['negative_direction'])


if __name__=='__main__':
    unittest.main()
