import csv
import os



if __name__=='__main__':


	path=str(os.path.dirname(os.path.abspath(__file__)))
	csv_multi=path.replace('\\','/')+'/'+'MultipleInput.csv'

	with open(csv_multi) as c_multi:
		l_main=filter(bool,list(csv.reader(c_multi)))

	#lm  : list multi

	lm=list(c_multi)
	lm_anchor=l_multi[1:-2:-1]
	
