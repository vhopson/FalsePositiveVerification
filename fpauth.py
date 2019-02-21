#!/usr/bin/python
#
# This script requires "requests", and "ConfigParser" along with Python3
#

import os
import sys
import argparse
import configparser
import CodeDx

## FP Authorization Criterion
#
# This routine receives the information for the individual FP from the Code Dx server.
# Depending on what *YOUR* criterion are for determining the validity of an authorized
# or unauthorized FP detection, return True or False respectively.  You can do anything
# in this part of the script from the information presented
#
# Currently, this only returns False.  So all False Positives detected are marked as
# the setting in your configuration file as 'status-fp-unauth'
#
def CheckAuthorization(finding) :
	return False

##
# Main Operational Entry Point
#
 
def main(args) :

	# Open the configuration file and set up access to the Code Dx server
	myini = configparser.ConfigParser()
	myini.read(args.config)
	
	# create a Code Dx object to use for API calls
	cdx = CodeDx.CodeDx(myini)
	
	# check to see that the project exists
	if ( args.proj in cdx.project_dictionary ) == False :
		print("Project \"" + args.proj + "\" does not exist on the Code Dx server.")
		return -1
	
	# compute the Project ID for use in our later calls
	project_id = cdx.project_dictionary[args.proj]
	print("Project ID: ", project_id)
	
	# collect all of the statuses, and check that the FP authorized/unauthorized settings
	# are available on the server
	unauth = myini['FPmarkup']['status-fp-unauth']
	unauth_status = 0
	auth = myini['FPmarkup']['status-fp-auth']
	auth_status = 0
	statuses = cdx.getStatuses(project_id)
	for key, val in statuses.items() :
		if (unauth_status == 0) and (unauth == val['display']) :
			unauth_status = val['id']
		if (auth_status == 0) and (auth == val['display']) :
			auth_status = val['id']
	
	# lets check and see if all of our statuses are available
	if unauth_status == 0 :
		print("Error: please add a user with name \"" + unauth + "\"")
		return -1
	
	if auth_status == 0 :
		print("Error: please add a user with name \"" + auth + "\"")
		return -1
	
	# Now we need to gather the findings and iterate across them
	# We are only looking for "false positive" in our status filter.
	# A check of each one is performed to determine the marking that should be
	# applied.
	unauth_list = []
	auth_list = []
	filter = { "status" : "false-positive" }
	findings = cdx.getFindings(project_id, filter)
	for finding in findings :
		# check each finding for authorization and add it to the appropriate
		# list
		if CheckAuthorization(finding) :
			# True, therefore add to authorized list
			auth_list.append(finding['id'])
		else :
			# False, therefore add to unauthorized list
			unauth_list.append(finding['id'])
	
	# print some statistics for display
	print("False Positive authorization for", len(auth_list), "findings")
	print("False Positive not authorized for", len(unauth_list), "findings")
	
	# now execute two bulk operations to write the data to the Code Dx server
	job = cdx.bulkStatusUpdate(project_id, unauth_list, unauth_status)
	cdx.waitForJob(job)
	
	job = cdx.bulkStatusUpdate(project_id, auth_list, auth_status)
	cdx.waitForJob(job)
	
	print("Done.")

##
# Build environment and parse command line
desc = " This command will investigate items marked as \"False Positive\"" + \
	   " and change them to \"unauthorized\"."
parser = argparse.ArgumentParser(description=desc)
parser.add_argument("--config", "-c", required=True, help="Input configuration file")
parser.add_argument("--proj", "-p", required=True, help="Project to modify")
args = parser.parse_args()

if __name__ == "__main__" :
	main(args)
