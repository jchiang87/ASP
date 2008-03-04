import numarray as num
import copy

def gammln(xx):
    cofs = (76.18009172947146, -86.50532032941677,
            24.01409824083091, -1.231739572450155,
            0.1208650973866179e-2, -0.5395239384953e-5)
    x = copy.copy(xx)
    y = copy.copy(xx)
    tmp = x + 5.5
    tmp -= (x + 0.5)*num.log(tmp)
    ser = 1.000000000190015
    for cof in cofs:
        y += 1.
        ser += cof/y
    return -tmp + num.log(2.5066282746310005*ser/x)

if __name__ == '__main__':
    fact = 1
    for i in range(1, 10):
        fact *= i
        print i, gammln(i+1.), num.log(fact)

    x = num.arange(2, 11)
    y = gammln(x)
    print y
    
