import os, sys
#sys.argv.append('-b') # run in batch mode so plot windows arent created
import numpy as np
import pandas as pd
import strip_parser
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import argparse

parser = argparse.ArgumentParser(description = 'Produce plots and give averages of strip measurement data')
parser.add_argument('-i', '--input', type=str, default='strips', help='Name of input file. Can take single file, folder, or regular expressions.')
parser.add_argument('-o', '--output', type=str, default='plots', help='Name of directory where plots will be saved.')
parser.add_argument('-a', '--average', type=str, help='Specify excel filename to save averages to file. If no option given average values will not be saved.')
parser.add_argument('-d', '--drop', type=str, default='', help='Comma separated list of substrings. Measurements from datafile which contain the substrings will be dropped from plotting and averaging.')
args = parser.parse_args()


outDir = args.output
inStr = args.input

to_drop = ['Time', '_0', '_1', '_2', '_3', '_Mean', '_V']
if args.drop:
    to_drop += args.drop.split(',')
print('Will drop measurements which contain the following substrings:', to_drop)


def plotter(files):

    # Fill a dictionary with the measurement dataframes and other useful info
    # Sensor name is used as the key for each set of measurements
    data = {}
    meas_all = []
    for i, file in enumerate(files):
        sensor, _, _, temp_df = strip_parser.parseFile(file, to_drop, True)
        data[sensor] = {}
        data[sensor]['num'] = i # Use to keep colors consistent when plotting
        data[sensor]['data'] = temp_df.copy(deep=True)
        data[sensor]['measurements'] = list(data[sensor]['data'].columns)
        meas_all += data[sensor]['measurements']
        del temp_df
    
    print('\n','Found measurements for the following sensors:\n', data.keys(), '\n')
    # Find all measurements taken, to know what to plot
    meas_all = list(set(meas_all))
    meas_all.remove('Strip')
    print('Will produce plots for the following measurements:\n', meas_all)

    if not os.path.isdir(outDir):
        os.mkdir(outDir)

    # Writing script in a way, where we dont need each sensor to have the exact same measurements for it to run
    sensors = list(data.keys())
    sensors.sort(key = lambda x: x.split('_')[1])
    sensors.sort(key = lambda x: x.split('_')[-1])
    plt_style = '-,'
    for meas in meas_all:
        plt.figure(figsize=(10,6))
        to_plot = [sensor for sensor in sensors if meas in data[sensor]['measurements']]
        for sensor in to_plot:
            #plt.plot(data[sensor]['data']['Strip'], data[sensor]['data'][meas], color=plt.cm.RdYlBu(2*data[sensor]['num']), label=sensor)
            if 'MAINR' in sensor:
                plt_style = '-+'
            plt.plot(data[sensor]['data']['Strip'], np.abs(data[sensor]['data'][meas]), plt_style, label=sensor)
            plt_style = '-,'

        plt.xlabel('Strip')
        plt.ylabel(getYUnit(meas))
        plt.title(meas)
        plt.legend(loc='best')

        plt.savefig('%s/%s.png' % (outDir, meas))


    print('Now producing average measurement for each sensor')

    # Start with a dataframe for all the measurements and keys filled with 0
    avg = pd.DataFrame(np.zeros((len(data.keys()), len(meas_all)), dtype=np.float32), index=list(data.keys()), columns=meas_all)
    for sensor in sensors:
        for meas in data[sensor]['measurements']:
            avg.loc[sensor,meas] = np.mean(data[sensor]['data'][meas])

    print(avg)

    if args.average:
        avg_out = args.average.split('.')[0]
        avg_out += '.xlsx'
        avg.to_excel(avg_out)
    #outf = open(avg_out, 'w')
    #outf.write(avg.to_csv(), sep='\t')
    #outf.close()

def getYUnit(meas):
    if 'Istrip' in meas or 'Current' in meas or 'Pin' in meas:
        return 'Current (A)'
    elif 'Resistance' in meas:
        return 'Resistance ($\Omega$)'
    elif 'Cap' in meas or ('Inter' in meas and 'C' in meas):
        return 'Capacitance (F)'
    else:
        return meas

def main():
    global inStr
    if os.path.isdir(inStr):
        inStr += "/*"
    files = glob.glob(inStr)
    print('Found the following files:', files)
    if files == []:
        print("No files found for input '%s'. Please double check and try again." % inStr)
        sys.exit(1)
    plotter(files)
    return 0

if __name__ == '__main__':
    main()
