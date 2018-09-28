import sys

import csv
import os
import gc
import pickle
# case_solver class and case_reader class
import calcsolve

gc.enable()


class CaseScene():

    def __init__(self):
        path0=str(os.path.dirname(os.path.abspath(__file__)))
        path=path.replace('\\','/')+'/'

        file_names=[
            'main.csv',
            'mast_achor_conf.csv',
            'misc.csv',
            'dictionary.py',
            'crane/',
            '.csv',
            'mast/mast.csv',
            'wind section/wind_section.csv'
            ]
        tie_release=0
        calcsolve.case_reader(path,file_names[0],,file_names[1],file_names[2],file_names[3],file_names[4],file_names[5],file_names[6],file_names[7])
        # unpickle
        
