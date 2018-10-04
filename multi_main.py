import sys
import csv
import os
#import pickle
import gc
from pkg.CaseScene import CaseSceneIns



gc.enable()

def runCase(nLoop):

	# create "mast_achor_conf.csv" for different mast combination height and collar combination, "mast_achor_conf.csv" will be read by calcsolve.case_reader
	csv_WriteConf=path_text+'mast_achor_conf.csv'
	l_write=list()
	l_write.append(ma_conf[0])
	l_write.append(ma_conf[1])
	# join title to list
	l_TitleMastType=['each mast no']+l_mastType[nLoop+1]
	l_write.append(l_TitleMastType)
	l_TitleAnchor=['collar height']+lm_anchor[nLoop]


	with open(csv_WriteConf,'w') as c_WriteConf:
		confWriter=csv.writer(c_WriteConf,delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		for ll in l_write:
			confWriter.writerow(ll)

	CaseSceneIns(path_text)


if __name__=='__main__':


	path=str(os.path.dirname(os.path.abspath(__file__)))
	path_text=path.replace('\\','/')+'/'
	# path_text='D:/TYS/Project/python solver 1.1/'
	csv_multi=path_text+'MultipleInput.csv'


	with open(csv_multi) as c_multi:
		l_main=filter(bool,list(csv.reader(c_multi)))

	#lm  : list multi

	lm=list(l_main)

	n=0
	for line in lm:
		if (line[0]=='Note:'):
			break
		n+=1

	noOfStage=len(list(filter(bool,lm[2])))-1
	noMastType=len(list(filter(bool,lm[1])))-1

	l_mastType0=list()
	l_mastType0=lm[2:n-1]

	l_mastType00=list(map(lambda aL: list(filter(bool,aL[1:])),l_mastType0))
	l_mastType=list(map(list,zip(*list(filter(bool,l_mastType00)))))
	#print(l_mastType)

	# l_mastType0=list()
	# for c1 in range(2,n):
	# 	l_mastType0.append(lm[c1][1:noOfStage-1])
	# 	c1+=1
	#
	# l_mastType1=list(map(list,zip(*l_mastType0)))
	# l_mastType2=l_mastType1[1:]
	# l_mastType=list(map(lambda a0: list(filter(bool,a0)),l_mastType2))

	lm_anchor00=list()
	for l1 in lm[n+2:]:
		lm_anchor00.append(l1[2:noOfStage+1])



	lm_anchor0=list(map(lambda x0: x0[::-1],list(map(list, zip(*lm_anchor00)))))

	## remove all empty in each element in lm_anchor0, lm_anchor is a list of list
	lm_anchor=list(map(lambda aList: list(filter(bool,aList)),lm_anchor0))
	# for li in lm_anchor:
	# 	print(li)
	# read mast type and quantity
	# mast and anchorage data

	ma_conf=list(map(lambda bList: list(filter(bool,bList)),lm[:2]))



	# clear 'OutputResult.csv' content
	csv_out=path_text+'OutputResult.csv'
	with open(csv_out,'w+') as c_out:
		c_out.truncate()


	for nLoop in range(0,noOfStage-1):
		runCase(nLoop)

gc.collect()
sys.exit()
