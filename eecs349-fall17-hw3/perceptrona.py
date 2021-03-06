import sys
import csv
import numpy as np
import scipy

def perceptrona(w_init, X, Y):
#	Perceptrona implementation of the sequential perceptron algorithm.
#   perceptrona(w_init, X, Y) finds and returns the weights w of the linearly discriminating
#	weight vector that correctly assigns X to class 1 or -1. The function also returns k, the 
#	number of iterations the algorthm took to converge.
#
#	The input w_init is a vector (in numpy) of length 2 containing the coefficients of the weight vector initialized to 0, such that w_init = <0, 0>
#   The output w is a vector (in numpy) of length 2 containing the coefficients of the weight vector w = <w0, w1>
#   X and Y are vectors of datapoints specifying  input (X) and output (Y)
#   of the function to be learned. Class support for inputs X,Y: float, double, single
#	X is a univatiate attribute vector
#
# 	To classify a given X example, take the dot product of the transform of w and <1, X>.
# 	If the output is positive, the example is classified as 1, otherwise it is classified as -1.
#
#   The algorithm iterates through all of the examples in X and classifies each example.
#	If the classification of any example does not match the output Y for that example, 
#	the algorithm is not converged and the weight vector is updated.
#	The algorithm terminates when it converges (all examples are correctly classified) or when it has iterated 10000 times 
#	(in which case the data is said to be not linearly separable)
#
#   AUTHOR: Adam Greenstein (ajg362)
#
	#figure out (w, k) and return them here. w is the vector of weights, k is how many iterations it took to converge.
	newX = []
	# Prepend the value 1 before each X value so that the example is in the form <1, X[i]>
	for value in X:
		curr = [1]
		curr.append(value)
		newX.append(curr)
	X = np.array(newX)
	w = w_init
	max_iter = 10000
	k = 0
	converged = False
	while converged == False and k < max_iter:
		k += 1
		converged = True
		for i in range(len(X)):
			g = np.dot(w.T, X[i]) # Classify the example
			classification = -1
			if g >= 0:
				classification = 1
			if classification != Y[i]: # Check if the classification matches the y value
				converged = False
				w = w + (X[i]*Y[i]) # Update the weights
	if k >= max_iter:
		print "The data is not linearly separable"
		return False
	else:
		print (w,k)
		return (w, k)


def main():
# 	The function can be called from the command line as follows:
#	python perceptrona.py <csvfile>
	rfile = sys.argv[1]
	
	#read in csv file into np.arrays X1, X2, Y1, Y2
	csvfile = open(rfile, 'rb')
	dat = csv.reader(csvfile, delimiter=',')
	X1 = []
	Y1 = []
	X2 = []
	Y2 = []
	for i, row in enumerate(dat):
		if i > 0:
			X1.append(float(row[0]))
			X2.append(float(row[1]))
			Y1.append(float(row[2]))
			Y2.append(float(row[3]))
	X1 = np.array(X1)
	X2 = np.array(X2)
	Y1 = np.array(Y1)
	Y2 = np.array(Y2)
	w_init = np.zeros(2) # Initialize the weights to zeros
	perceptrona(w_init, X1, Y1)
	perceptrona(w_init, X2, Y2)

if __name__ == "__main__":
	main()
