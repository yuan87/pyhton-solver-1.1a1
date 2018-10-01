import csv
import os
import pickle



if __name__=='__main__':


	path=str(os.path.dirname(os.path.abspath(__file__)))
	path_text=path.replace('\\','/')+'/'
	csv_multi=path_text+'MultipleInput.csv'

	with open(csv_multi) as c_multi:
		l_main=filter(bool,list(csv.reader(c_multi)))

	#lm  : list multi

	lm=list(c_multi)
	n=0
	for line in lm:
		if (line[1]=='Stage 1':
			startAt=n
			break
		n+=1

	lm_anchor0=list(map(l_multi[n::-1], zip(*l)))

	## remove all empty in each element in lm_anchor0
	lm_anchor=list(map(lambda aList: filter(bool,aList),lm_anchor0))

	# read mast type and quantity
	
