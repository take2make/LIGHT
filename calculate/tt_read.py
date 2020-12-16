import numpy as np
import matplotlib.pyplot as plt
import os


class MagReader(object):
    def __init__(self, mname, data_dir = 'raw_data'):
        self.mname = mname
        path = os.path.join('data', data_dir)
        print(path)
        if os.path.isdir(path):
            try:
                self.fname = os.path.join(path, mname+".tt")
                self.process_tt_file()
            except OSError:
                print(f'There is no data for {mname}.tt')
        else:
            print("You have no data directory")

    def process_tt_file(self):
        """
        Считываем .tt файл для получения звездных величин
        в различных фильтрах
        """
        print(f"Reading tt file for run {self.mname}")
        raw_data = np.loadtxt(self.fname, skiprows=87, dtype=float)
        print(f"{self.fname} found and read\n")

        self.raw_data = raw_data

        self.tl = raw_data[:, 0]
        self.MV = raw_data[:, 9]
        self.MB = raw_data[:, 8]
        self.minV = min(self.MV)
        self.minB = min(self.MB)

        stpmin = np.argmin(self.MV)
        i15 = stpmin
        while self.tl[i15] <= self.tl[stpmin] + 15:
            i15 += 1

        self.dm15 = abs(self.minV - self.MV[i15])

    def show_mbol_lightcurve(self, num, fig=None, m15=np.arange(0.7, 1.85, 0.1)):
        """
        Рисуем кривую блеска для звездных величин
        """
        if fig is None:
            fig = plt.figure()

        ax = fig.gca()

        ax.scatter(self.dm15, self.minV, color='dimgray', marker=f'.')

        ax.minorticks_on()
        ax.grid(which='minor', color='black', linestyle=':')
        ax.grid(which='major', color='black', linestyle=':')
        print(f"for {num} model is {self.mname}")
        ax.set_xlim([min(m15), max(m15)])
        ax.set_ylim([-15, -22])

        ax.set_xlabel(r"$\Delta m_{15}$")
        ax.set_ylabel(r"$M_V$")

        return fig
