

from qiskit import IBMQ, QuantumCircuit, execute, Aer
from qiskit.compiler import transpile, assemble
from qiskit.circuit.library import QFT
from math import pi

from matplotlib.pyplot import scatter

def lrange(k):
    return list(range(0,k))


def add_super_postion(n):
    
    def cylic(_list):
        return [_list[-1]] + _list[1:]

    lhs = QuantumCircuit(2*n , n)
    lhs = lhs.compose(QFT(n), qubits= [ _ for _ in range(n) ]) 
    
    const =  2*pi / ( 2 ** n )
    for k in range(n):
        for q in range(n, 2*n):   
            lhs.cp(const* 2**( q%n + k) , q, k)

    lhs = lhs.compose(QFT(n, inverse=True)) 
    lhs.measure(lrange(n),lrange(n))
    return lhs
    
def inputwarpper(circuit, qubitslength, classicallength , _bin):
    ret = QuantumCircuit( qubitslength, classicallength)
    for j,bit in enumerate(_bin):
        ret.reset(j)
        { '0' : lambda : ret.initialize([1,0], j),
         '1' : lambda : ret.initialize([0,1], j) }[bit]()
    return ret.compose( circuit )


def job_resulthandle(job, circuit):
    result = job.result()
    counts = result.get_counts(circuit)
    # print("\nTotal count for 00 and 11 are:",counts)
    return counts 
    # print(counts)

def simulate_overPc(circuit):
    job = execute(circuit, Aer.get_backend('qasm_simulator'), shots=4000)
    return job_resulthandle(job, circuit)
    
def simulate_overIBM(circuit):

    IBMQ.load_account() 
    provider = IBMQ.get_provider(hub='ibm-q')
    print(provider.backends())
    backend = provider.get_backend('ibmq_quito')
    job = execute(circuit, backend, shots=1000)
    job_resulthandle(job, circuit)

if __name__ == "__main__":

    circuit = add_super_postion(5)    
    print(circuit.draw())

    def convert_to_bin(x):

        def _convert_to_bin(y):            
            return bin(y)[2:][::-1]

        _str = _convert_to_bin(x)
        
        _str += (5 - len(_str)) * "0"
        return _str

    success = [[], [] ]
    fails = [[] , [] ]

    for i in range( 10 ):
        for j in range( 3,4 ):
            counts = simulate_overPc(inputwarpper( circuit, 10, 5, convert_to_bin(i) + convert_to_bin(j) )) 
            print(convert_to_bin(i) + convert_to_bin(j))
            expected = convert_to_bin(i+j)[::-1]
            print(" expected : {0} + {1} = {2} ({3}) ".format(i,j,i+j, expected))
            print( "got {0}".format(counts))
            _max =   max(counts, key=counts.get)
            print( "max {0}".format( _max ))
            if _max == expected: 
                success[0].append(i)
                success[1].append(j)
            else :
                fails[0].append(i)
                fails[1].append(j)
    
    import matplotlib.pyplot as plt 
    plt.scatter( success[0], success[1] )
    plt.scatter( fails[0], fails[1] )
    plt.show()


    print(circuit.draw())
    (circuit)
    
    
