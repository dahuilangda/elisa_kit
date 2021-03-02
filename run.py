import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from pynverse import inversefunc
from functools import partial

import sys
import os

if len(sys.argv[:]) != 2:
    print('Usage : python cAMP.py <input_file>')

def func(x,a,b,c,d):
    y=(a-d)/(1+(x/c)**b)+d
    return y

if not os.path.exists('output'):
    os.mkdir('output')



if __name__ == '__main__':
    input_file = sys.argv[1]
    df_data = pd.read_excel(input_file, sheet_name=0)
    df_data = df_data.fillna('')
    df_standard = pd.read_excel(input_file, sheet_name=1)
    x = list(df_standard['Value/nM'].values)
    x = [1e-2 if s < 1e-2 else s for s in x]
    y = list(df_standard['mean'].values)
    popt, pcov = curve_fit(func, x, y)
    yval=func(x,popt[0],popt[1],popt[2],popt[3])
    x = [np.log10(s) for s in x ]

    # Draw stardard plot
    plt.scatter(x,y)
    # plt.plot(x,yval,'g',label='A=%5.3f,B=%5.3f,C=%5.3f,D=%5.3f'%tuple(popt))
    plt.plot(x,yval,'g',label='IC50=%5.3f'%popt[2])
    plt.legend()
    plt.savefig('output'+input_file[:-4]+'svg')

    func_2 = partial(func, a=popt[0], b=popt[1], c=popt[2], d=popt[3])
    invcube = inversefunc(func_2)
    df_final = pd.DataFrame(columns=df_data.columns.values)
    df_final[df_data.columns.values[0]] = df_data[df_data.columns.values[0]]
    for col in df_data.columns.values[1:]:
        values = []
        for x in df_data[col]:
            try:
                values.append(invcube(x))
            except:
                values.append('')
        df_final[col] = values
    df_final.to_csv('output/'+input_file[:-5]+'_results.csv', index=False)


