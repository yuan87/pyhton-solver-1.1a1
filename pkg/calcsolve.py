import sys
import numpy as np
import csv
import os
# from itertools import izip  #(not require in python 3 and above)
import math
import gc
import pandas as pd
import pickle
import json


gc.enable()



# alternate release tie back? Y=1, N=0
#release_tie=1

#print(os.path.dirname(os.path.abspath(__file__)))

########
# wind area coef from 45 degree
wa_coef=1.2
########

########
gravity=10
steel_density=7850
########

def altenate_release2(listH):

	x = len(listH)
	listH0=list()
	num=x-int(x/2)
	iStart=x-(2*num)+1
	i=0
	for i in range(0,num):
		H0=listH[iStart+i*2]
		listH0.append(H0)
		i+=1

	return listH0

# def listTostr(lst):
# 	if len(lst)==1:
# 		return str(lst[0])
# 	else:
# 		outstr=str(lst[0])
# 		slicedlst=lst[1:]
# 		for j in slicedlst:
# 			outstr+=(','+str(j))
# 		return outstr
#

class case_solver():
	def __init__(self,path_text,listAnchor0,topLoad,windForce,windForceRegion,mastHeight,topWindHeight,tie_release,windCondition):
		'''
		listAnchor = list anchorage height position
		topLoad = top part moment , Fh , Fv (moment in tm, force in t)
		windForce = wind force per unit length (N/m)
		windForceRegion =
		mastHeight =
		topWindHeight =
		tie_release =
		'''

		self.path_text=path_text
		self.listAnchor0=listAnchor0
		self.topLoad=topLoad
		self.windForce=windForce				#list
		self.windForceRegion=windForceRegion		#list
		self.mastHeight=mastHeight
		self.topWindHeight=topWindHeight
		self.tie_release=tie_release
		self.windCondition=windCondition

		# print(self.path_text,self.listAnchor0,self.topLoad,self.windForce,self.windForceRegion,self.mastHeight,self.topWindHeight,self.tie_release,self.windCondition,'\n\n')

		if (tie_release==1):
			self.strTie='Alt released'
		if (tie_release==0):
			self.strTie='All tighten'

		# Output title for current case
		title='Mast Height %sm,  Anchorage:%s,  %s,  %s'
		title=title %(str(mastHeight),str(listAnchor0),self.strTie,self.windCondition)

		self.title=title
		self.calc()


	def calc(self):
		if (self.tie_release==1):
			self.listAnchor=self.alt_release_tie(self.listAnchor0)
		else:
			self.listAnchor=self.listAnchor0

		# total deflection by external load
		moment=self.topLoad[0]
		force_horizontal=self.topLoad[1]
		force_verticle=self.topLoad[2]
		l_deM=list()
		l_deFh=list()
		l_deWP=list()

		l_dA=list()

		for anchor in self.listAnchor:

			# deflection by M
			deM=-moment*gravity*anchor*anchor/2*1000
			l_deM.append(deM)
			# deflection by Fh
			deFh=force_horizontal*gravity/6*(anchor**3-3*(self.mastHeight+self.topWindHeight)*anchor**2)*1000
			l_deFh.append(deFh)
			# deflection by q
			windReg=self.windForceRegion[1:]
			windReg.append(self.mastHeight)

			deWP=0  # deflection by wind pressure for each tie (sum of all wind region)

			for wf,h in zip(self.windForce,windReg):
				# find deflection by wind pressure in each wind region
				deWP0=0

				if len(windReg)==1:
					previous_wp_height=0
				else:
					iii=windReg.index(h)-1
					if iii==-1:
						previous_wp_height=0
					else:
						previous_wp_height=windReg[windReg.index(h)-1]

				if anchor<h:
					deWP0=wf*h/24*(6*(h-previous_wp_height)*anchor**2-4*anchor**3+anchor**4/(h-previous_wp_height))*-1
				else:
					deWP0=wf*h/24*(4*(h-previous_wp_height)**2*anchor-(h-previous_wp_height)**3)*-1
				deWP+=deWP0
			l_deWP.append(deWP)

			# deflection cause by anchor forces
			# l_dA[1][1] force cause by anchor 1 at anchor 1, l_dA[1][2] force cause by anchor 2 at anchor 1, l_dA[2][2] force cause by anchor 2 at anchor 2
			l_dASub=list()
			for anchorAct in self.listAnchor:
				# loop 1:calculate force acting of anchor1 by anchor 1,2,3 ....n
#				if anchor<anchorAct:
#					dA=1*anchorAct**3/3*(anchorAct-anchor)/2/anchorAct+(anchorAct-anchor)**3/2/anchorAct**3
#				else:
#					dA=1*anchorAct**3/3*(1+3*(anchor-anchorAct)/2/anchorAct)

				if anchor<anchorAct:
					dA=anchor**2/6*(anchor-3*anchorAct)
				else:
					dA=anchorAct**2/6*(anchorAct-3*anchor)

				l_dASub.append(dA)
			l_dA.append(l_dASub)

		# print(l_deM)
		# print(l_deFh)
		# print(l_deWP)

		l_de=[k1+k2+k3 for k1,k2,k3 in zip(l_deM,l_deFh,l_deWP)]   # sum of deflection


		arr_fa=np.linalg.solve(np.array(l_dA),np.array(l_de))
		# arr_fa value change to int in list format
		l_fa=list(map(lambda f:int(f),arr_fa.tolist()))


		# print(l_fa)

		# zip height input and anchorage reaction together for output as a table
		self.tab_fa=list(zip(self.listAnchor,l_fa))


		out_lst.append(str(self.topLoad[0]))
		out_lst.append(str(self.topLoad[1]))
		out_lst.append(str(self.topLoad[2]))
		out_lst.append(str(len(self.listAnchor)))
		out_lst.append(self.listAnchor)




	def output_table(self):
		l_fa_to_an=list()

		for anchor in self.listAnchor0:
			boo=False
			for anchor0,fa in self.tab_fa:
				if anchor==anchor0:
					boo=True
					l_fa_to_an.append((anchor0,str(fa)))
			if not boo:
				l_fa_to_an.append((anchor,'-'))

		# print(l_fa_to_an)
		self.l_fa_to_an=l_fa_to_an

		# pickle tab_out
		# outFile=self.path_text+'OutpuTResult.pkl'
		# with open(outFile,'wb') as pk_out:
		# 	pickle.dump(self.l_fa_to_an,pk_out)

		###
		csv_out=self.path_text+'OutputResult.csv'
		with open(csv_out,'a') as c_out:
			writer=csv.writer(c_out)
			writer.writerow([self.title])
			# writer.writerow(self.listAnchor0)
			writer.writerow(l_fa_to_an)

		# return result
		return list(map(lambda ls: list(ls),l_fa_to_an))

	def alt_release_tie(self,listH):
		listH0=listH[::-1]
		listH0=listH0[::2]
		listH0.reverse()
		return listH0

	def get_ansys_data(self):
		return self.out_lst


# return list of wind forces value, and height of wind forces value start change
def get_wind_force_height(inlst):
	lstR=list()
	lst1=list()
	lstCount=list()
	count1=0
	for a in inlst:
		if a not in lst1:
			lst1.append(a)
			lstCount.append(count1)
		count1+=1
	lstR.append(lst1)
	lstR.append(lstCount)
	return lstR



#path=str(os.path.dirname(os.path.abspath(__file__)))
#path_text=path.replace('\\','/')+'/'

class case_reader():
	'''
	Input:
	path and file name

	Output:
	write to csv_read_data
	listAnchor = list anchorage height position
	topLoad = top part moment , Fh , Fv (moment in tm, force in t)
	windForce = wind force per unit length (N/m)
	windForceRegion =
	mastHeight =
	topWindHeight =
	tie_release =
	'''
	def __init__(self,path_text,file_main,file_ma_conf,file_misc,file_dictionary,dir_crane,file_crane,file_mast,file_wind):
		self.path_text=path_text
		self.file_main=file_main
		self.file_ma_conf=file_ma_conf
		self.file_misc=file_misc
		self.file_dictionary=file_dictionary
		self.dir_crane=dir_crane
		self.file_crane=file_crane
		self.file_mast=file_mast
		self.file_wind=file_wind
		self.fieldnames=['Anchorage','Top load in serv','Wind force in serv','Wind force region in','Top load out serv','Wind force out serv','Wind force region out','Mast height','Top wind height']
		self.out_lst=list()

		self.read_helper()



	def read_helper(self):
		csv_main=self.path_text+self.file_main

		with open(csv_main) as c_main:
			l_main=filter(bool,list(csv.reader(c_main)))

		l_main=list(l_main)

		craneType=int(l_main[0][1])
		jibLength=float(l_main[1][1])

		####------- Rearrange mast and anchorage input data to "mast_anchor_conf.csv" ---------####
		csv_ma_conf=self.path_text+self.file_ma_conf

		with open(csv_ma_conf) as c_ma_conf:
			l_ma_conf=filter(bool,list(csv.reader(c_ma_conf)))

		l_ma_conf=list(l_ma_conf)


		mastTypeNo=int(list(filter(bool,l_ma_conf[0]))[1])

		mastType=list()

		mastQuantity=list()

		for i in range(1,mastTypeNo+1):

			mastType.append(int(l_ma_conf[1][i]))
			mastQuantity.append(float(l_ma_conf[2][i]))

		# print(l_ma_conf)
		collarHeight0=(filter(bool,l_ma_conf[3][1:]))
		collarHeight=list(map(lambda a0:float(a0),collarHeight0))

		csv_misc=self.path_text+self.file_misc

		with open(csv_misc) as c_misc:
			l_misc=list(csv.reader(c_misc))

		addHeight1=float(l_misc[0][1])  # height of fixing angle
		addHeight2=float(l_misc[1][1])  # additional height from mast top to center of top part wind force acting
		addForce=float(l_misc[2][1])    # additional horizontal force acting of mast
		addForceH=float(l_misc[3][1])   # height position of additional horizontal force acting

		topWindHeight=addHeight2

		dictionary_file=self.path_text+self.file_dictionary


		with open(dictionary_file,'r') as df:
			strdf=df.read()
		dict0=json.loads(strdf)

		# dMast
		# dCrane
		dCrane0=dict0['dCrane']['list']
		dMast0=dict0['dMast']['list']
		dCrane={}
		for d1 in dCrane0:
			dCrane.update(d1)
		dMast={}
		for d2 in dMast0:
			dMast.update(d2)

		# get crane model Eg: STT293 or STL230
		for indexCrane, nameCrane in dCrane.items():
			if int(indexCrane)==craneType:
				craneModel=nameCrane
				break

		# get mast model in a list Eg: L69B1, H205B
		mastModel=list()

		for mt in mastType:
			for indexMast, nameMast in dMast.items():
				if int(indexMast)==mt:
					mastModel.append(nameMast)
					break

		# read specific crane model data
		csv_crane=self.path_text+self.dir_crane+craneModel+self.file_crane

		with open(csv_crane) as c_crane:
			l_crane=list(csv.reader(c_crane))

		l_crane=filter(bool,l_crane[3:])

		for row in l_crane:
			if float(row[0])==jibLength:
				row0=list()
				for j in filter(bool,row[1:]):
					row0.append(float(j))
					R_IN_SERV=row0[0:3]
					R_OUT_SERV=row0[3:]
				break

		# R_IN_SERV: in service data for specific crane and jib length
		# R_OUT_SERV: out of service data for specific crane and jib length

		csv_mast=self.path_text+self.file_mast

		with open(csv_mast) as c_mast:
			l_mast=list(csv.reader(c_mast))
		l_mast=filter(bool,l_mast[2:])

		mastProp=list()
		for k in mastType:
			mastPropRow=list()
			for row in l_mast:
				if int(row[0])==int(k):
					mastPropRow0=filter(bool,row[1:])

					for l in mastPropRow0:
						mastPropRow.append(float(l))
					break
			mastProp.append(mastPropRow)

		mastProps=list()
		for item in mastProp:
			area_devide=item[2]/item[0]*wa_coef
			res=item
			item.append(area_devide)
			mastProps.append(res)
		mastPropKey=[
			'length',
			'weight',
			'wind_area',
			'main_chord_area',
			'iyy',
			'izz',
			'area_unit_length'
			]

		count=0
		mast_data=list()
		for n in mastProps:
			mast_data.append(dict(zip(mastPropKey,n)))

		csv_wind=self.path_text+self.file_wind

		with open(csv_wind) as c_wind:
			l_wind=list(csv.reader(c_wind))
		l_wind=list(filter(bool,l_wind[1:]))


		# in service wind pressure
		inServWindP=float(l_wind[0][1])

		outServWindH0=list()
		outServWindP=list()

		# outServWindH0= list of height in float, outServWindP list of wind pressure in float
		outServWindH0=list(map(lambda a1:float(a1),l_wind[1][1:]))
		outServWindP=list(map(lambda a2:float(a2),l_wind[2][1:]))

		#dictionary?
		craneHeight00=0
		craneHeight=0
		sectionHeight=list() #different mast section height
		for p in range(0,mastTypeNo):
			craneHeight0=mast_data[p].get('length')*mastQuantity[p]
			craneHeight=craneHeight+craneHeight0
			sectionHeight.append(craneHeight0+craneHeight00)
			craneHeight00=craneHeight0

		windProfile=list()
		areaProfile=list()

		acc=0
		c1=0
		for sh in sectionHeight:
			for w in range(acc,int(math.ceil(sh))):
				areaProfile.append(mast_data[c1].get('area_unit_length'))
			acc=int(math.ceil(sh))
			c1+=1


		a0=0
		outServWindH=list()
		for r in outServWindH0:
			if craneHeight<=r and r!=0.0:
				outServWindH.append(craneHeight)
				break
			else:
				outServWindH.append(r)
			if r==0.0:
				outServWindH[a0]=craneHeight
			a0+=1

		acc0=0
		c2=0
		for  swh in outServWindH:
			for x in range(int(acc0),(int(math.ceil(swh)))):

				windProfile.append(outServWindP[c2])
			acc0=int(math.ceil(swh))
			c2+=1

		# arrWindForceO=np.multiply(np.array(areaProfile),np.array(windProfile)).tolist() ## numpy method
		arrWindForceO=[a*b for a,b in zip(areaProfile,windProfile)]

		# in service wind force
		# arrWindForceI=(inServWindP*np.array(areaProfile)).tolist() ## numpy method
		arrWindForceI=list(map(lambda x0:x0*inServWindP,areaProfile))   # per meter

		lWindForceI=get_wind_force_height(arrWindForceI)
		lWindForceO=get_wind_force_height(arrWindForceO)

		# check last element in arrWindForceO, arrWindForceI
		if craneHeight%1!=0:
			wForceI= float(craneHeight%1)*arrWindForceI[-1]
			wForceO= float(craneHeight%1)*arrWindForceO[-1]
			arrWindForceI[-1]=wForceI
			arrWindForceO[-1]=wForceO
			## TODO: Check
			lWindForceI=get_wind_force_height(arrWindForceI)
			lWindForceO=get_wind_force_height(arrWindForceO)

		listAnchor=list()

		mastHeight=craneHeight+addHeight1

		lData=list()
		lData.append(collarHeight)
		lData.append(R_IN_SERV)
		lData.append(lWindForceI[0])
		lData.append(lWindForceI[1])
		lData.append(R_OUT_SERV)
		lData.append(lWindForceO[0])
		lData.append(lWindForceO[1])
		lData.append(mastHeight)
		lData.append(topWindHeight)
		self.dictData=dict(zip(self.fieldnames,lData))

		# output read_helper data to  pickle
		pkl_read_data=self.path_text+'ReadData.pkl'
		with open(pkl_read_data,'wb') as c_read_data:
			pickle.dump(self.dictData,c_read_data)

		lmastH=list()
		lstLen=[ele.get('length') for ele in mastProps]
		sumProduct=float()
		for mq,ll in (zip(mastQuantity,lstLen)):
			product=mq*ll
			sumProduct+=product
			lmastH.append(sumProduct)
		lmastH0=[0].extend(lmastH)

		out_lst.append(“windpressure”)
		out_lst.append(str(mastTypeNo))
		out_lst.append((mastQuantity))
		out_lst.append([item[0] for item in mastProp]) # length
		out_lst.append([item[2] for item in mastProp]) # mast wind area
		out_lst.append([item[1]/item[0]/item[3]/4/steel_density for item in mastProp]) # mast weight / mast length / main chord x-section / 4 / steel density
		out_lst.append(lmastH) # list of  0, base mast height postion (top), base mast 2 height postion (top), standard mast height postion (top)
		out_lst.append([item[3] for item in mastProp]) # mast X-section
		out_lst.append([item[4] for item in mastProp]) # mast Iyy
		out_lst.append([item[5] for item in mastProp]) # mast Izz

	def get_ansys_data(self):
		return self.out_lst



# if __name__=='__main__':
# 	pass
	###>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Below lines are restructured to class case_reader > read_helper <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<##
	# path=str(os.path.dirname(os.path.abspath(__file__)))
	# csv_main=path.replace('\\','/')+'/'+'main.csv'
	#
	# with open(csv_main) as c_main:
	# 	l_main=filter(bool,list(csv.reader(c_main)))
	#
	# l_main=list(l_main)
	#
	# craneType=int(l_main[0][1])
	# jibLength=float(l_main[1][1])
	#
	# mastTypeNo=len(list(filter(bool,l_main[2])))-1
	#
	# mastType=list()
	#
	# mastQuantity=list()
	# for i in range(1,mastTypeNo+1):
	# 	mastType.append(int(l_main[3][i]))
	# 	mastQuantity.append(float(l_main[4][i]))
	#
	#
	# collarHeight0=(filter(bool,l_main[5][1:]))
	# collarHeight=list(map(lambda a0:float(a0),collarHeight0))
	#
	# csv_misc=path.replace('\\','/')+'/'+'misc.csv'
	#
	# with open(csv_misc) as c_misc:
	# 	l_misc=list(csv.reader(c_misc))
	#
	# addHeight1=float(l_misc[0][1])  # height of fixing angle
	# addHeight2=float(l_misc[1][1])  # additional height from mast top to center of top part wind force acting
	# addForce=float(l_misc[2][1])    # additional horizontal force acting of mast
	# addForceH=float(l_misc[3][1])   # height position of additional horizontal force acting
	#
	# topWindHeight=addHeight2
	#
	# dictionary_file=path.replace('\\','/')+'/'+'dictionary.py'
	# exec(open(dictionary_file).read())
	# # dMast
	# # dCrane
	#
	#
	# # get crane model Eg: STT293 or STL230
	# for indexCrane, nameCrane in dCrane.items():
	# 	if int(indexCrane)==craneType:
	# 		craneModel=nameCrane
	# 		break
	#
	# # get mast model in a list Eg: L69B1, H205B
	# mastModel=list()
	#
	# for mt in mastType:
	# 	for indexMast, nameMast in dMast.items():
	# 		if int(indexMast)==mt:
	# 			mastModel.append(nameMast)
	# 			break
	#
	# # read specific crane model data
	# csv_crane=path.replace('\\','/')+'/crane/%s.csv'
	# csv_crane=csv_crane %(craneModel)
	#
	# with open(csv_crane) as c_crane:
	# 	l_crane=list(csv.reader(c_crane))
	#
	# l_crane=filter(bool,l_crane[3:])
	#
	# for row in l_crane:
	# 	if float(row[0])==jibLength:
	# 		row0=list()
	# 		for j in filter(bool,row[1:]):
	# 			row0.append(float(j))
	# 			R_IN_SERV=row0[0:3]
	# 			R_OUT_SERV=row0[3:]
	# 		break
	#
	# # R_IN_SERV: in service data for specific crane and jib length
	# # R_OUT_SERV: out of service data for specific crane and jib length
	#
	# csv_mast=path.replace('\\','/')+'/mast/mast.csv'
	#
	# with open(csv_mast) as c_mast:
	# 	l_mast=list(csv.reader(c_mast))
	# l_mast=filter(bool,l_mast[2:])
	#
	# mastProp=list()
	# for k in mastType:
	# 	mastPropRow=list()
	# 	for row in l_mast:
	# 		if int(row[0])==int(k):
	# 			mastPropRow0=filter(bool,row[1:])
	#
	# 			for l in mastPropRow0:
	# 				mastPropRow.append(float(l))
	# 			break
	# 	mastProp.append(mastPropRow)
	#
	# mastProps=list()
	# for item in mastProp:
	# 	area_devide=item[2]/item[0]*wa_coef
	# 	res=item
	# 	item.append(area_devide)
	# 	mastProps.append(res)
	# mastPropKey=[
	# 	'length',
	# 	'weight',
	# 	'wind_area',
	# 	'main_chord_area',
	# 	'iyy',
	# 	'izz',
	# 	'area_unit_length'
	# 	]
	#
	# count=0
	# mast_data=list()
	# for n in mastProps:
	# 	mast_data.append(dict(zip(mastPropKey,n)))
	#
	# csv_wind=path.replace('\\','/')+'/wind section/wind_section.csv'
	# with open(csv_wind) as c_wind:
	# 	l_wind=list(csv.reader(c_wind))
	# l_wind=list(filter(bool,l_wind[1:]))
	#
	#
	# # in service wind pressure
	# inServWindP=float(l_wind[0][1])
	#
	# outServWindH0=list()
	# outServWindP=list()
	#
	# # outServWindH0= list of height in float, outServWindP list of wind pressure in float
	# outServWindH0=list(map(lambda a1:float(a1),l_wind[1][1:]))
	# outServWindP=list(map(lambda a2:float(a2),l_wind[2][1:]))
	#
	# #dictionary?
	# craneHeight00=0
	# craneHeight=0
	# sectionHeight=list() #different mast section height
	# for p in range(0,mastTypeNo):
	# 	craneHeight0=mast_data[p].get('length')*mastQuantity[p]
	# 	craneHeight=craneHeight+craneHeight0
	# 	sectionHeight.append(craneHeight0+craneHeight00)
	# 	craneHeight00=craneHeight0
	#
	# windProfile=list()
	# areaProfile=list()
	#
	# acc=0
	# c1=0
	# for sh in sectionHeight:
	# 	for w in range(acc,int(math.ceil(sh))):
	# 		areaProfile.append(mast_data[c1].get('area_unit_length'))
	# 	acc=int(math.ceil(sh))
	# 	c1+=1
	#
	#
	# a0=0
	# outServWindH=list()
	# for r in outServWindH0:
	# 	if craneHeight<=r and r!=0.0:
	# 		outServWindH.append(craneHeight)
	# 		break
	# 	else:
	# 		outServWindH.append(r)
	# 	if r==0.0:
	# 		outServWindH[a0]=craneHeight
	# 	a0+=1
	#
	# acc0=0
	# c2=0
	# for  swh in outServWindH:
	# 	for x in range(int(acc0),(int(math.ceil(swh)))):
	#
	# 		windProfile.append(outServWindP[c2])
	# 	acc0=int(math.ceil(swh))
	# 	c2+=1
	#
	# # arrWindForceO=np.multiply(np.array(areaProfile),np.array(windProfile)).tolist() ## numpy method
	# arrWindForceO=[a*b for a,b in zip(areaProfile,windProfile)]
	#
	# # in service wind force
	# # arrWindForceI=(inServWindP*np.array(areaProfile)).tolist() ## numpy method
	# arrWindForceI=list(map(lambda x0:x0*inServWindP,areaProfile))   # per meter
	#
	# lWindForceI=get_wind_force_height(arrWindForceI)
	# lWindForceO=get_wind_force_height(arrWindForceO)
	#
	# # check last element in arrWindForceO, arrWindForceI
	# if craneHeight%1!=0:
	# 	wForceI= float(craneHeight%1)*arrWindForceI[-1]
	# 	wForceO= float(craneHeight%1)*arrWindForceO[-1]
	# 	arrWindForceI[-1]=wForceI
	# 	arrWindForceO[-1]=wForceO
	#
	# listAnchor=list()
	#
	# mastHeight=craneHeight+addHeight1


##>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Restructured lines end here<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<##

	# R_IN_SERV, R_OUT_SERV

	##########
	# calculate working case here
	##########



	# alt_release_tie() for collarHeight to obtain a alternate release tie arrangement
	# last parameter 0: all tie tighten 1: tie alternate release

	#in_service_case=case_solver(collarHeight,R_IN_SERV,lWindForceI[0],lWindForceI[1],mastHeight,topWindHeight,0)
	#in_service_case.calc()
	#in_service_case.output_table()


	# in_service_case_alt=case_solver(collarHeight,R_IN_SERV,lWindForceI[0],lWindForceI[1],mastHeight,topWindHeight,1)
	# in_service_case_alt.calc()
	# l_in_service_alt=in_service_case_alt.output_table()

	#

gc.collect()
