from math import *
import numpy as np
import matplotlib as mpl
mpl.use("agg")
import matplotlib.pyplot as plt
import os
from random import *
from vectors import Vector,Point
from planarProjections import *




for mkdir in ("Graphs","Data"):
    if not os.path.exists("./"+mkdir):
        os.makedirs("Graphs"+mkdir)

def flip(axis,dt,Is,Os,Vs=[(1,0,0),(0,1,0),(0,0,1)],cond=("time",2),
        do_PsC=False):
    Os0=Os
    def ivects(Os):
        VsC=[np.array(el) for el in Vs]
        OsC=np.array(Os)
        return [tuple(el+dt*(np.cross(OsC,el))) for el in VsC]
    def lintorot(Vs1,Vs2):
        Vs1=np.array([np.array(el) for el in Vs1])
        Vs2=np.array([np.array(el) for el in Vs2])
        Vs_vel=(Vs2-Vs1)/dt
        #Supposing Os is perpendicular to Vs:
        OsC=np.cross(Vs1,Vs_vel)/np.array(list(np.linalg.norm(vec) for vec in Vs1))**2
        OsC=[np.linalg.norm(el) for el in OsC]
        return OsC


    def dataAppend():#for each var in var_data; updates three lists in data[var
        data["time"].append(time)
        Ts,Os,As,Vs,OsC,PsC
        for i,el in list(enumerate(data))[1:]: #splice to get rid of time
            for j in range(3): data[el][j].append(eval(el)[j])


    alphas=lambda:[(Is[::-1][1-i]-Is[i-1])/Is[i]*Os[i-1]*Os[::-1][1-i] for i in
                   range(3)]
    omegas=lambda:[Os[i]+As[i]*dt for i in range(3)]
    thetas=lambda:[Ts[i]+Os[i]*dt for i in range(3)]

    vlens=tuple(mag(vec) for vec in Vs)
    Vs_to_proj=lambda Vs    :[v3_to_proj(v3) for v3 in Vs]
    proj_to_Vs=lambda projs :[proj_to_v3(proj,vlen) for proj,vlen in zip(projs,vlens)]


    time=0
    Ts,OsC,As,PsC=[0]*3,[0]*3,alphas(),Vs_to_proj(Vs)

    data={"time":[]}
    vars_data=("Ts,Os,As,Vs"+",PsC"*do_PsC).split(",")
    data.update({el:[[],[],[]] for el in vars_data})
    dataAppend()

    while {"time":time<cond[1],"rotation":Ts[axis-1]<cond[1]}[cond[0]]:
        if do_PsC:
            As,Os,Ts,Vs,PsC=alphas(),omegas(),thetas(),ivects(Os),Vs_to_proj(Vs)
        else:
            As,Os,Ts,Vs=alphas(),omegas(),thetas(),ivects(Os)
            
        """
        As,Os,Ts,Vs_new=alphas(),omegas(),thetas(),ivects(Os)
        OsC=lintorot(Vs,Vs_new)
        print(Vs[0],ivects(OsC)[0])
        Vs=Vs_new
        """
        time+=dt
        dataAppend()

    if do_PsC:
        #updating projection xcoords and ycoords into plot data
        PsCx=[[p[0] for p in P] for P in data["PsC"]]
        PsCy=[[p[1] for p in P] for P in data["PsC"]]
        data.update({"PsCx":PsCx,"PsCy":PsCy})
        vars_data=list(data)[1:]

    file_name="./Data/flipdata{}.txt".format((axis,Is,Os0,dt))
    datafile=open(file_name,"w")
    datafile.write(str(data))
    datafile.close()
    
    return {"As":As,"Os":Os,"Ts":Ts,"time":time,"file":file_name,"data":data}
    
def file_name_find(axis,Is,Os,dt):
    return "./Data/flipdata{}.txt".format((axis,Is,Os,dt))

def mkgraph(axis,Is,Os,dt):
    file_name=file_name_find(axis,Is,Os,dt)
    dataf=open(file_name,"r")
    data=eval(dataf.read())
    dataf.close()
    key_name="RotationAxis{}dt{}".format(axis,dt)
    if not os.path.exists("./Graphs/"+key_name):
        os.makedirs("./Graphs/"+key_name)

    vars_data="Ts,Os,As,Vs,PsC".split(",")
    for el in vars_data:
        if el not in ("PsC","Vs") and el in list(data):#not graphing PsC or Vs
            print("graphing...",el,"./Graphs/{}/{}Graph{}.png".format(key_name,key_name,el))
            fig=plt.figure()
            for j in range(3): plt.plot(data["time"],data[el][j],label=el+str(j))
            plt.grid()
            plt.legend()
            plt.xlabel("time (s)")
            plt.ylabel(el)
            fig.savefig("./Graphs/{}/{}Graph{}.png".format(key_name,key_name,el))


IsC=sorted([3.115,2.071,1.226],reverse=True)
IsM=sorted([2.239,1.575,1.000],reverse=True)
Is=IsM
m=.518
xc=.195
yc=1.863
zc=.725
g=32.2*12#in/s2
t0=atan(yc/zc)
h0=zc*sin(t0)+yc*cos(t0)
#print("m:{},t:{},yc:{},zc:{},h0".format(m,t0,yc,zc,h0))

o2C=-(2*m*g*h0/Is[1])**.5
OsC=[.1,o2C,.1]

def model(do_PsC=False,print_bool=False,graph_bool=False,**kwargs):
    if "Os" not in kwargs: kwargs["Os"]=[.1,-(2*m*g*h0/Is[1])**.5,.1]
    if "dt" not in kwargs: kwargs["dt"]=.01
    if "cond" not in kwargs: kwargs["cond"]=("time",2)
    dt,cond,Os=[kwargs[name] for name in ("dt","cond","Os")]
    print("Modelling with dt={}, cond={}".format(dt,cond))
    axis=2
    res=flip(axis,dt,Is,Os,cond=cond,do_PsC=do_PsC)

    Linit=[Is[i]*Os[i] for i in range(3)]
    Lfin=[Is[i]*res["Os"][i] for i in range(3)]
    if print_bool:
        for el in list(res)[:-1]: print("{}: {}".format(el,res[el]))
        print("Initial Conditions: Os={}".format(Os))
        print("\ndt:",dt)
        print("\nInit angular momenta: {}\n\tMagnitude: {}".format(Linit,sum([el**2 for el in Linit])))
        print("Final angular momenta: {}\n\tMagnitude: {}".format(Lfin,sum([el**2 for el in Lfin])))
    if graph_bool:
        mkgraph(axis,Is,Os,dt)
    return res["file"]

def __main__():
    pass
    model()

#__main__()
