import intermediateAxis as iax
import numpy as np
import anim3d as an
import os


def graph_model():
    file_name=iax.model(dt=.001,cond=("time",5),graph_bool=True,do_PsC=True)

def get_data():
    file_name=iax.model(dt=.001,cond=("time",2))
    f=open(file_name,"r")
    data=eval(f.read())
    f.close()

def animate_model():
    an.__main__()
    
def OsC_vs_Os():
    #print(data["Vs"])
    #OSC vs OS comparison
    deltas=list(np.array(data["OsC"])-np.array(data["Os"]))
    len_d=len(deltas[0])
    for el in [[delt[i] for i in range(0,len_d,len_d//20)] for delt in deltas]:
        print(el,"\n")
def __main__():
    graph_model()
    get_data()
    #animate_model()
    #OsC_vs_Os()

__main__()
