import operator as op
import numpy as np
from sympy import symbols,lambdify
from sympy.core.expr import Expr

tuplefy=lambda x:x if isinstance(x,tuple) else (x,)

def to_number(expr):
    x=expr.replace('.','',1)
    if x.isdigit():
        return float(expr)
    elif x[:-1].isdigit():
        return complex(expr) 
    else:
        return False

def to_func(res):
    return lambdify(res.free_symbols,res)

def evaluate(it,opers,prs,p_rpr=0,**variables):
    if not p_rpr:
        prs.update({" ":(0,0),"(":(0,1),")":(1,0),",":(1.5,1.6),"\n":(1,0)})
        prs.update({k:(0,100) for k in set(opers)-set(prs) if callable(opers[k])})
    it=iter(it)
    operator=None
    operands=()
    will={}
    kw={}
    pr="("
    while pr!=")":
        expr=""
        while will.pop("it",True) and (ch:=next(it,")")) not in prs:
            expr+=ch
            continue

        if expr and not expr in prs:
            value=variables.get(expr) or opers.get(expr) or to_number(expr) or symbols(expr)
            operands+=tuplefy(value)

        if expr in prs and any(prs[expr]): op=expr
        elif any(prs[ch]): op=ch
        else: continue

        if op+"_" in opers and not operands: op+="_"

        if ch=="(":
            pr=ch
            if operands and "*" in opers: op="*"
        else: pr=op
        lpr,rpr=prs[pr]
        operator=opers.get(op,lambda x:x)
        if 0<lpr<=p_rpr: break
        if rpr:
            right,ch=evaluate(it,opers,prs,rpr,**variables)
            will["it"]=rpr==1
            operands+=tuplefy(right)

        operands=operator(*operands,**kw),
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
          "pi":np.pi,"e":np.e,"exp":np.exp}

    precedence={"[":(0,1),"]":(1,0),"!":(16,0),
                "+_":(0,12),"+":(4,5),"-_":(0,13),"-":(6,7),
                "*":(8,9),"/":(10,11),"^":(15,14),"add":(4,5)}

    #operators that are not constants and appear in operators are added to precedence with a value of (0,100)

    expr="+1.23+((+5.23*(1+2j)*4 add 4* cos(4)*t_func(cos(3),2+1*sin(1.5*pi),e^2^-1)+e ^3 +7.26+2j*6.54/ln( 3) -1.9/0.1-2)*(3^ 4-2 )* (((4+3)))* 1.6  - 7)-2.13^-1.34 ^-1*3"
    result=evaluate(expr,operators,precedence)
    x=expr.replace(" ","").replace("add","+").replace("^","**").replace("pi","np.pi").replace("e","np.e").replace("ln","np.log").replace("sin","np.sin").replace("cos","np.cos")
    print(expr," = ",result,"with a difference from pythons eval of",result-eval(x),"\n")

    #Small example using different precedences but where functions are highest in precedence, 0 in left precedence means that it only take right operands
    #operators of length 1 can not be inside named functions or constants!
    expr="3+4*2+5+func 4 + c+x"#x if a variable
    opers={"*":op.mul,"+":op.add,"func": lambda x:x**2,"c":20}

    print(f"mul before add: {expr} = ",evaluate(expr,opers,x=4,prs={"+":(2,3),"*":(4,5)}))

    print(f"add before mul: {expr} = ",evaluate(expr,opers,x=5,prs={"*":(2,3),"+":(4,5)}))

    print(f"left before right: {expr} = ",evaluate(expr,opers,x=6,prs={"*":(2,3),"+":(2,3)}))

    print(f"right before left: {expr} = ",evaluate(expr,opers,prs={"*":(3,2),"+":(3,2)}))

    #In the last example you get a function by using the to_func method which can be evaluated fast later