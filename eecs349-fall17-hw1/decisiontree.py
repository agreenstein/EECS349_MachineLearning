import io, sys, os
import csv
import math
import random


def main():
	if len(sys.argv) != 5:
		print "Command should follow format: python decisiontree.py <inputFileName> <trainingSetSize> <numberOfTrials> <verbose>"
		sys.exit(1)
	inputFileName = sys.argv[1]
	trainingSetSize = int(sys.argv[2])
	numberOfTrials = int(sys.argv[3])
	verbose = int(sys.argv[4])

	# Read the data and get the attributes and examples
	examples = read_data(inputFileName)
	attribute_names = examples[0]
	examples = examples[1:len(examples)]
	attribute_indices = range(len(attribute_names) - 1)
	class_idx = len(attribute_names) - 1

	# Create decision trees, classify data, and print output numberOfTrials times
	ID3_results = []
	PP_results = []
	for trialNumber in range(numberOfTrials):
		print "\n" + "--------------------"
		print "Trial number %d" % trialNumber
		print "--------------------"
		# Split the examples into training and test data
		rand_indices = random.sample(xrange(len(examples)), trainingSetSize)
		training_examples = []
		test_examples = []
		for idx in rand_indices:
			training_examples.append(examples[idx])
		for i in range(len(examples)):
			if i not in rand_indices:
				test_examples.append(examples[i])

		# Generate the ID3 decision tree from the training data
		mode = Mode(training_examples, len(attribute_names) - 1)
		decision_tree = ID3Tree()
		decision_tree = ID3(training_examples, attribute_indices, mode, class_idx, mode)
		print_tree(decision_tree, attribute_names, None, 0, None)
		# Now that we have the tree, use it to classify the test data
		# Also classify the data using prior probability -> because data is binary, just assign all examples the most common classification (i.e., the mode)
		# But rather than actually classifying, we can just see whether the mode matches the actual classification for each example and count the number that match
		classified_examples = []
		correct_classifications_ID3 = 0
		correct_classifications_PP = 0
		if len(test_examples) == 0:
			p_correct_ID3 = 0
			p_correct_PP = 0
			print "There are no testing examples."
		else:
			for test_ex in test_examples:
				# classify using ID3
				classified_ex = test_ex
				ID3_classification = classify_testingData(decision_tree, test_ex)
				# See if we got the classification correct
				if ID3_classification == test_ex[class_idx]:
					correct_classifications_ID3 += 1
				classified_ex.append(ID3_classification)
				# classify using prior probability
				if mode == test_ex[class_idx]:
					correct_classifications_PP += 1
				classified_ex.append(mode)
				classified_examples.append(classified_ex)
			p_correct_ID3 = float(correct_classifications_ID3) / float(len(test_examples))
			ID3_results.append(p_correct_ID3)
			p_correct_PP = float(correct_classifications_PP) / float(len(test_examples))
			PP_results.append(p_correct_PP)
		# Print out the output
		if verbose == 1:
			print_verbose(attribute_names, training_examples, classified_examples)
		print "\n" + "Performance:"
		print "	Percent of test cases correctly classified using prior probability = %.0f%%" % (100 * p_correct_PP)
		print "	Percent of test cases correctly classified by a decision tree built with ID3 = %.0f%%" % (100 * p_correct_ID3)
	
	testingSetSize = len(examples) - trainingSetSize
	summary_output(inputFileName, trainingSetSize, testingSetSize, numberOfTrials, ID3_results, PP_results)

#### Class used to represent ID3 tree
# We are only creating a binary tree learner, so any tree/subtree will only need information on the attribute it represents and it's true/false children
class ID3Tree:
	def __init__(self):
		# attribute field is stored as an index number used to access the attribute name from the attributes array
		self.attribute = None
		self.trueChild = None
		self.falseChild = None

############ Helper functions ############
# Function that reads the input file and converts "true/false" strings to booleans
def read_data(inputFile):
	f = open(inputFile, 'r')
	examples = []
	# Create the reader object
	reader = csv.reader(f, delimiter='	')
	for row in reader:
		temp_row = row
		for i in range(len(temp_row)):
			# Convert strings "true" and "false" to booleans True and False
			if "rue" in temp_row[i]: # Assuming that all of the data will be entered as 'true', but only check for 'rue' just in case the 't' is capitalized
				temp_row[i] = True
			elif "alse" in temp_row[i]: # Same idea for false
				temp_row[i] = False
		examples.append(temp_row)
	return examples

# Function to find the most common example
def Mode(examples, class_idx):
	true_count = 0
	for example in examples:
		if example[class_idx] == True:
			true_count += 1
	false_count = len(examples) - true_count
	if true_count >= false_count:
		return True
	else:
		return False

# Implementation of ID3 algorithm
def ID3(examples, attribute_indices, default, class_idx, mode):
	if len(examples) == 0:
		return default
	# Go through examples to see if all examples have the same classification
	same_class = True
	start_class = examples[0][class_idx]
	for example in examples:
		if example[class_idx] != start_class:
			same_class = False
			break
	# If all examples have the same class, then return that class
	if same_class:
		return start_class
	# Else if attributes list is empty, then return most common classification
	elif len(attribute_indices) == 0:
		return mode
	# Otherwise, choose an attribute to split on and recursively call ID3
	else:
		best_attribute = choose_attribute(examples, attribute_indices, class_idx)
		tree = ID3Tree()
		tree.attribute = best_attribute
		# best_attribute only has values of true or false, so don't need to loop through all possible values
		# Just split into true examples and false examples
		true_examples = []
		false_examples = []
		for example in examples:
			if example[best_attribute] == True:
				true_examples.append(example)
			else:
				false_examples.append(example)
		# Remove the current attribute from the attributes list by creating a new attribute list that doesn't include it
		new_attributes = []
		for i in range(len(attribute_indices)):
			if attribute_indices[i] != best_attribute:
				new_attributes.append(attribute_indices[i])
		# Create true and false subtrees
		tree.trueChild = ID3(true_examples, new_attributes, mode, class_idx, mode)
		tree.falseChild = ID3(false_examples, new_attributes, mode, class_idx, mode)
		return tree

# Function used to classify an example using a decision tree that was generated from training data
def classify_testingData(ID3Tree, example):
	classification = None
	if ID3Tree == True or ID3Tree == False:
		return ID3Tree
	attribute = ID3Tree.attribute
	trueChild = ID3Tree.trueChild
	falseChild = ID3Tree.falseChild
	if example[attribute] == True:
		# go down the true branch
		if trueChild == True or trueChild == False:
			# we are at a leaf, so return the value
			classification = trueChild
		else:
			# we need to split again on the child attribute
			classification = classify_testingData(trueChild, example)
	else:
		# go down the false branch
		if falseChild == True or falseChild == False:
			# we are at a leaf, so return the value
			classification = falseChild
		else:
			# we need to split again on the child attribute
			classification = classify_testingData(falseChild, example)
	return classification

# Function to calculate entropy
def calculate_entropy(examples, class_idx):
	entropy = 0
	true_count = 0
	# If there are no examples, return 0
	if len(examples) == 0:
		return 0
	# attributes are only either true or false (this is a binary decision tree) so just need to count the number of true examples
	for example in examples:
		if example[class_idx] == True:
			true_count += 1
	p_true = float(true_count) / float(len(examples))
	p_false = 1 - p_true
	# If the percentage of true is either 100% or 0%, just return 0 for the entropy
	if p_true == 1 or p_true == 0:
		return 0
	entropy = -(p_true * math.log(p_true, 2)) - (p_false * math.log(p_false, 2))
	return entropy

# Function to choose the best attribute by calculating information gain (using entropy function)
def choose_attribute(examples, remaining_attributes, class_idx):
	best_attribute = None
	prev_entropy = calculate_entropy(examples, class_idx)
	max_info_gain = 0
	# go through remaining attributes, split into true/false based on that attribute, and calculate entropy
	for att_idx in remaining_attributes:
		true_examples = []
		false_examples = []
		for example in examples:
			if example[att_idx] == True:
				true_examples.append(example)
			else:
				false_examples.append(example)
		# Calculate the entropy from splitting into true/false based on the current attribute
		true_example_pct = float(len(true_examples)) / float(len(examples))
		false_example_pct = 1 - true_example_pct
		curr_entropy = (true_example_pct * calculate_entropy(true_examples, class_idx)) + (false_example_pct * calculate_entropy(false_examples, class_idx))
		info_gain = prev_entropy - curr_entropy
		# Check if the info gain for the current attribute is greater than the max info gain
		if info_gain > max_info_gain:
			best_attribute = att_idx
			max_info_gain = info_gain
	if best_attribute == None:
		print "Best attribute was none \n"
		print "max_info_gain was % f \n" % max_info_gain
	return best_attribute

def print_tree(ID3Tree, attribute_names, parent, level, branch):
	print "level %d" % level
	level += 1
	if ID3Tree == True or ID3Tree == False:
		return ID3Tree
	attribute = ID3Tree.attribute
	trueChild = ID3Tree.trueChild
	falseChild = ID3Tree.falseChild
	printTrueChild = True
	printFalseChild = True
	if parent == None:
		print "Root attribute is %s." % attribute_names[attribute]
	else:
		print "Node attribute is %s. " % attribute_names[attribute] + "Parent attribute was %s, " % attribute_names[parent] + "and attribute is on %s branch." % branch
	if trueChild == True or trueChild == False:
		print "True child is a leaf, all attributes are %s." % trueChild
		printTrueChild = False
	else:
		print "True child node is attribute %s" % attribute_names[trueChild.attribute]
	if falseChild == True or falseChild == False:
		print "False child is a leaf, all attributes are %s. \n" % falseChild
		printFalseChild = False
	else:
		print "False child node is attribute %s. \n" % attribute_names[falseChild.attribute]
	if printTrueChild:
		print_tree(trueChild, attribute_names, attribute, level, True)
	if printFalseChild:
		print_tree(falseChild, attribute_names, attribute, level, False)

def print_verbose(attribute_names, training_examples, classified_examples):
	print "\n" + "The set of examples in the training set:"
	print attribute_names
	for ex in training_examples:
		print ex
	print "\n" + "The set of examples in the testing set (including classifications using ID3 decision tree and prior probability):"
	classified_attribute_names = []
	for att in attribute_names:
		classified_attribute_names.append(att)
	classified_attribute_names.append('ID3 Class')
	classified_attribute_names.append('PP Class')
	print classified_attribute_names
	for cl_ex in classified_examples:
		print cl_ex

# Function to print the output
def summary_output(inputFileName, trainingSetSize, testingSetSize, numberOfTrials, ID3_results, PP_results):
	print "\n" + "------------------------------------------------------------------------------"
	print "Summary:"
	print "file used = %s" % inputFileName
	print "number of trials = %d" % numberOfTrials
	print "training set size for each trial = %d" % trainingSetSize
	print "testing set size for each trial = %d" % testingSetSize
	if numberOfTrials == 0:
		print "Number of trials was 0, there are no results."
	else:
		if testingSetSize == 0:
			print "The training set size was too big, and no examples were left for testing data"
		else:
			avg_ID3 = float(sum(ID3_results))/float(len(ID3_results))
			avg_PP = float(sum(PP_results))/float(len(PP_results))
			print "mean performance of using prior probability derived from the training set = %.0f%% correct classification" % (100 * avg_PP)
			print "mean performance of decision tree over all trials = %.0f%% correct classification" % (100 * avg_ID3)
	print "------------------------------------------------------------------------------ \n"


if __name__ == "__main__":
    main()