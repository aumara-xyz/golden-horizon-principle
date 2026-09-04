"""Independent adaptive integration checks for analytic building blocks."""
import unittest
import mpmath as m
from high_precision import correlation, pole


class AnalyticChecks(unittest.TestCase):
    def test_correlations_and_poles(self):
        with m.workdps(60):
            L, u = m.mpf('.7'), m.mpf('.31')
            def f(x,k):
                return m.sin(k*m.pi*(x+L)/(2*L))/m.sqrt(L)
            for i,j in [(1,1),(1,3),(2,4),(3,4),(16,16)]:
                numeric = m.quad(lambda x:(f(x+u,i)*f(x,j)+f(x+u,j)*f(x,i))/2,[-L,L-u])
                self.assertLess(abs(numeric-correlation(i,j,u,L)),m.mpf('1e-55'))
            for i in [1,2,15,16]:
                numeric = m.quad(lambda x:f(x,i)*m.exp(x/2),[-L,L])
                self.assertLess(abs(numeric-pole(i,m.mpf('.5'),L)),m.mpf('1e-55'))
            for i in range(1,17):
                for j in range(1,17):
                    self.assertLess(abs(correlation(i,j,0,L)-int(i==j)),m.mpf('1e-55'))


if __name__ == '__main__':
    unittest.main()
