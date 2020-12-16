from res import *
import argparse
import os


def parsing():
    parser = argparse.ArgumentParser(description='\
        program for determination characteristic times of SN\
        -----------------------------------------------------------------------------\
        just use it')

    parser.add_argument("--read", default=None, type=str, help="input path to salt data")
    parser.add_argument("--mod", default="all", type=str, help="get models")
    parser.add_argument("--stand", default="NoPlot", type=str, help="find appropriate models only for salt data")
    parser.add_argument("--mag", action="store_true", help="reading .tt files")
    parser.add_argument("--lbol", action="store_true", help="reading .lbol files")
    parser.add_argument("--pf", action="store_true", help="plot pf relation")
    parser.add_argument("--showL", default=0, type=int, help="plot light curve")
    parser.add_argument("--ta", action="store_true", help='plot data for ta ')
    parser.add_argument("--tb", action="store_true", help='plot data for tb ')


    args = parser.parse_args()
    reading = False

    if args.read:
        dirname, filename = os.path.split(args.read)
        read = reading_results(dirname, filename)
        reading = True

    if args.mod == 'all':
        models = {}
        path = os.path.join('data', 'raw_data')
        files = os.listdir(path)
        for i in range(len(files)):
            mod = files[i]
            if mod[-2:] == 'tt':
                models[mod[:-3]] = i
        reading = False
        print(models.keys())

    if args.mod == 'salt':
        try:
            models = read.mname
            print(models.keys())
        except:
            print('firstly read salt data')

    if args.stand=='Plot':
        if args.mod == 'salt' and reading:
            plot_correlation(read, models)
            models = find_appropriate_models(read, models)
            print(models)
        else:
            print('plot only for salt data')
    elif args.stand=='NoPlot':
        if reading:
            models = find_appropriate_models(read, models)
            print(models)
        else:
            print('you have no appropriate models')

    if args.mag:
        mag_read = read_mag_reader(models)

    if args.lbol:
        lbol_read = read_lbol_reader(models)

    if args.pf:
        mag_read = read_mag_reader(models)
        show_pf_relation(mag_read)
        plt.show()

    if args.showL:
        lbol_read = read_lbol_reader(models)
        show_lbol(lbol_read, args.showL)

    if args.ta:
        try:
            lbol_read = read_lbol_reader(models)
            plot_ta(lbol_read)
            plt.show()
        except:
            print('firstly read salt data')

    if args.tb:
        try:
            lbol_read = read_lbol_reader(models)
            plot_tb(lbol_read)
            plt.show()
        except:
            print('firstly read salt data')




if __name__ == "__main__":
    parsing()


