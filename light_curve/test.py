from calculate.res import *
import unittest
import os

class SaltTest(unittest.TestCase):
	def setUp(self):
		path = os.path.join('tests', 'salt_test.txt')
		self.data = ResReader(path)
		self.x1 = [-0.11239155464737571, 0.31821090814784814]
		self.c =  [0.18966532125179603, 0.27001552143799223]

		self.dataMag = np.loadtxt(path, skiprows=1, usecols=11, dtype=float, delimiter=',')
		self.M = [-18.28, -19.2]

	def test_init(self):
		 self.assertEqual((self.data.color[0], self.data.color[1]), (self.c[0], self.c[1]), "Неправильно считано")
		 self.assertEqual((self.data.x1[0], self.data.x1[1]), (self.x1[0], self.x1[1]), "Неправильно считано")
		 self.assertEqual((self.dataMag[0], self.dataMag[1]), (self.M[0], self.M[1]), "Неправильно считано")
		 print('correctly reading')

	def test_correlation(self):
		_x1 = self.data.x1
		_c = self.data.color
		mag = self.dataMag

		Z1 = self.data.correlation_fun(self.data.x1, self.data.color) - [0.5,0.5]
		Z2 = self.data.correlation_fun(self.data.x1, self.data.color) + [0.5,0.5]

		y = np.sqrt(_x1 ** 2 + _c ** 2 + mag ** 2) >= np.sqrt(_x1 ** 2 + _c ** 2 + Z2 ** 2)
		y2 = np.sqrt(_x1 ** 2 + _c ** 2 + mag ** 2) * y <= np.sqrt(_x1 ** 2 + _c ** 2 + Z1 ** 2)

		self.assertTrue(y2[0]==True, 'salt не сходится')
		self.assertTrue(y2[1]==True, 'salt не сходится')
		print('salt сходится')

if __name__ == '__main__':
    unittest.main()