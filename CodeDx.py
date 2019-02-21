import sys
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import configparser
import time

## Code Dx Object to contain Code Dx API specifics.
#
# This object is constructed with several pieces of common information available
# directly from the object.  These items are documented as the attributes above
# (in Doxygen).
#
class CodeDx(object) :

	## Constructor
	#
	def __init__(self, ini) :
		# disable the Insecure request warning when using HTTPS ***DEMO ONLY
		requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
		
		# Grab values from the INI file that are related to the Code Dx server
		self.url = ini['CodeDx']['transport'] + "://" + ini['CodeDx']['ip']
		if 'port' in ini['CodeDx'] :
			self.url += ":" + ini['CodeDx']['port']
		
		# append the basis for the path into the API
		self.url += "/codedx"
		
		# Capture the API-Key for use in this object
		self.apikey = ini['CodeDx']['api-key']
		
		# here are the default headers we will use for all requests
		self.headers = { 'Content-Type' : 'application/json',
						 'API-Key' : self.apikey }
		
		# get a project list from the server create a dictionary for quick
		# identification of project ID's
		self.project_dictionary = {}
		for project in self.getProjects() :
			self.project_dictionary[project['name']] = project['id']
		

	## getProjects
	#
	# Collect a projects list from the designated server for this object.  We collect
	# { 'projects' : [ { "id", "name" }, ... ] }
	#
	def getProjects(self) :
		# reach out to the Code Dx server and capture the project list.
		cdx = requests.get(self.url + '/api/projects', headers = self.headers, verify=False)
		if cdx.status_code != 200 :
			print("Code Dx object: getProjects GET request failed with status " + cdx.status_code)
			return []
		
		# we should have a successful list. Return it.
		return cdx.json()['projects']		

	## getStatuses
	#
	# Get all of the available status values from the server for the given project
	#
	def getStatuses(self, id) :
		# reach out to the Code Dx server and collect all available status settings.
		cdx = requests.get(self.url + '/api/projects/' + str(id) + '/statuses',
						   headers = self.headers, verify=False)
		if cdx.status_code != 200 :
			print("Code Dx object: getProjects GET request failed with status",cdx.status_code)
			return []
	
		# we now have available statuses for our server.  Return the dictionary from the query
		return cdx.json()
	
	## getFindings
	#
	# Collect all of the findings, and return them in a simple list of dictionaries.
	#
	def getFindings(self, id, filter) :
		# add required elements for the filter
		req_filter = { 'filter' : filter }
		req_filter["sort"] = { "by" : "id", "direction" : "ascending" }
		max_results = 2500
		current_page = 1
		req_filter["pagination"] = { "page" : current_page, "perPage" : max_results }
		
		# loop and gather all results possible into our list
		retval = []
		while True :
			# Get the data requested.
			cdx = requests.post(self.url + "/api/projects/" + str(id) + "/findings/table",
								headers = self.headers, data = json.dumps(req_filter), verify=False)
			if cdx.status_code != 200 :
				print("Code Dx object: getFindings POST request failed with status", cdx.status_code)
				return []
			
			# append the data to our return value
			returned_list = cdx.json()
			retval.extend(returned_list)
			if len(returned_list) < max_results :
				break
			else :
				current_page += 1
				req_filter["pagination"]["page"] = current_page
				
		# we should have everything.  Return the results to the caller
		return retval

	## bulkStatusUpdate
	#
	# Set the status of the findings to the desired value
	#
	def bulkStatusUpdate(self, id, findings, status) :
		# if the input length of the findings to change is zero, simply reject it.
		if len(findings) < 1 :
			return '-1'
		
		# convert the input list to strings
		id_list = []
		for finding in findings :
			id_list.append(str(finding))
			
		# prepare the filter we will need
		req_filter = { "filter" : { "finding" : id_list } }
		req_filter['status'] = status
		
		cdx = requests.post(self.url + "/api/projects/" + str(id) + "/bulk-status-update",
							verify=False, headers = self.headers, data = json.dumps(req_filter))
		if cdx.status_code != 200 :
			print("Code Dx object: bulkStatusUpdate POST request failed with status", cdx.status_code)
			return '-1'
		
		# return the job-id
		return cdx.json()['jobId']
		
	## waitForJob
	#
	# Check each second for the jobId that is queued to be done
	#
	def waitForJob(self, jobId) :
		# Just in case the user is not watching closely
		if jobId == '-1' :
			return
		
		# loop until the job returns complete
		while True :
			cdx = requests.get(self.url + "/api/jobs/" + jobId, verify=False, headers=self.headers)
			if cdx.status_code != 200 :
				print("Code Dx object: waitForJob GET request failed with status", cdx.status_code)
				break
			
			# check the response to the job code.  break out of the loop if done
			response = cdx.json()
			if response['status'] != 'queued' :
				break
			
			# not done yet.  Wait for 1 second
			time.sleep(1)
			
				
			
		
	
		
		

