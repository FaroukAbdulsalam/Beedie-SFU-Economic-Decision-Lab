from models import *

def close(a,b,tol=1e-6):
    return abs(a-b)<tol

def run():
    eq=equilibrium()
    assert close(eq["price"],800)
    assert close(eq["quantity"],10000)

    e=point_elasticity(800)
    assert close(e,-1.6)

    trade=trade_advantage(12,24,8,10,"Canada","Mexico")
    assert trade["comparative_board"]=="Mexico"
    assert trade["comparative_sensor"]=="Canada"

    pc=price_control(26000,20,-6000,20,"Price ceiling",600)
    assert close(pc["shortage"],8000)

    pf=price_control(26000,20,-6000,20,"Price floor",1000)
    assert close(pf["surplus"],8000)

    exp=experiment_model(500,500,20,30,120,2)
    assert exp["effect_pp"]>0

    print("All model checks passed.")

if __name__=="__main__":
    run()
