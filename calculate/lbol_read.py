import numpy as np
import matplotlib.pyplot as plt
from parameters import Msun, T_Ni, T_Co, C_Co, C_Ni
import os


class LbolReader(object):
    def __init__(self, mname, data_dir = 'raw_data'):
        self.mname = mname
        path = os.path.join('data', data_dir)
        if os.path.isdir(path):
            try:
                self.fname = os.path.join(path, mname+".lbol")
                self.process_lbol_file()
            except:
                print(f'There is no data for {mname}.lbol')
        else:
            print("You have no data directory")

    def process_lbol_file(self):
        """
        Считываение lbol файл с кривой блеска
        """
        print(f"Reading lbol file for run {self.mname}")
        raw_data = np.loadtxt(self.fname, skiprows=1, dtype=float)
        print(f"{self.fname} found and read\n")
        self.tl = raw_data[:, 0]
        self.lbol = raw_data[:, 2]

    def find_ta_tb(self, eps=1e-5):
        """
        Находим времена ta и tb, когда кривая блеска
        пересекается с кривой блеска депозиции
        :param eps:
        :return: ta, tb, lbol_ta, lbol_tb
        """
        Mni = int(self.mname[2]) * 0.1
        lbol_ni_bol = np.log10(Mni * (C_Ni * np.exp(-self.tl / T_Ni) + C_Co * np.exp(-self.tl / T_Co)))
        lbol_lni = lbol_ni_bol - self.lbol

        try:
            ta = self.tl[lbol_lni < eps][0]
            tb = self.tl[lbol_lni < eps][-1]
            lbol_ta = self.lbol[lbol_lni < eps][0]
            lbol_tb = self.lbol[lbol_lni < eps][-1]
        except:
            print('cannot find times')
            ta = 0
            tb = 0
            lbol_ta = 0
            lbol_tb = 0

        return ta, tb, lbol_ta, lbol_tb

    def show_lbol_lightcurve(self, fig=None):
        """
        Построение кривых блеска
        """
        if fig is None:
            fig = plt.figure(figsize=(10, 9), dpi=300)
        fig.set_size_inches(6, 5, forward=True)

        ax = fig.gca()
        Mni = int(self.mname[2]) * 0.1
        print(f'light curve for {self.mname} and Mni = {Mni} of solar masses')
        lbol_ni_bol = np.log10(Mni * (C_Ni * np.exp(-self.tl /T_Ni) + C_Co * np.exp(-self.tl / T_Co)))

        ta, tb, lbol_ta, lbol_tb = self.find_ta_tb()
        ax.set_xlabel(f't, дни')
        ax.set_ylabel(r'$\log{L}$, $\log$ Эрг/c')
        ax.plot(self.tl, lbol_ni_bol, color='black', linestyle='--', label=r'Логарифм светимости $\log{L_{\gamma}}$')
        ax.plot(self.tl, self.lbol, color='black', label='Логарифм светимости сверхновой')
        ax.scatter(ta, lbol_ta, color='black')
        ax.text(ta-1, lbol_ta-0.3, r'$t_A$', fontsize=18)
        ax.scatter(tb, lbol_tb, color='black')
        ax.text(tb-2, lbol_tb-0.3, r'$t_B$', fontsize=18)
        ax.set_xlim([0, 60])
        ax.set_ylim([40, 43])

        return fig
