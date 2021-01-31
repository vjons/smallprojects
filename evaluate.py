import operator as op
import numpy as np
from sympy import symbols,lambdify
from sympy.core.expr import Expr

tuplefy=lambda x:x if isinstance(x,tuple) else (x,)
extend = lambda x,y: tuplefy(x)+tuplefy(y)

def to_number(expr):
    if expr.isdigit():
        return int(expr)
    x=expr.replace('.','',1)
    if x.isdigit():
        return float(expr)
    elif x[:-1].isdigit():
        return complex(expr) 
    else:
        return None
# P9G84XA

def to_func(res):
    return lambdify(res.free_symbols,res)

std_opers={"+_":op.pos,"+":op.add,"-_":op.neg,"-":op.sub,"*":op.mul,"/":op.truediv,"^":op.pow}
std_precs={"+_":(0,12),"+":(4,5),"-_":(0,13),"-":(6,7),"*":(8,9),"/":(10,11),"^":(15,14)}

def evaluate(expr,opers=std_opers,precs=std_precs,conv=to_number):
    """
    Evaluate is a function that evaluates an expression using user defined operators
    and operator precedence. Uses sympy to handle variables. 

    Parameters:
        expr: iterable[str]
            Expression to evaluate
        opers: dict[str,Function or Object], default = std_opers
            Defined functions and constants
        precs: dict[str,(Number,Number)], default = std_precs
            Defining the left and right operator precedence in evaluation.
            For unitary operators precedence right or left should be set to 0
        conv: function[str] -> Object or Bool, default = to_number
            Function that evaluates atomic expressions within expr returns False if variable

    Returns:
        sympy.core.expr.Expr|Object
            If expression contains variables an sympy.core.expr.Expr is returned else an Object

    Cases where it does not work

    - Operators can't contain other single character operators
    - Names for unitary operators should be extended with an underscore if there exists a binary operator with the same name.
    - Operators ",", ")", "(" and "," have special.
    - "a(b)" is treated as "a*b" if not a is a function but "(a)b" wont work in general to avoid ambiguity.
    - "f (b,c)" does not work as intended but f(b,c) does and evaluates the function f.
    - Space is needed between multi character operators and its operands except for single character unitary operators.
    - If the expr you want to evaluate contain names that are not defined in the "opers" argument it will be treated as variable. The evaluator then returns a sympy.core.expr.Expr object which can be converted to a lambda-function by the to_func method.
    """
    ops=opers.copy()
    ops.update({",":extend})

    if isinstance(precs,str):
        prs={k:(2*n,2*n+1) for n,k in enumerate(precs[::-1],start=1)}
    elif isinstance(precs,tuple):
        prs={k:(2,3) if precs[0]=="L" else (3,2) for k in precs[1]}
    else:
        prs=precs.copy()
    prs.update({" ":(0,0),"(":(0,1),")":(1,0),",":(1.001,1.002)})
    prs.update({k:(0,100) for k in set(ops)-set(prs) if callable(ops[k])})

    return _eval(iter(expr),ops,prs,conv,0)[0]


def _eval(it,opers,precs,conv,p_rpr):
    operator=None
    operands=()
    will={}
    pr="("
    while pr!=")":
        expr=""
        while will.pop("it",True) and (ch:=next(it,")")) not in precs:
            expr+=ch
            continue

        if expr and not expr in precs:
            value=opers.get(expr) or conv(expr) or symbols(expr)
            operands+=tuplefy(value)

        if expr in precs and expr!="(": op=expr
        elif ch.strip(): op=ch
        else: continue
        if op+"_" in opers and not operands: op+="_"
        if ch=="(":
            pr=ch
            if operands and "*" in opers: op="*"
        else:pr=op
        lpr,rpr=precs[pr]
        operator=opers.get(op,lambda x:x)
        if 0<lpr<=p_rpr: break
        if rpr:
            right,ch=_eval(it,opers,precs,conv,rpr)
            will["it"]=rpr==1
            operands+=tuplefy(right)

        operands=operator(*operands),
    return operands+(op,)

if __name__=="__main__":
    #Large test case with the precedence used by pythons eval
    t_func = lambda x,y,z:x*y**2+z
    factorial = lambda n: 1 if not n else n*factorial(n-1)
    to_array =lambda *x:np.array(x)

    opers=std_opers.copy()
    opers.update({"[":to_array,"!":factorial,"add":op.add,
                  "sin":np.sin,"cos":np.cos,"ln":np.log,"t_func":t_func,
                  "pi":np.pi,"e":np.e,"exp":np.exp})

    precs=std_precs.copy()
    precs.update({"[":(0,1),"]":(1,0),"!":(100,0),"add":(4,5)})
    #operators that are not constants and appear in operators are added to precedence with a value of (0,100)

    expr="+1.23+((+5.23*(1+2j)*4 add 4* cos(4)*t_func(cos(3)^2,2+1*sin(1.5*pi),e^2^-1)+e ^3+4+2j*6.54/ln( 3) -1.9/0.1-2))"#*(3^ 4-2 )* (((4+3)))* 1.6  - 7)-2.13^-1.34 ^-1*3"
    result=evaluate(expr,opers,precs)
    _x_=expr.replace(" ","").replace("add","+").replace("^","**").replace("pi","np.pi").replace("e","np.e").replace("ln","np.log").replace("sin","np.sin").replace("cos","np.cos")
    print(expr," = ",result,"with a difference from pythons eval of",result-eval(_x_),"\n")

    # Small example using different precedences but where functions are highest in precedence, 0 in left precedence means that it only take right operands
    # operators of length 1 can not be inside named functions or constants!
    expr="3+4*2+5+func 4 +constant*x"#x if a variable
    opers={"*":op.mul,"+":op.add,"func": lambda x:x**2,"constant":20}

    print(f"mul before add: {expr} = ",evaluate(expr,opers,"*+"))

    print(f"add before mul: {expr} = ",evaluate(expr,opers,"+*"))

    print(f"left before right: {expr} = ",evaluate(expr,opers,("L","+*")))

    print(f"right before left: {expr} = ",evaluate(expr,opers,("R","+*")))

    # In the last example you get a function by using the to_func method which can be evaluated fast later