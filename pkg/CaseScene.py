import sys
import pandas as pd
import csv
import os
import gc
import pickle
import json
# case_solver class and case_reader class
# from pkg.calcsolve import case_solver
# from pkg.calcsolve import case_reader
from .calcsolve import *
from .SolveAnsys import *




gc.enable()

def listTostr(lst):
    if len(lst)==1:
        return str(lst[0])
    else:
        outstr=str(lst[0])
        slicedlst=lst[1:]
        for j in slicedlst:
            outstr+=(','+str(j))
        return outstr


class CaseSceneIns():
    '''
    This class is function as create instances of case_reader and case_solver, ie: create creating different case
    Define working condition and cases here
    '''

    def __init__(self,path_text):

        # path0=str(os.path.dirname(os.path.abspath(__file__)))
        # path=path.replace('\\','/')+'/'
        self.path_text=path_text

        file_names=[
            'main.csv',
            'mast_achor_conf.csv',
            'misc.csv',
            'dictionary.json',
            'crane/',
            '.csv',
            'mast/mast.csv',
            'wind section/wind_section.csv'
            ]

        caseReader=case_reader(self.path_text,file_names[0],file_names[1],file_names[2],file_names[3],file_names[4],file_names[5],file_names[6],file_names[7])
        # unpickle
        with open(self.path_text+'ReadData.pkl','rb') as r_data:
            dictData=pickle.loads(r_data.read())
        # dictData=caseReader.dictData

        self.run_solve(self.path_text,dictData)

    def ansys_data(self,reader,solver):
        """ get read and solver instance"""
        l1=reader.get_ansys_data()
        l2=solver.get_ansys_data()

        z_coor0=[]
        z_coor0.extend() # extend mast height
        z_coor0.extend() # extend anchorage height
        z_coor=list(set(z_coor0)) # remove duplicate
        apdlParam=list()
        apdlParam.append(l2[0])
        apdlParam.append(l2[1])
        apdlParam.append(l2[2])
        apdlParam.append('') # slewing moment
        apdlParam.append(l1[0]) # wind WindPressure
        apdlParam.append(l1[1])
        apdlParam.append(l2[3])
        apdlParam.append(str(int(l2[3])+int(l1[1])+1))
        apdlParam.append(listTostr(l1[2]))
        apdlParam.append(listTostr(l1[3]))
        apdlParam.append(listTostr(l1[4]))
        apdlParam.append(listTostr(l1[5]))
        apdlParam.append(listTostr(l1[6]))
        apdlParam.append(listTostr(l1[7]))
        apdlParam.append(listTostr(l1[8]))
        apdlParam.append(listTostr(l1[9]))
        apdlParam.append(listTostr(l2[4])) # anchrahe height
        apdlParam.append(listTostr(z_coor)) # z coor
        apdlParam.append(self.path_text) # directory
        # 1st virsion used to have nth stage

        return apdlParam



    def run_solve(self,path,dictData):
        # solve for in service and out of service, all anchora tighten and alt released configuration

        tie_release=0
        strInService='In service'
        strOutOfService='Out of service'
        solverInTighten=case_solver(
            path,
            dictData.get('Anchorage'),
            dictData.get('Top load in serv'),
            dictData.get('Wind force in serv'),
            dictData.get('Wind force region in'),
            dictData.get('Mast height'),
            dictData.get('Top wind height'),
            tie_release,
            strInService
            )
        rInTighten=solverInTighten.output_table()
        solverAInTighten=solveansys(self.ansys_data(case_reader,solverInTighten))


        solverOutTighten=case_solver(
            path,
            dictData.get('Anchorage'),
            dictData.get('Top load out serv'),
            dictData.get('Wind force out serv'),
            dictData.get('Wind force region out'),
            dictData.get('Mast height'),
            dictData.get('Top wind height'),
            tie_release,
            strOutOfService
            )
        rOutTighten=solverOutTighten.output_table()
        solverAOutTighten=solveansys(self.ansys_data(case_reader,solverOutTighten))


        tie_release=1
        solverInReleased=case_solver(
            path,
            dictData.get('Anchorage'),
            dictData.get('Top load in serv'),
            dictData.get('Wind force in serv'),
            dictData.get('Wind force region in'),
            dictData.get('Mast height'),
            dictData.get('Top wind height'),
            tie_release,
            strInService
            )
        rInReleased=solverInReleased.output_table()
        solverAInReleased=solveansys(self.ansys_data(case_reader,solverInReleased))


        solverOutReleased=case_solver(
            path,
            dictData.get('Anchorage'),
            dictData.get('Top load out serv'),
            dictData.get('Wind force out serv'),
            dictData.get('Wind force region out'),
            dictData.get('Mast height'),
            dictData.get('Top wind height'),
            tie_release,
            strOutOfService
            )
        rOutReleased=solverOutReleased.output_table()
        solverAOutReleased=solveansys(self.ansys_data(case_reader,solverOutReleased))

        self.dictData=dictData
        self.rList=[rInTighten,rOutTighten,rInReleased,rOutReleased]

    def get_result(self):
        return str(self.dictData.get('Mast height')),self.rList




gc.collect()
