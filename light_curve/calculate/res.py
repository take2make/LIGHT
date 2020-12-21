import os
import numpy as np
import matplotlib.pyplot as plt
from .tt_read import MagReader
from .lbol_read import LbolReader
from .parameters import Msun, c
import matplotlib

#matplotlib.rcParams.update({'font.size': 12, 'figure.figsize':(10,9), 
    #'lines.linewidth': 1.5, 'figure.dpi': 300, 'lines.markersize' : 5})


class ResReader(object):
    def __init__(self, fname):
        self.fname = fname
        self.process_res_file()

    def process_res_file(self):
        """
        Считываем данные из файла. Получаем имена стандартизированных
        кривых блеска, а также параметры стандартизации x1 и color
        """
        print(f"Reading res file for run {self.fname}")
        raw_data = np.loadtxt(self.fname, skiprows=1, usecols=(7, 9), dtype=float, delimiter=',')
        name_data = np.loadtxt(self.fname, skiprows=1, usecols=1, dtype=str, delimiter=',')
        print(f"{self.fname} found and read")

        self.mname = {name_data[i]: i for i in range(len(name_data))}
        self.x1 = raw_data[:, 0]
        self.color = raw_data[:, 1]
        self.set_cosmology_parameters()

    def set_cosmology_parameters(self):
        """
        Задаем космологическую модель для стандартизации
        """
        self.MB = -19.48
        self.alpha = 0.154
        self.beta = 3.02

    def correlation_fun(self, x, y):
        """
        Функция стандартизации, зависящая от космологических
        параметров
        """
        return self.MB - self.alpha * x + self.beta * y

    def error_surfaces(self, ax):
        """
        Строим поверхности, задающие погрешность для
        уравнения стандартизации
        """
        x = np.arange(-2, 3.3, 0.1)
        y = np.arange(0, 1.1, 0.01)
        X, Y = np.meshgrid(x, y)
        Z_er_1 = self.correlation_fun(X, Y) + 0.33
        Z_er_2 = self.correlation_fun(X, Y) - 0.33
        ax.plot_surface(X, Y, Z_er_1, color='gray', alpha=0.5)
        ax.plot_surface(X, Y, Z_er_2, color='gray', alpha=0.5)

    def find_stand_data(self, mag):
        _x1 = self.x1
        _c = self.color
        Z1 = self.correlation_fun(_x1, _c) - 0.5
        Z2 = self.correlation_fun(_x1, _c) + 0.5

        y = np.sqrt(_x1 ** 2 + _c ** 2 + mag ** 2) >= np.sqrt(_x1 ** 2 + _c ** 2 + Z2 ** 2)
        y2 = np.sqrt(_x1 ** 2 + _c ** 2 + mag ** 2) * y <= np.sqrt(_x1 ** 2 + _c ** 2 + Z1 ** 2)

        model = {}
        for (num_mod, i) in zip(self.mname.keys(), self.mname.values()):
            if y2[i]:
                model[num_mod] = i
        return model

    def plot_surface(self, mag, fig=None):
        """
        Строим поверхность стандартизации
        """
        if fig == None:
            fig = plt.figure()
        fig.set_size_inches(6, 5, forward=True)
        ax = fig.add_subplot(111, projection='3d')

        self.error_surfaces(ax)
        _x1 = self.x1
        _c = self.color
        Z1 = self.correlation_fun(_x1, _c) - 0.5
        Z2 = self.correlation_fun(_x1, _c) + 0.5

        y = np.sqrt(_x1 ** 2 + _c ** 2 + mag ** 2) >= np.sqrt(_x1 ** 2 + _c ** 2 + Z2 ** 2)
        y2 = np.sqrt(_x1 ** 2 + _c ** 2 + mag ** 2) * y <= np.sqrt(_x1 ** 2 + _c ** 2 + Z1 ** 2)

        ax.set_xlabel(r' $x_1$ ', fontsize=18)
        ax.set_ylabel(r' c ', fontsize=18)
        ax.set_zlabel(r' $M_B^*$ ', fontsize=18)
        ax.view_init(10, -25)

        model = {}
        for (num_mod, i) in zip(self.mname.keys(), self.mname.values()):
            if y2[i]:
                ax.scatter(self.x1[i], self.color[i], mag[i], linewidth=1, marker='o', alpha=1, c='black');
                model[num_mod] = i
            else:
                ax.scatter(self.x1[i], self.color[i], mag[i], linewidth=1, marker='^', alpha=1, c='black');
        ax.xaxis.set_rotate_label(False)
        ax.yaxis.set_rotate_label(False)


def read_lbol_reader(models):
    """
    Считываем из models кривые блеска
    :return: lbol
    """
    lbol_read = {}
    for num_mod, i in zip(models.keys(), models.values()):
        lbol_read[num_mod] = [LbolReader(num_mod), i]
    return lbol_read


def read_mag_reader(models):
    """
    Считываем из models максимум кривой блеска в полосе B
    :return: minMB
    """
    mag_read = {}
    for num_mod, i in zip(models.keys(), models.values()):
        mag_read[num_mod] = [MagReader(num_mod), i]
    return mag_read


def find_appropriate_models(read, data):
    """
    Считываем подходящие модели сверхновых на основе
    уравнения стандартизации
    :return: models
    """
    mag_read = read_mag_reader(data)
    minMB = np.array([mag_read[name][0].minB for name in mag_read.keys()])
    return read.find_stand_data(minMB)


def plot_correlation(read, models, path_to_save='graphics'):
    """
    Построение поверхности стандартизации
    """
    #try:
    print(models)
    mag_read = read_mag_reader(models)
    minMB = np.array([mag_read[name][0].minB for name in mag_read.keys()])
    read.plot_surface(minMB)

    if os.path.isdir(path_to_save):  
        path = os.path.join(path_to_save,"correlation.jpeg")
        plt.savefig(path, format='jpeg', dpi=300)
        plt.show()
    else:
        os.mkdir(path_to_save)
        path = os.path.join(path_to_save,"correlation.jpeg")
        plt.savefig(path, format='jpeg', dpi=300)
        plt.show()


def reading_results(path="standart_data", data='results_SALT.txt'):
    """
    Считывание данных из results.txt. Хранятся данные
    для сверхновых откалиброванных по модели SALT.
    """
    if os.path.isdir(path):
        try:
            file = os.path.join(path, data)
            read = ResReader(file)
            return read
        except OSError:
            print('There is no results for SALT')
    else:
        print("You have no standart_data directory")


def show_lbol(lbol_read, num, path_to_save="graphics", fig=None):
    """
    Построение кривых блеска для различных моделей
    """
    if fig is None:
        fig = plt.figure()
    #fig.set_size_inches(6, 5, forward=True)

    keys = list(lbol_read.keys())
    for name in keys[:num]:
        lbol_read[name][0].show_lbol_lightcurve(fig)

    if os.path.isdir(path_to_save):  
        plt.grid()
        plt.minorticks_on()
        plt.grid(which='minor', color='black', linestyle=':')
        plt.grid(which='major', color='black', linestyle=':')
        path = os.path.join(path_to_save,"lbol.eps")
        plt.savefig(path, format='eps', dpi=300)
        plt.show()
    else:
        os.mkdir(path_to_save)
        plt.grid()
        plt.minorticks_on()
        plt.grid(which='minor', color='black', linestyle=':')
        plt.grid(which='major', color='black', linestyle=':')
        path = os.path.join(path_to_save,"lbol.eps")
        plt.savefig(path, format='eps', dpi=300)
        plt.show()


def plot_ta(lbol_read, fig=None, path_to_save="graphics"):
    """
    Построение зависимости отношения tb/td
    """
    if fig is None:
        fig = plt.figure()
    #fig.set_size_inches(6, 5, forward=True)
    ax = fig.gca()
    name = list(lbol_read.keys())

    for i, mname in enumerate(name):
        ta, tb, *args = lbol_read[mname][0].find_ta_tb()
        ax.scatter(i, ta, label=mname, color='grey')
        
    ax.set_xlabel(r"model", fontsize=12)
    ax.set_ylabel(r"$t_A$", fontsize=12)

    ax.set_ylim([5,30])

    ax.minorticks_on()
    ax.grid(which='minor', color='black', linestyle=':')
    ax.grid(which='major', color='black', linestyle=':')

    if os.path.isdir(path_to_save):
        path = os.path.join(path_to_save,"ta.eps")
        plt.savefig(path, format='eps', dpi=300)
    else:
        os.mkdir(path_to_save)
        path = os.path.join(path_to_save,"ta.eps")
        plt.savefig(path, format='eps', dpi=300)
    return ta


def plot_tb(lbol_read, fig=None, path_to_save="graphics"):
    """
    Построение зависимости отношения tb/td
    """
    if fig is None:
        fig = plt.figure()
    #fig.set_size_inches(6, 5, forward=True)
    ax = fig.gca()
    name = list(lbol_read.keys())
    for i, mname in enumerate(name):
        ta, tb, *args = lbol_read[mname][0].find_ta_tb()
        ax.scatter(i, tb, label=mname, color='grey')

    ax.set_xlabel(r"model", fontsize=12)
    ax.set_ylabel(r"$t_B$", fontsize=12)

    ax.set_ylim([3,65])

    ax.minorticks_on()
    ax.grid(which='minor', color='black', linestyle=':')
    ax.grid(which='major', color='black', linestyle=':')

    if os.path.isdir(path_to_save):
        path = os.path.join(path_to_save,"tb.eps")
        plt.savefig(path, format='eps', dpi=300)
    else:
        os.mkdir(path_to_save)
        path = os.path.join(path_to_save,"tb.eps")
        plt.savefig(path, format='eps', dpi=300)
    return tb


def show_pf_relation(mag_read, fig=None, m15 = np.arange(0.7, 1.85, 0.1), path_to_save="graphics"):
    """
    Построение соотношения Псковского-Филипсса
    """
    if fig is None:
        fig = plt.figure()
    #fig.set_size_inches(6, 5, forward=True)

    ax = fig.gca()

    [mag_read[name][0].show_mbol_lightcurve(mag_read[name][1], fig) for name in mag_read.keys()]
    a = -20.883
    b = 1.949
    mV = a + b * m15
    err = np.sqrt(0.417)
    ax.fill_between(m15, mV - err, mV + err, alpha=0.2, color='black')

    if os.path.isdir(path_to_save):
        path = os.path.join(path_to_save,"PF.jpeg")
        plt.savefig(path, format='jpeg', dpi=300)
    else:
        os.mkdir(path_to_save)
        path = os.path.join(path_to_save,"PF.jpeg")
        plt.savefig(path, format='jpeg', dpi=300)
