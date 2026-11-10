"""Independent algebra check of legacy Ring -> native FFA fields.

This integration analysis implements the documented equations independently;
it does not execute OPALX kernels or form a native unit-test dependency.
"""
from pathlib import Path
import json, math
import numpy as np

ORDER=4

def mul(a,b): return np.convolve(a,b)[:ORDER+1]

def enge(x, lam, coeffs):
    # Taylor series in epsilon, with coefficients derivative/n!.
    q=np.zeros(ORDER+1); q[0]=x/lam; q[1]=1/lam
    power=np.zeros(ORDER+1);power[0]=1
    polynomial=np.zeros(ORDER+1)
    for coefficient in coeffs:
        polynomial += coefficient*power
        power=mul(power,q)
    exponential=np.zeros(ORDER+1);exponential[0]=math.exp(polynomial[0])
    for n in range(1,ORDER+1):
        exponential[n]=sum(k*polynomial[k]*exponential[n-k] for k in range(1,n+1))/n
    denominator=exponential.copy();denominator[0]+=1
    inverse=np.zeros(ORDER+1);inverse[0]=1/denominator[0]
    for n in range(1,ORDER+1):
        inverse[n]=-sum(denominator[k]*inverse[n-k] for k in range(1,n+1))/denominator[0]
    return inverse*np.array([math.factorial(n) for n in range(ORDER+1)])

def profile(x, data, native=False):
    xs,xe,ls,le,cs,ce=data
    sign=-1 if native else 1
    start=enge(sign*x-xs,ls,cs)
    end=enge(-sign*x-xe,le,ce)
    derivatives=start*np.array([sign**n for n in range(ORDER+1)])+end*np.array([(-sign)**n for n in range(ORDER+1)])
    derivatives[0]-=1
    return derivatives

def coefficients(k,tan):
    df=np.zeros((ORDER+1,ORDER+1));df[0,0]=1
    for n in range(0,ORDER,2):
        for i in range(n+1):df[n+1,i+1]=df[n,i]/(n+1)
        if n+1==ORDER:break
        for i in range(n+1):df[n+2,i]=-(k-n)**2*df[n,i]/((n+1)*(n+2))
        for i in range(n+2):
            df[n+2,i]+=2*(k-n)*tan*df[n+1,i]/(n+2)
            df[n+2,i+1]-=(1+tan*tan)*df[n+1,i]/(n+2)
    return df

def cylindrical(r,z,xi,R,k,tan,B0,fringe,native=False):
    derivatives=profile(xi,fringe,native)
    df=coefficients(k,tan);field=np.zeros(3);h=(r/R)**k*B0
    for n in range(0,ORDER+1,2):
        f_even=df[n]@derivatives
        field[1]+=f_even*h*(z/r)**n
        if ORDER>=n+1:
            f_odd=df[n+1]@derivatives
            field[0]+=(f_even*(k-n)/(n+1)-tan*f_odd)*h*(z/r)**(n+1)
            field[2]+=f_odd*h*(z/r)**(n+1)
    return field

def cartesian(cyl,phi):
    br,by,bphi=cyl
    return np.array([br*math.cos(phi)-bphi*math.sin(phi),by,br*math.sin(phi)+bphi*math.cos(phi)])

def old_field(position,R,a,start,L,k,tan,B0,fringe):
    # Literal RingSection operations: translate, rotate by -startF, cycle axes.
    start_position=np.array([R*math.sin(a),R*math.cos(a),0.])
    delta=position-start_position
    old_rotation=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    cycl=old_rotation@delta
    local=np.array([cycl[1],cycl[2],cycl[0]])
    q=local+np.array([R,0,0]);r=math.hypot(q[0],q[2]);phi=math.atan2(q[2],q[0])
    xi=phi-tan*math.log(r/R)-(start+L/8)/R
    local_B=cartesian(cylindrical(r,q[1],xi,R,k,tan,B0,fringe),phi)
    cycl_B=np.array([local_B[2],local_B[0],local_B[1]])
    return old_rotation.T@cycl_B

def native_field(position,R,a,start,L,k,tan,B0,fringe,reverse_spiral=True):
    template_phi=a+(start-3*L/8)/R
    entrance_phi=math.pi/2-(template_phi+L/R)
    entrance=np.array([R*math.cos(entrance_phi)-R,0,R*math.sin(entrance_phi)])
    rotation=np.array([[math.cos(entrance_phi),0,math.sin(entrance_phi)],[0,1,0],[-math.sin(entrance_phi),0,math.cos(entrance_phi)]])
    local=rotation@(position-entrance)
    q=local+np.array([R,0,0]);r=math.hypot(q[0],q[2]);phi=math.atan2(q[2],q[0])
    native_tan=-tan if reverse_spiral else tan
    xi=phi-native_tan*math.log(r/R)-L/(2*R)
    local_B=cartesian(cylindrical(r,q[1],xi,R,k,native_tan,-B0,fringe,native=True),phi)
    return rotation.T@local_B


def main():
    R=4.42;L=4.5*math.pi/180*R;start=14.23*math.pi/180*R
    k=7.717022064259446;tan=math.tan(3.142/4);B0=-.6532097983351404
    school=(L/(2*R),L/(2*R),.12/R,.12/R,[-1.3,3.42,-1.2,.23],[-1.3,3.42,-1.2,.23])
    asymmetric=(.4*L/R,.6*L/R,.11/R,.15/R,[-1.3,3.42,-1.2,.23],[-.2,2.8,.3,.04])
    errors=[];negative=[]
    for name,fringe in [('school',school),('asymmetric_control',asymmetric)]:
        local_errors=[]
        for a in [math.radians(-6),math.radians(29),math.radians(230)]:
            centre=math.pi/2-a-(start+L/8)/R
            for relative_radius in [.99,1.,1.01]:
                r=R*relative_radius
                for angular_offset in [-.05,-.02,0,.02,.05]:
                    theta=centre+angular_offset
                    for z in [-.005,-.001,0,.001,.005]:
                        old_position=np.array([r*math.cos(theta),r*math.sin(theta),z])
                        native_position=np.array([old_position[0]-R,z,old_position[1]])
                        old_B=old_field(old_position,R,a,start,L,k,tan,B0,fringe)
                        # Magnetic field is axial under the x,y,z -> x,z,y reflection.
                        expected=-old_B[[0,2,1]]
                        actual=native_field(native_position,R,a,start,L,k,tan,B0,fringe)
                        wrong=native_field(native_position,R,a,start,L,k,tan,B0,fringe,False)
                        error=float(np.max(np.abs(actual-expected)))
                        local_errors.append(error);negative.append(float(np.max(np.abs(wrong-expected))))
        errors.append(dict(profile=name,samples=len(local_errors),max_absolute_field_error_T=max(local_errors)))
    result=dict(method='independent scalar equations and literal frame matrices; not a call to native kernels',profiles=errors,total_samples=sum(x['samples'] for x in errors),negative_control_without_spiral_flip_max_error_T=max(negative),expected_axial_mapping='B_native=-B_old[[x,z,y]]',start_end_parameter_policy='unchanged: current native AsymmetricEnge already mirrors the old scalar function')
    assert max(x['max_absolute_field_error_T'] for x in errors)<5e-12
    assert max(negative)>.01
    (Path(__file__).with_suffix('.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
