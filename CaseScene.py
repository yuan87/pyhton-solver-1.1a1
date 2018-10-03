import sys

import csv
import os
import gc
import pickle
# case_solver class and case_reader class
import calcsolve

gc.enable()


class CaseSceneIns():
    '''
    This class is function as create instances of case_reader and case_solver, ie: create creating different case
    Define working condition and cases here
    '''

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

        caseReader=calcsolve.case_reader(path,file_names[0],file_names[1],file_names[2],file_names[3],file_names[4],file_names[5],file_names[6],file_names[7])
        # unpickle
        with open('ReadData.pkl','wb') as r_data:
            dictData=pickle.loads(r_data.read())

        run_solve(path,dictData)

    def run_solve(self,path,dictData):
        # solve for in service and out of service, all anchora tighten and alt released configuration
        tie_release=0
        strInService='In service'
        strOutOfService='Out of service'
        solverInTighten=calcsolve.case_solver(
            dictData.get('Anchorage'),
            dictData.get('Top load in serv'),
            dictData.get('Wind force in serv'),
            dictData.get('Wind force region in'),
            dictData.get('Mast height'),
            dictData.get('Top wind height'),
            tie_release,
            strInService
            )

        solverOutTighten=calcsolve.case_solver(
            dictData.get('Anchorage'),
            dictData.get('Top load out serv'),
            dictData.get('Wind force out serv'),
            dictData.get('Wind force region out'),
            dictData.get('Mast height'),
            dictData.get('Top wind height'),
            tie_release,
            strOutOfService
            )

        tie_release=1
        solverInReleased=calcsolve.case_solver(
            dictData.get('Anchorage'),
            dictData.get('Top load in serv'),
            dictData.get('Wind force in serv'),
            dictData.get('Wind force region in'),
            dictData.get('Mast height'),
            dictData.get('Top wind height'),
            tie_release,
            strInService
            )

        solverOutReleased=calcsolve.case_solver(
            dictData.get('Anchorage'),
            dictData.get('Top load out serv'),
            dictData.get('Wind force out serv'),
            dictData.get('Wind force region out'),
            dictData.get('Mast height'),
            dictData.get('Top wind height'),
            tie_release,
            strOutOfService
            )



gc.collect()
sys.exit()
