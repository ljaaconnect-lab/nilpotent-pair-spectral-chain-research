from fractions import Fraction

class DAG:
    def __init__(self):
        self.nodes=[]
        self.gates=0
    def emit(self,op,*args):
        self.nodes.append((op,*args))
        self.gates += op in ('add','mul')
        return len(self.nodes)-1
    def inp(self,name): return self.emit('input',name)
    def const(self,x): return self.emit('const',Fraction(x))
    def add(self,a,b): return self.emit('add',a,b)
    def mul(self,a,b): return self.emit('mul',a,b)
    def sub(self,a,b): return self.add(a,self.mul(self.const(-1),b))
    def evaluate(self,output,inputs,prime):
        values=[]
        for node in self.nodes:
            op,*args=node
            if op=='input': value=inputs[args[0]] % prime
            elif op=='const': value=args[0].numerator*pow(args[0].denominator,-1,prime)%prime
            elif op=='add': value=(values[args[0]]+values[args[1]])%prime
            elif op=='mul': value=values[args[0]]*values[args[1]]%prime
            else: raise ValueError(op)
            values.append(value)
        return values[output]

def marked_inputs(n,dag):
    p=[[dag.inp(('p',i,j)) for j in range(n)] for i in range(n)]
    powers=[dag.inp('z')]
    for _ in range(n*n-1): powers.append(dag.mul(powers[-1],powers[-1]))
    return [[dag.mul(p[i][j],powers[i*n+j]) for j in range(n)] for i in range(n)]
