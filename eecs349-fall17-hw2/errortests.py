import io, sys, os
import csv
import numpy as np
import matplotlib.pyplot as plt
import time


# Function that calculates the error rate for a set of typos, truewords, and dictionary words by comparing
# whether the corrected typo (calculated using the spell_check function) matches the corresponding true word.
# The function also tracks the time it takes to measure the error for all of the data.
def measure_error(typos, truewords, dictionarywords):
	start = time.time()
	if len(typos) == 0: # Check to make sure that we actually have data
		return 0
	error_count = 0
	# Go through list of typos and find the closest word in the dictionary, then compare to the trueword at that index
	for i in range(len(typos)):
		if i % 50 == 0:
			print "testing word number %d" % i
		corrected_word = find_closest_word(typos[i], dictionarywords)
		# Increment error count if the corrected word is different than the true word
		if corrected_word != truewords[i]:
			error_count += 1
	# Compute the error rate
	error_rate = float(error_count) / float(len(typos))
	print "time elapsed = %.1f seconds" % (time.time() - start)
	print "error rate is: %f" % error_rate
	return error_rate

# Function to compute the Levenshtein distance between two strings using the Manhattan distance (distance in rows + distance in columns) between two keys as the substitution cost
# After determining the substitution cost, it repeats the same code found in the levenshtein_distance function
def qwerty_levenshtein_distance(string1, string2, deletion_cost, insertion_cost):
	# Initialize matrix
	# '.' is used as a placeholder in the 3rd and 4th rows so that the matrix is a square (4x10)
	qwerty_matrix = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
					 ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'], 
					 ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', '.'], 
					 ['z', 'x', 'c', 'v', 'b', 'n', 'm', '.', '.', '.']]
	substitution_cost = 1
	### Levenshtein distance algorithm
	distance = 0
	# Initialize the distance matrix
	m = len(string1) + 1
	n = len(string2) + 1
	M = np.zeros((m, n))
	for i in range(m):
		M[i,0] = i * deletion_cost # distance of any 1st string to an empty 2nd string
	for j in range(n):
		M[0,j] = j * insertion_cost # distance of any 2nd string to an empty 1st string
	# Go through matrix and calculate distances
	for j in range(1, n):
		for i in range(1, m):
			if string1[i-1].lower() == string2[j-1].lower():
				M[i,j] = M[i-1, j-1] # no operation cost, because they match
			else:
				substitution_cost = qwerty_Manhattan_distance(qwerty_matrix, string1[i-1].lower(), string2[j-1].lower())
				M[i,j] = min(M[i-1,j] + deletion_cost, M[i, j-1] + insertion_cost, M[i-1,j-1] + substitution_cost)
	distance = M[m-1,n-1]
	return distance

# Function to compute the Manhattan distance between two letters. Called by qwerty_levenshtein_distance
def qwerty_Manhattan_distance(qwerty_matrix, letter1, letter2):
	# Non alpha-numeric characters should be considered as word delimiters so we don't need to worry about that
	letter1_row = -1
	letter1_col = -1
	letter2_row = -1
	letter2_col = -1
	# Find letter positions
	# First find the row
	for i in range(len(qwerty_matrix)):
		if letter1 in qwerty_matrix[i]:
			letter1_row = i
			# Then find the column
			for j in range(len(qwerty_matrix[i])):
				if qwerty_matrix[i][j] == letter1:
					letter1_col = j
					break
		if letter2 in qwerty_matrix[i]:
			letter2_row = i
			# Then find the column
			for j in range(len(qwerty_matrix[i])):
				if qwerty_matrix[i][j] == letter2:
					letter2_col = j
					break
	# Calculate the distance
	row_dist = abs(letter1_row - letter2_row)
	col_dist = abs(letter1_col - letter2_col)
	return row_dist + col_dist

# Function that finds the closest word in a dictionary to a given input string. Calls the function to calculate Levenshtein distance
# Modified slightly from find_closest_word function above to include inputs for insertion, deletion, and substitution costs
def experiment_find_closest_word(string1, dictionary, insertion_cost, deletion_cost, substitution_cost):
	# Initialize cost variables
	closest_word = ""
	# Initialize min distance
	min_distance = levenshtein_distance(string1, dictionary[0][0], deletion_cost, insertion_cost, substitution_cost)
	# Go through each word in dicationary and calculate the distance, checking to see if it's smaller than the current smallest distance
	for dict_word in dictionary:
		curr_distance = levenshtein_distance(string1, dict_word[0], deletion_cost, insertion_cost, substitution_cost)
		if curr_distance == 0: # we found a perfect match
			return dict_word[0]
		elif curr_distance < min_distance:
			min_distance = curr_distance
			closest_word = dict_word[0]
	return closest_word

# Function that finds the closest word in a dictionary to a given input string. Calls the function to calculate Levenshtein distance
# Modified slightly from find_closest_word function above to include inputs for insertion and deletion costs.
# The substitution cost in this function is the manhattan distance.
def experiment_find_closest_word_querty(string1, dictionary, insertion_cost, deletion_cost):
	# Initialize cost variables
	closest_word = ""
	# Initialize min distance
	min_distance = qwerty_levenshtein_distance(string1, dictionary[0][0], deletion_cost, insertion_cost)
	# Go through each word in dicationary and calculate the distance, checking to see if it's smaller than the current smallest distance
	for dict_word in dictionary:
		curr_distance = qwerty_levenshtein_distance(string1, dict_word[0], deletion_cost, insertion_cost)
		if curr_distance == 0: # we found a perfect match
			return dict_word[0]
		elif curr_distance < min_distance:
			min_distance = curr_distance
			closest_word = dict_word[0]
	return closest_word

# Function that calculates the error rate for a set of typos, truewords, and dictionary words by comparing
# whether the corrected typo (calculated using the spell_check function) matches the corresponding true word.
# The function also tracks the time it takes to measure the error for all of the data.
# This is modified from the measure_error function above to go through a set of possible paramters, testing to find which has the lowest error rate.
def measure_error_experiment(typos, truewords, dictionarywords):
	results = []
	values = [0,1,2,4]
	for insertion in values:
		for deletion in values:
			for substitution in values:
				print "checking permutation: insertion = %d, deletion = %d, substitution = %d" % (insertion, deletion, substitution)
				curr_result = [[insertion, deletion, substitution]]
				start = time.time()
				if len(typos) == 0: # Check to make sure that we actually have data
					return 0
				error_count = 0
				# Go through list of typos and find the closest word in the dictionary, then compare to the trueword at that index
				for i in range(len(typos)):
					corrected_word = experiment_find_closest_word(typos[i], dictionarywords, insertion, deletion, substitution)
					# Increment error count if the corrected word is different than the true word
					if corrected_word != truewords[i]:
						error_count += 1
				# Compute the error rate
				error_rate = float(error_count) / float(len(typos))
				curr_result.append(error_rate)
				print "time elapsed = %.1f seconds" % (time.time() - start)
				print "error rate is: %f" % error_rate
				results.append(curr_result)
	return results

# Function that calculates the error rate for a set of typos, truewords, and dictionary words by comparing
# whether the corrected typo (calculated using the spell_check function) matches the corresponding true word.
# The function also tracks the time it takes to measure the error for all of the data.
# This is modified from the measure_error function above to go through a set of possible paramters, testing to find which has the lowest error rate.
# The substitution cost in this function is the manhattan distance
def measure_error_experiment_querty(typos, truewords, dictionarywords):
	results = []
	values = [1,2,4]
	for insertion in values:
		for deletion in values:
			print "checking permutation: insertion = %d, deletion = %d" % (insertion, deletion)
			curr_result = [[insertion, deletion]]
			start = time.time()
			if len(typos) == 0: # Check to make sure that we actually have data
				return 0
			error_count = 0
			# Go through list of typos and find the closest word in the dictionary, then compare to the trueword at that index
			for i in range(len(typos)):
				corrected_word = experiment_find_closest_word_querty(typos[i], dictionarywords, insertion, deletion)
				# Increment error count if the corrected word is different than the true word
				if corrected_word != truewords[i]:
					error_count += 1
			# Compute the error rate
			error_rate = float(error_count) / float(len(typos))
			curr_result.append(error_rate)
			print "time elapsed = %.1f seconds" % (time.time() - start)
			print "error rate is: %f" % error_rate
			results.append(curr_result)
	return results

