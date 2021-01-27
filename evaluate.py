import operator as op
import numpy as np

tuplefy=lambda x:x if isinstance(x,tuple) else (x,)
identity=lambda x:x

def evaluate(it,opers,prs,p_rpr=0):
    if not p_rpr:
        prs.update({" ":(0,0),"(":(0,1),")":(1,0),",":(1.1,1.2),"\n":(1,0)})
    it=iter(it)
    operator=None
    operands=()
    will={}
    pr="("
    while pr!=")":
        expr=""
        while will.pop("it",True) and (ch:=next(it,")")) not in prs:
            expr+=ch
            continue

        if expr and not expr in prs:
            operands+=tuplefy(opers.get(expr) or eval(expr))

        if expr in prs and any(prs[expr]): op=expr
        elif any(prs[ch]): op=ch
        else: continue

        if op+"_" in opers and not operands: op+="_"

        if ch=="(":
            pr=ch
            if operands: op="*"
        else: pr=op
        lpr,rpr=prs[pr]
        operator=opers.get(op,identity)
        if 0<lpr<=p_rpr: break
        if rpr:
            right,ch=evaluate(it,opers,prs,rpr)
            will["it"]=rpr==1
            operands+=tuplefy(right)
        
        operands=operator(*operands),
    return operands+(op,) if p_rpr else operands[0]

if __name__=="__main__":
    #Large case with the precedence used by pythons eval
    t_func = lambda x,y,z:x*y**2+z
    factorial = lambda n: 1 if not n else n*factorial(n-1)
    to_array =lambda *x:np.array(x)
    extend = lambda x,y: tuplefy(x)+tuplefy(y)

    operators={"[":to_array,          ",":extend,"!":factorial,
          "+_":op.pos,"+":op.add,"-_":op.neg,"-":op.sub,
          "*":op.mul,"/":op.truediv,"^":op.pow,"add":op.add,
          "sin":np.sin,"cos":np.cos,"ln":np.log,"t_func":t_func,
          "pi":np.pi,"e":np.e}

    precedence={"[":(0,1),"]":(1,0),"!":(16,0),
                "+_":(0,12),"+":(4,5),"-_":(0,13),"-":(6,7),
                "*":(8,9),"/":(10,11),"^":(15,14),"add":(4,5),
                "sin":(0,16),"cos":(0,16),"ln":(0,16),"t_func":(0,16)}

    expr="+1.23+((+5.23*(1+2j)*4 add 4* cos(4)*t_func(cos(3),2+1*sin(1.5*pi),e^2^-1)+e ^3 +7.26+2j*6.54/ln( 3) -1.9/0.1-2)*(3^ 4-2 )* (((4+3)))* 1.6  - 7)-2.13^-1.34 ^-1*3"
    result=evaluate(expr,operators,precedence)
    x=expr.replace(" ","").replace("add","+").replace("^","**").replace("pi","np.pi").replace("e","np.e").replace("ln","np.log").replace("sin","np.sin").replace("cos","np.cos")
    print(expr," = ",result,"with a difference from pythons eval of",result-eval(x),"\n")

    #Small example using different precedences but where functions are highest in precedence, 0 in left precedence means that it only take right operands
    #operators of length 1 can not be inside named functions or constants!
    expr="3+4*2+5+func 4 + constant"
    opers={"*":op.mul,"+":op.add,"func": lambda x:x**2,"constant":20}

    print(f"mul before add: {expr} = ",evaluate(expr,opers,prs={"+":(2,3),"*":(4,5),"func":(0,6)}))

    print(f"add before mul: {expr} = ",evaluate(expr,opers,prs={"*":(2,3),"+":(4,5),"func":(0,6)}))

    print(f"left before right: {expr} = ",evaluate(expr,opers,prs={"*":(2,3),"+":(2,3),"func":(0,6)}))

    print(f"right before left: {expr} = ",evaluate(expr,opers,prs={"*":(3,2),"+":(3,2),"func":(0,6)}))