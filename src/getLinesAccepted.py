#!/usr/bin/env python3
##########################################################################################
# Developer: Icaro Alzuru         Project: HuMaIN (http://humain.acis.ufl.edu)
# Description: 
#   Generates the file with the accepted or known lines: When the three OCRs generate 
# the same value or when only two generate the same value and have a confidence > 0.9. 
#
##########################################################################################
# Copyright 2019    Advanced Computing and Information Systems (ACIS) Lab - UF
#                   (https://www.acis.ufl.edu/)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##########################################################################################

import argparse, io, os, sys

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
def getConfidence( probPathFilename ):
	""" Given a probabilities file: .prob, returns the number of symbols 
	and their average confidence.

	:type probPathFilename: string
	:param probPathFilename: 
	"""
	# Read file
	lines = []		# List of lines of the file
	with open( probPathFilename ) as f:
		lines = [line.rstrip() for line in f]

	# Compute the summation of the uncertainty
	sum = 0.0
	n = 0
	text = ""
	for line in lines:
		words = line.split('\t')
		if words[0] != ' ':
			text = text + words[0]
			if ( len(words) > 1 ):		
				sum = sum + float(words[1])
				n = n + 1

	if n == 0:
		return "", 0, 0.0
	else: 
		return text, n, sum/n

#----------------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	""" Generates the file with the accepted or known lines: When the three OCRs generate the same value or when only two generate the same value and have a confidence > 0.9. 
	"""
	parser = argparse.ArgumentParser("Generates the file with the accepted or known lines: When the three OCRs generate the same value or when only two generate the same value and have a confidence > 0.9.")
	parser.add_argument('-i1', '--input1', action="store", required=True, help="Directory where the first probability files are located.")
	parser.add_argument('-i2', '--input2', action="store", required=True, help="Directory where the second group of probability files are located.")
	parser.add_argument('-i3', '--input3', action="store", required=True, help="Directory where the third group of probability files are located.")
	parser.add_argument('-o', '--output', action="store", required=True, help="Path and filename of the text file which will store the result and confidence in both directories.")
	args = parser.parse_args()

	# Arguments Validations
	if ( not os.path.isdir( args.input1 ) ):
		print('Error: The first directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(1)

	if ( not os.path.isdir( args.input2 ) ):
		print('Error: The second directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(1)

	if ( not os.path.isdir( args.input3 ) ):
		print('Error: The third directory of probability files was not found.\n')
		parser.print_help()
		sys.exit(1)

	# Create the lists of files to process
	files_list1 = list()
	for root, dirs, filenames in os.walk( args.input1 ):
		files_list1 = list(f for f in filenames if f.endswith('.prob'))
	n1 = len(files_list1)

	files_list2 = list()
	for root, dirs, filenames in os.walk( args.input2 ):
		files_list2 = list(f for f in filenames if f.endswith('.prob'))
	n2 = len(files_list2)

	files_list3 = list()
	for root, dirs, filenames in os.walk( args.input3 ):
		files_list3 = list(f for f in filenames if f.endswith('.prob'))
	n3 = len(files_list3)

	files_set1 = set( files_list1 )
	files_set2 = set( files_list2 )
	files_set3 = set( files_list3 )

	# Set of probabilities files present or common in the three directories
	files_set123 = files_set1 & files_set2 & files_set3
	files_list123 = list(files_set123)
	files_list123.sort()

	# Set of probabilities files only present in the directories 1 and 2
	files_set12 = (files_set1 & files_set2) - files_set3
	files_list12 = list(files_set12)
	files_list12.sort()

	# Set of probabilities files only present in the directories 1 and 3
	files_set13 = (files_set1 & files_set3) - files_set2
	files_list13 = list(files_set13)
	files_list13.sort()

	# Set of probabilities files only present in the directories 2 and 3
	files_set23 = (files_set2 & files_set3) - files_set1
	files_list23 = list(files_set23)
	files_list23.sort()

	with open(args.output, 'w') as f:
		i = 0
		while i<len(files_list123):
			filename = files_list123[i]
			s1, l1, a1 = getConfidence( args.input1 + "/" + filename )
			s2, l2, a2 = getConfidence( args.input2 + "/" + filename )
			s3, l3, a3 = getConfidence( args.input3 + "/" + filename )
			if (s1 == s2) and (a1 > 0.9) and (a2 > 0.9):
				s = filename + "\t" + str(l1) + "\t" + str(a1) + "\t" + str(a2) + "\t" + str(a3) + "\t" + s1 + "\n"
				f.write( s )
				i = i + 1
				continue
			if (s1 == s3) and (a1 > 0.9) and (a3 > 0.9):
				s = filename + "\t" + str(l1) + "\t" + str(a1) + "\t" + str(a2) + "\t" + str(a3) + "\t" + s1 + "\n"
				f.write( s )
				i = i + 1
				continue
			if (s2 == s3) and (a2 > 0.9) and (a3 > 0.9):
				s = filename + "\t" + str(l2) + "\t" + str(a1) + "\t" + str(a2) + "\t" + str(a3) + "\t" + s2 + "\n"
				f.write( s )
				i = i + 1
				continue
			if (s1 == s3) and (s2 == s3):
				s = filename + "\t" + str(l1) + "\t" + str(a1) + "\t" + str(a2) + "\t" + str(a3) + "\t" + s1 + "\n"
				f.write( s )
				i = i + 1
				continue

			i = i + 1

		i = 0
		while i<len(files_list12):
			filename = files_list12[i]
			s1, l1, a1 = getConfidence( args.input1 + "/" + filename )
			s2, l2, a2 = getConfidence( args.input2 + "/" + filename )
			if (s1 == s2) and (a1 > 0.9) and (a2 > 0.9):
				s = filename + "\t" + str(l1) + "\t" + str(a1) + "\t" + str(a2) + "\t-1\t" + s1 + "\n"
				f.write( s )
			i = i + 1

		i = 0
		while i<len(files_list13):
			filename = files_list13[i]
			s1, l1, a1 = getConfidence( args.input1 + "/" + filename )
			s3, l3, a3 = getConfidence( args.input3 + "/" + filename )
			if (s1 == s3) and (a1 > 0.9) and (a3 > 0.9):
				s = filename + "\t" + str(l1) + "\t" + str(a1) + "\t-1\t" + str(a3) + "\t" + s1 + "\n"
				f.write( s )
			i = i + 1

		i = 0
		while i<len(files_list23):
			filename = files_list23[i]
			s2, l2, a2 = getConfidence( args.input2 + "/" + filename )
			s3, l3, a3 = getConfidence( args.input3 + "/" + filename )
			if (s2 == s3) and (a2 > 0.9) and (a3 > 0.9):
				s = filename + "\t" + str(l2) + "\t-1\t" + str(a2) + "\t" + str(a3) + "\t" + s2 + "\n"
				f.write( s )
			i = i + 1
