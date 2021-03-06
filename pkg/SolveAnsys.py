import gc
import os, subprocess


apdlTxt="""
FINISH
/FILNAME,Anchor,1
/CLEAR,NOSTART
/prep7
/UIS,MSGPOP,3

/VIEW,1,,-1
/ANG,1
/REP,FAST

Mtop = %s
Ftop = %s
Fv = %s
Mslew = %s
WindPressure = %s

N_type = %s
N_anchorage = %s
N_point= %s

*DIM,Q_mast,,N_type
Q_mast(1)=%s

*DIM,L_mast,,N_type
L_mast(1)=%s

*DIM,A_mast,,N_type
A_mast(1)=%s

*DIM,C0_mast,,N_type
C0_mast(1)=%s

*DIM,H_mast,,N_type
H_mast(1)=%s

*DIM,XSection_mast,,N_type
XSection_mast(1)=%s

*DIM,Iyy_mast,,N_type
Iyy_mast(1)=%s


*DIM,Izz_mast,,N_type
Izz_mast(1)=%s

*DIM,H_anchorage,,N_anchorage
H_anchorage(1)=%s

ET,1,BEAM4
*DO,i,1,N_type,1
  MPTEMP,,,,,,,,
  MPTEMP,1,0
  MPDATA,EX,i,,2.06e11
  MPDATA,PRXY,i,,0.3
  MPTEMP,,,,,,,,
  MPTEMP,1,0
  MPDATA,DENS,i,,C0_mast(i)* 7850
*ENDDO

*DO,i,1,N_type,1
	R,i,XSection_mast(i),Iyy_mast(i),Izz_mast(i),,,,
*ENDDO
RMORE, , , , , , ,

*DIM,Z_coor,,N_point
Z_coor(1)=%s

*DO,i,1,N_point,1
	K,i,0,0,Z_coor(i)
*ENDDO

*DO,i,1,(N_point - 1) ,1
	L,i,i+1
*ENDDO

H01=0
*DO,i,1,N_type,1
	LSEL, ,LOC,Z,(H01-0.1),(H01 + H_mast(i) + 0.1)
	H01 = H01 + H_mast(i)

	  !!Assign section!!
	  LATT,i,i,1, , , ,

*ENDDO
Allsel,all
LESIZE,all,0.02, , , , , , ,1
LMESH,all
ksel,,,,N_point

FK,all,Fz,-Fv
FK,all,Fx,Ftop
FK,all,My,Mtop
FK,all,Mz,Mslew
*DIM,Fw_mast,,N_type

*DO,i,1,N_type,1
	Fw_mast(i)=A_mast(i)*WindPressure / L_mast(i)
*ENDDO

H01=0
*DO,i,1,N_type,1

	LSEL, ,LOC,Z,(H01-0.05),(H01 + H_mast(i) + 0.05)
	H01 = H01 + H_mast(i)
	ESLL
	/MREP,EPLOT
	SFBEAM,all,1,PRES,Fw_mast(i), , , , , ,

*ENDDO

KSEL,S,LOC,Z,-0.01,0.01
DK,ALL, , , ,0,ALL , , , , ,

*DO,i,1,N_anchorage,1
	KSEL,S,LOC,Z,H_anchorage(i)-0.01,H_anchorage(i)+0.01
	NSLK
	D,ALL, , , , , ,UX,UY, , , ,
*ENDDO

ACEL,0,0,9.81

/SOL
ANTYPE,0
NLGEOM,1
ALLSEL
SOLVE
FINI
/POST1

*DIM,FrX,,N_anchorage

*DO,i,1,N_anchorage,1
	KSEL,S,LOC,Z,H_anchorage(i)-0.01,H_anchorage(i)+0.01
	NSLK
	FSUM,0,ALL
	*GET,Frx0,FSUM,0,item,FX
	FrX(i) = -FrX0
*ENDDO

*CREATE,ansuitmp
*CFOPEN,'%sfo_FrX %s','lst',' '
*VWRITE,FrX(1), , , , , , , , ,
(F12.4)
*CFCLOS
*END
/INPUT,ansuitmp
/AUTO,1
/VIEW,1,,-1
/ANG,1
"""



gc.enable()

class solveansys:


    def __init__(self,apdlParam):
        """
        """
        self.moment=apdlParam[0]
		self.force_horizontal=apdlParam[1]
		self.force_verticle=apdlParam[2]
		self.moment_slewing=apdlParam[3]
		self.windPressure=apdlParam[4]
		self.noMastType=apdlParam[5]
		self.noAnchorage=apdlParam[6]
		self.noPoint=apdlParam[7]
		self.strMQ=apdlParam[8]
        self.strML=apdlParam[8]
        self.strMWA=apdlParam[10]
        self.strMC0=apdlParam[11]
        self.strMH=apdlParam[12]
        self.strMXS=apdlParam[13]
        self.strMIyy=apdlParam[14]
        self.strMIzz=apdlParam[15]
        self.strHA=apdlParam[16]
        self.strZC=apdlParam[17]
        self.outDirectory=apdlParam[18]



    def parameteransys(self):


        # apdlTxt=apdlTxt %(str(Mtop),str(Fh),str(Fv),"0",str(windPressure),str(len(mastType)),str(noAnchorage),str(noAnchorage+len(mastType)+1),strMQ,strML,strMWA,strMC0,strMH,strMXS,strMIyy,strMIzz,strHA,strZC,outDirectory,str(nthStage))
        apdlTxt=apdlTxt %(
            self.moment,
            self.force_horizontal,
            self.force_verticle,
            self.moment_slewing,
            self.windPressure,
            self.noMastType,
            self.noAnchorage,
            self.noPoint,
            self.strMQ,
            self.strML,
            self.strMWA,
            self.strMC0,
            self.strMH,
            self.strMXS,
            self.mastIyy,
            self.mastIzz,
            self.strHA,
            self.strZC,
            self.outDirectory
            )
