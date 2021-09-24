import os, sys
sys.argv.append('-b') # run in batch mode so plot windows arent created
import numpy as np
import pandas as pd
import strip_parser
import matplotlib.pyplot as plt
import glob

outDir = 'CV-plots'
inStr = '35720-CV/*'
to_drop = ['Time', 'Hum', 'Dew', 'freq2', '_G_', 'Temp']

avg_out = 'averages.txt'

def plotter(files):

    # Fill a dictionary with the measurement dataframes and other useful info
    # Sensor name is used as the key for each set of measurements
    data = {}
    meas_all = []
    for i, file in enumerate(files):
        sensor, _, _, temp_df = strip_parser.parseFile(file, to_drop)
        data[sensor] = {}
        data[sensor]['num'] = i # Use to keep colors consistent when plotting
        data[sensor]['data'] = temp_df.copy(deep=True)
        data[sensor]['measurements'] = list(data[sensor]['data'].columns)
        meas_all += data[sensor]['measurements']
        del temp_df
    
    print('\n','Found measurements for the following sensors:\n', data.keys(), '\n')
    # Find all measurements taken, to know what to plot
    meas_all = list(set(meas_all))
    meas_all.remove('BiasVoltage')
    print('Will produce plots for the following measurements:\n', meas_all)

    if not os.path.isdir(outDir):
        os.mkdir(outDir)

    # Writing script in a way, where we dont need each sensor to have the exact same measurements for it to run
    for meas in meas_all:
        plt.figure(figsize=(10,6))
        to_plot = [sensor for sensor in data.keys() if meas in data[sensor]['measurements']]
        for sensor in to_plot:
            #plt.plot(data[sensor]['data']['Strip'], data[sensor]['data'][meas], color=plt.cm.RdYlBu(2*data[sensor]['num']), label=sensor)
            if 'LCR' in meas:
                plt.plot(np.abs(data[sensor]['data']['BiasVoltage']), data[sensor]['data'][meas]**-2, label=sensor)
            else:
                plt.plot(np.abs(data[sensor]['data']['BiasVoltage']), np.abs(data[sensor]['data'][meas]), label=sensor)

        plt.xlabel('Strip')
        plt.ylabel(getYUnit(meas))
        if 'freq1' in meas:
            plt.title('CV Measurement: 10kHz')
        else:
            plt.title(meas)
        plt.legend(loc='best')

        plt.savefig('%s/%s.png' % (outDir, meas))


    print('Now producing average measurement for each sensor')

    # Start with a dataframe for all the measurements and keys filled with 0
    avg = pd.DataFrame(np.zeros((len(data.keys()), len(meas_all)), dtype=np.float32), index=list(data.keys()), columns=meas_all)
    for sensor in data:
        for meas in data[sensor]['measurements']:
            avg.loc[sensor,meas] = np.mean(data[sensor]['data'][meas])

    print(avg)


def getYUnit(meas):
    if 'LCR' in meas:
        return 'Inverse Capacitance Squared ($pF^{-2}$)'
    elif 'Istrip' in meas or 'Current' in meas or 'Pin' in meas:
        return 'Current (A)'
    elif 'Resistance' in meas:
        return 'Resistance ($\Omega$)'
    elif 'Cap' in meas or ('Inter' in meas and 'C' in meas):
        return 'Capacitance (F)'
    else:
        return meas

def main():
    files = glob.glob(inStr)
    print('Found the following files:', files)
    plotter(files)
    return 0

if __name__ == '__main__':
    main()
