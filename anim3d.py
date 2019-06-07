user_exec_yes=False
if __name__ =="__main__":
    user_exec_yes=input("exec?") in ["y","Y",""]
if user_exec_yes: print("Initializing Program.")

import numpy as np
import matplotlib as mpl
mpl.use("agg")
mpl.rcParams["animation.ffmpeg_path"]="/cygdrive/c/Users/awaw6/ffmpeg/bin/ffmpeg.exe"
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from mpl_toolkits.mplot3d.art3d import Poly3DCollection as p3c
import matplotlib.animation as ani
import matplotlib.colors as colors
import intermediateAxis as ia
import os
import track_data as td
import planarProjections as pp

class Rot_Box(object):

    mag=lambda self,vec:sum([el**2 for el in vec])**.5


    def __init__(self,scale=(1,1,1)):
        rnd=lambda x:int(x+.5*(1-2*(x<0)))
        mrnd=lambda m: tuple(rnd(el) for el in m)

        strc=lambda vx,scale:tuple(ela*elb for ela,elb in zip(vx,scale))
        mmstrc=lambda verts,scale:[[strc(vx,scale) for vx in vxs] for vxs in verts]

        mrotx=lambda t:np.array([[1,0,0],
                                [0,np.cos(t),-np.sin(t)],
                                [0,np.sin(t),np.cos(t)]
                               ])
        mroty=lambda t:np.array([[np.cos(t),0,np.sin(t)],
                                [0,1,0],
                                [-np.sin(t),0,np.cos(t)]
                               ])
        mrotz=lambda t:np.array([[np.cos(t),-np.sin(t),0],
                                [np.sin(t),np.cos(t),0],
                                [0,0,1]
                               ])
        rotx=lambda t,vx:np.matmul(mrotx(t),vx)
        roty=lambda t,vx:np.matmul(mroty(t),vx)
        rotz=lambda t,vx:np.matmul(mrotz(t),vx)
        rotmcc=lambda mt,vx:rotx(mt[0],roty(mt[1],rotz(mt[2],vx)))
        self.rotmcc=rotmcc
        
        x=[-1,-1, 1, 1]
        y=[-1,-1,-1,-1]#normal axis
        z=[-1, 1, 1,-1]
        self.scale=scale

        verts=[list(zip(x,y,z))]
        for i in range(3):
            verts+=[[mrnd(tuple(rotx(np.pi/2,vx))) for vx in verts[-1]]]
        for i in (1,-1):
            verts+=[[mrnd(tuple(rotz(np.pi/2*i,vx))) for vx in verts[0]]]
        self.verts=mmstrc(verts,scale)





    def read_data(self,do_PsC=False,**kwargs):

        file_name=ia.model(do_PsC,**kwargs)
        dataf=open(file_name,"r")
        data=eval(dataf.read())
        dataf.close()
        Ts_to_mangs=lambda Ts:list(zip(*[[tf-ti for ti,tf in zip(el[:-1],el[1:])] for el in Ts]))
        Os_to_mangs=lambda Os:list(zip(*[[omg*dt for omg in omgs] for omgs in Os]))
        data["mangs"]=Ts_to_mangs(data["Ts"])
        #data.update(mangsC=Os_to_mangs(data["OsC"])
        return data

    def axes_to_verts(axes_list,ascale=(1,1,1)):
        axes=[[ax*sc for ax,sc in zip(axes,ascale)] for axes in axes_list]
        def mkvert(axes,pos=np.zeroes(3),vxs=[]):
            if axes:
                for i in [1,-1]:
                    mkvert(axes[1:],pos+i*np.array(axes[0]),vxs)
            else:
                print("yielding:",pos)
                vxs.append(tuple(pos))
            return vxs
        return [mkvert(axes) for axes in axes_list]


    def datrot(self,verts,mangs):
        data=[]
        for mang in mangs:
            data.append(verts)
            verts=[[tuple(self.rotmcc(mang,vx)) for vx in vxs] for vxs in verts]
        return np.array(data)#returns list of verts in the form of cartesian tuples



    def mkanimation(self,time=20,data=None,Vs=None,mangs=None,track_data=None,
            draw_artists=["axes"],animate=True,fps=None,save="",**kwargs):
        if "dt" not in kwargs: kwargs.update(dt=.01)
        dt=kwargs["dt"]
        save_loc="./Videos"
        verts_to_xyz=lambda verts:tuple([[vx[i] for vx in vxs] for vxs in verts] for i in range(3))
        def create_lines(verts):
            lines=[]
            xs,ys,zs=verts_to_xyz(verts)
            for i in range(len(verts)): lines.append(ax.plot(xs[i],ys[i],zs[i],"o")[0])
            return lines
        def animate_lines(num,lines):
            xs,ys,zs=verts_to_xyz(data[num])
            for i,line in enumerate(lines):
                line.set_data(xs[i],ys[i])
                line.set_3d_properties(zs[i])


        def create_polys(verts):
            create_polys=[]
            for i,el in enumerate(verts):
                poly=p3c([el],alpha=.5,zorder=0)
                poly.set_color(colors.rgb2hex([0]+[i/len(verts)*.5+.35]*2))
                create_polys.append(poly)
            return create_polys
        def animate_polys(num,polys):
            verts=data[num]
            for vxs,poly in zip(verts,polys):
                poly.set_verts([vxs])
                #poly.set_sort_zpos(0)

        def genVec(verts):#returns (xyzs=_,xyzs_=(xs_,ys_,zs_)) of prince axes
            xyzs=verts_to_xyz([verts[i] for i in [4,2,3]])
            xyzs_=[[sum(ws)/2 for ws in wss] for wss in xyzs]
            return xyzs_
        """
        def create_axes(verts):
            xyzs,xyzs_=genVec(verts)
            Vs_=zip(*[el[0] for el in Vs])
            axes=[ax.quiver(*[[0]*3]*3,*xyzs_,colors=["r"]*3,linewidth=2,arrow_length_ratio=.3,zorder=10)[0],
                  ax.quiver(*[[0]*3]*3,*Vs_,colors=["b"]*3,linewidth=2,arrow_length_ratio=.3,zorder=10)[0],
                 ]
            return axes
        def animate_axes(num,axes):
            xyzs,xyzs_=genVec(data[num])
            origin,coords_=zip(*[[0]*3]*3),zip(*xyzs_)
            Vs_=[el[num] for el in Vs]
            for axis,pos_ in zip(axes[::-1],[coords_,Vs_]):
                axis.set(segments=list(zip(origin,pos_)))
            #for axe in axes: axe.set_sort_zpos(1)
        """
        def create_axes(verts):
            xyzs_=np.array(genVec(verts))
            Vs_=np.array(list(zip(*[el[0] for el in Vs])))
            axes=[]
            if track_data: iterate=zip([Vs_],["rgb"])
            else: iterate=zip([xyzs_,Vs_],["ccc","rgb"])
            for pos_,col in iterate:
                for i in range(3):
                    pt=np.array(pos_[:,i])
                    axes.append(ax.plot(*zip(-pt,pt),col[i],linewidth=2,zorder=1,)[0])
            return axes
        def animate_axes(num,axes):
            xyzs_=np.array(genVec(data[num]))
            Vs_=np.array(list(zip(*[el[num] for el in Vs])))
            if track_data: iterate=enumerate([Vs_])
            else: iterate=enumerate([xyzs_,Vs_])
            for i,pos_ in iterate:
                for j in range(3):
                    pt=np.array(pos_[:,j])
                    axes[3*i+j].set_data(*zip(-pt[:2],pt[:2]))
                    axes[3*i+j].set_3d_properties([-pt[2],pt[2]])

        def create_diags(verts):
            diags=[]
            xyzs=np.array(verts_to_xyz([verts[i] for i in [0,2]]))
            for i in range(2): 
                for j in range(4):
                    diags.append(ax.plot(*zip([0]*3,xyzs[:,i,j]))[0])
            return diags
        def animate_diags(num,diags):
            xyzs=np.array(verts_to_xyz([verts[i] for i in [0,2]]))
            for i in range(2):
                for j in range(4):
                    diags[4*i+j].set_data(*zip([0]*2,xyzs[:2,i,j]))
                    diags[4*i+j].set_3d_properties([0,xyzs[2,i,j]])
        
        def graph_track():
            data_td=td.track_tv_data
            for i,name in enumerate(ax_p2d):
                for j in range(3):
                    ax_p2d[name].plot(data_td[j][0],[el[i] for el in data_td[j][1]],label=name+str(j)+"m")
            

        def create_p2d(data_d):
            p2d={}
            for name in list(data_d)[1:]:
                for j,col in zip(range(len(data_d[name])),"rgb"):
                    ax_p2d[name].plot(data_d["time"][j],data_d[name][j],col,label=name+str(j))
                    p2d.update({name+str(j):ax_p2d[name].plot([0,0],[0,data_d[name][j][0]],col)[0]})
                ax_p2d[name].legend()
                ax_p2d[name].set_xlabel("Time")
                ax_p2d[name].set_ylabel(name)
                ax_p2d[name].set_title("Time vs "+name)
                ax_p2d[name].grid()
            return p2d
        def animate_p2d(num,p2d):
            for name in list(data_d)[1:]:
                for j in range(len(data_d[name])):
                    p2d[name+str(j)].set_data([data_d["time"][j][num]]*2,[0,data_d[name][j][num]])

        animators=[animate_lines,animate_polys,animate_axes,animate_diags,animate_p2d]
        creators=[create_lines,create_polys,create_axes,create_diags,create_p2d]
        def animate(num,artists):
            for anifunc in animators:
                name=anifunc.__name__
                name=name[name.index("_")+1:]
                if name in list(artists): anifunc(num,artists[name])
                    
        def init_art(verts,artists):
            arts={}
            for crefunc in creators:
                name=crefunc.__name__
                name=name[name.index("_")+1:]
                if name in list(artists): 
                    if name!="p2d": arts.update({name:crefunc(verts)})
                    else: arts.update({name:crefunc(data_d)})
            if "polys" in artists:
                for poly in arts["polys"]: ax.add_collection(poly)
            return arts

        draw_p2d="p2d" in draw_artists
        if mangs==None or Vs==None or draw_p2d:
            data_model=self.read_data(do_PsC=draw_p2d,**kwargs)
        
        if draw_p2d: 
            fig=plt.figure(figsize=plt.figaspect(1/3))
            ax=fig.add_subplot(1,3,1,projection="3d")
            var_names=["Psx","Psy"]
            ax_p2d={name:fig.add_subplot(1,3,i+2) for i,name in enumerate(var_names)}
            if track_data:
                data_d=track_data
            else:
                data_d={"time":data_model["time"]*3,"Psx":data_model["PsCx"],"Psy":data_model["PsCy"]}
        else:
            fig=plt.figure()
            ax=p3.Axes3D(fig)
            data_d=None


        verts=self.verts
        if mangs==None:
            mangs=data_model["mangs"]
        if Vs==None:
            Vs=(np.array(data_model["Vs"])*.5).tolist()

        ax.set_xlim3d([-2,2]);ax.invert_xaxis()
        ax.set_ylim3d([-2,2]);ax.invert_yaxis()
        ax.set_zlim3d([-2,2])

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        ax.legend()
        ax.set_title("Rotation of Principal Axes in 3D")
        
        artists=init_art(verts,draw_artists)

        plt.tight_layout()

        print("Data reading complete. Initializing animation...")

        if not os.path.exists(save_loc):
            os.makedirs(save_loc)
        fig.savefig(save_loc+"/rotbox.png")

        if animate:
            if data==None: data=self.datrot(verts,mangs)
            data_len=len(data)
            if not fps: fps=data_len/time
            else:
                if data_len//(time*fps)==0:
                    print("fps too high.")
                    return
                def mod_data(data):
                    interval=len(data)//(time*fps)
                    if interval:
                        return [data[i] for i in range(0,len(data),interval)]
                    else: return data
                data=mod_data(data)
                data_len=len(data)
                if draw_p2d:
                    for name in list(data_d)[1:]:
                        for j in range(3):
                            data_d[name][j]=mod_data(data_d[name][j])
                    data_d["time"]=mod_data(data_d["time"])
                    for name in data_d:
                        data_d[name]=[vec+[0]*(data_len-len(vec)) for vec in data_d[name]]

                Vs=[mod_data(vec) for vec in Vs]
                Vs=[vec+[(0,0,0)]*(data_len-len(vec)) for vec in Vs]

            print("Animating...")

            poly_ani=ani.FuncAnimation(fig,animate,data_len,fargs=(artists,),interval=200)

            print("Animation complete. Saving...")

            myWriter=ani.FFMpegWriter(fps=fps)
            if save and input("Are you sure? (y/n)") not in ["y","Y"]:
                return
            poly_ani.save(save_loc+"/rotatingBox({}){}.mp4".format(dt,save),writer=myWriter)

            print("Save complete. End of program.")

def __main__():
    scale=tuple(.5/(el/max(ia.Is)+.1) for el in ia.Is)
    scale=tuple(scale[i] for i in [0,1,2])
    fps=10
    video_time,cond_time=10,1
    kwargs=dict(cond=("time",cond_time),dt=.001,Os=(.1,3,.5)) #tblock
    #kwargs=dict(cond=("time",cond_time),dt=.001,Os=(.1,16,.1))  #nasablock
    
    rb=Rot_Box(scale=scale)
    
    def proj_test():
        data=rb.read_data(**kwargs)
        Vs=data["Vs"]
        Vs2d=[[(v[:2],v[2]>=0) for v in vec] for vec in Vs]
        Vs3d_calc=[[(pp.proj_to_v3(v[0],1),v[1]) for v in vec] for vec in Vs2d]
        Vs3d_calc=[[(*v[0][:2],v[0][2]*(-1+2*v[1])) for v in vec] for vec in Vs3d_calc]
        rb.mkanimation(time=10,draw_artists=["axes"],fps=fps,**kwargs,Vs=Vs3d_calc)
        quit()
    #proj_test()
    
    track_times,Vs_exp=td.track_data_fps(fps,video_time/cond_time)
    #Vs_exp=[[tuple(v[i] for i in (1,0,2)) for v in V] for V in Vs_exp] #for nasa
    track_Psx=[[v[0] for v in V] for V in Vs_exp]
    track_Psy=[[v[1] for v in V] for V in Vs_exp]
    track_data={"time":track_times,"Psx":track_Psx,"Psy":track_Psy}
    #rb.mkanimation(time=video_time,draw_artists=["axes","p2d"],fps=fps,**kwargs)
    rb.mkanimation(time=video_time,draw_artists=["axes","p2d"],fps=fps,**kwargs,Vs=Vs_exp,track_data=track_data)

if user_exec_yes:
    __main__()



