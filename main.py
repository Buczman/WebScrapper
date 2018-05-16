#####################################################
#					WEBSCRAPPING					#
#			POLISH CONSTITUTIONAL TRIBUNAL			#
#													#
#		  MATEUSZ BUCZYNSKI & OSKAR RYCHLICA		#
#####################################################

#####################################################
# REQUIREMENTS:
#####################################################

# *Please download wkthmltopdf.exe, install it and specify
# path to it in variable pathwkthmltopdf.
# *Please install newest selenium driver
# *Please download geckodriver and specify path to it in
# variable driver(executable_path=...)

####################################################

# Below code is aimed at scraping jurisdiction accompanied
# by separate opinions.

# Specify filters and necessary parameters at PARAMETRIZATION
# section!!!

# Each method is described more thoroughly throughout the code

#####################################################
# OUTPUT:
#####################################################

# Output is as below:
# - outputL - main list containing:

# * outputLDict - list of dictionaries in a form of JSON
# containing fields:
# ** id		 - id of a jurisdiction
# ** link	 - direct link to the jurisdiction
# ** sign	 - signature name of a jurisdiction
# ** sep_opi - list of (if available) separate opinions
			 # in a form of dictionaries with fields:
			   # *** link - direct link to the separate
						# opinion
			   # *** by	  - name and surname of the
						# separate opinion's author

# * mostcommon5 - list of tuples with 5 most active
# authors in separate opinions in a form of:
# (name , number of separate opinions)

# * file output saved in folders in a following way:
# ** /ID_SIGNATURE - here are all PDF and HTML files
   # relating to a separate jurisdiction stored, each file
   # named as ID_SINGATURE.PDF (.HTML)
# ** /ID_SIGNATURE/separate_opinions - here are all
   # PDF and HTML files relating to each separate opinion
   # of a single jurisdiction stored, named as
   # ID_SIGNATURE_BY.PDF (.HTML)

# Program also produces a log file containing DEBUG info.

#####################################################
# IMPORTS
#####################################################

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pdfkit
import json
import collections
import os
import sys
from functions import *
pLoggerInit()

#####################################################
# CONSTANTS
#####################################################

outputDict = {} # output dict
pageCount=0
objectCount=0

#####################################################
# PARAMETRIZATION
#####################################################

# here you should define starting page of Tribunal Search and webpage of separate opinions
jurisdictionURL = 'http://ipo.trybunal.gov.pl/ipo/Szukaj'
sepOpinionURL = 'http://ipo.trybunal.gov.pl/ipo/SzukajZO'
mainOutputDirectory = "output/"

try:
	driver = webdriver.Firefox(executable_path = 'C:\Gecko\geckodriver.exe') # defining main driver object, using Firefox browser as default
	pathwkthmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'	 # defining wkthtml driver
	PDFconfig = pdfkit.configuration(wkhtmltopdf=pathwkthmltopdf)
except:
	pLogger('log.txt', True, '[ERROR] Drivers not located!')
	raise
wait = WebDriverWait(driver, 30)										 # defining wait object with timeout of 30 s

# True - print also PDF versions of pages, False (default) - no PDF output
isPDFOutput = False

#initializing logger

pLogger('log.txt', True, '[DEBUG] Drivers located!')

# Diagnosis stage
# To pick a particular "Diagnosis stage" specify a below argument:
# 0 - "Proper diagnosis stage"/"Rozpoznanie właściwe"
# 1 - "Signalization"/"Sygnalizacja"
# 2 - "Preliminary control"/"Wstępna kontrola"
diagnosisStageSel = 0
diagnosisStageSelDict = {0:'Proper diagnosis stage',
						 1:'Signalization',
						 2:'Preliminary control'}

# Time range
# To pick a particular "Time range" specify a below argument:
# 0 - "Last year"/"Ostatni rok"
# 1 - "Last 5 years"/"Ostatnie 5 lat"
# 2 - "Last 10 years"/"Ostatnie 10 lat"
# 3 - "Since 16.10.1997"/"od 16.10.1997 roku"
# 4 - "Since 1986"/"Od 1986 roku"
timeRangeSel = 3
timeRangeSelDict = {0:'Last year',
					1:'Last 5 years',
					2:'Last 10 years',
					3: 'Since 16.10.1997',
					4:'Since 1986'}

#####################################################
# PAGE LOAD & OBJECT FILTERING
#####################################################

pLogger('log.txt', True, '[DEBUG] Opening webpage: ', jurisdictionURL)
driver.get(jurisdictionURL) # opening main page
pLogger('log.txt', True, '[DEBUG] Page loaded! ', jurisdictionURL)

# waiting for filters to load - choosing one onlyu if it is not chosen already
diagnosisStage = wait.until(EC.visibility_of_element_located(
							 (By.ID,
							  'filtr:facetList_rodzajRozstrzygniecia:' + str(diagnosisStageSel) +':facetCommand')))
if len(diagnosisStage.find_elements_by_tag_name("img")) == 0:
	diagnosisStage.click()

timeRange = wait.until(EC.visibility_of_element_located(
							 (By.ID,
							  'filtr:facetList_wyszukiwanieOkres:' + str(timeRangeSel) +':facetCommand')))
if len(timeRange.find_elements_by_tag_name("img")) == 0:
	timeRange.click()

pLogger('log.txt', True, '[DEBUG] Filtering done using options: Diagnosis stage: {0}, Time Range: {1}!'.format(diagnosisStageSelDict[diagnosisStageSel],
																							                   timeRangeSelDict[timeRangeSel]))
#####################################################
# MAIN FILES SCRAPING
#####################################################

# This chunk crawls over all listed jurisdictions to find
# links to separate pages and stores them in a dict. This
# chunk returns a list of dictionaries with keys:
#
# - id		  - id of the scraped object
# - sign	  - signature number of the jurisdiction
# - link	  - hyperlink to the particular jurisdiction
# - sep_opi	  - empty list (for now) for future separate opinions

# Getting maximum views per page (in our case it should be 500)
allViewOptions =  wait.until(EC.visibility_of_element_located(
							 (By.XPATH,
							  "//select[@name='wyszukiwanie:dataTable:rows']"))).find_elements_by_tag_name("option")

allViewOptions[-1].click() # assuming that the options are ordered, we choose the last one as it displays the most elements at once
maxPagesPerView = allViewOptions[-1].get_attribute("value")
pLogger('log.txt', True, '[DEBUG] Achieved maximum objects per page: ', maxPagesPerView)

# Main hyperlink scraping procedure. It crawls over each link returned by dataTable on
# Tribunal Page and keeps its name and link in a dictionary
while True:
	# hardcoded 0.5s so we are sure that the model showed up (and fortunately hidden)
	time.sleep(0.5)
	wait.until_not(EC.visibility_of_element_located((By.ID, "j_idt24_modal")))
	objectCount = pageCount*500 + 0 # single page iterator

	while True:
		name = 'wyszukiwanie:dataTable:' + str(objectCount) + ':dokument_:sprawa:sprawaLink' #each jurisdiction XPATH is build from constant parts and interable
		if len(driver.find_elements_by_xpath('//a[@id="' + name + '"]')) == 0: # we want to break if we find no correct elements on page
			break
		item = driver.find_element_by_xpath('//a[@id="' + name + '"]')
		sign_ = item.text # item's text's a signature
		link_ = item.get_attribute('href') # item's href's a link to a separate page
		if sign_ not in outputDict:
			outputDict[sign_] = [{'id':objectCount, 'link':link_, 'sep_opi':[]}]
		else:
			outputDict[sign_].append({'id':objectCount, 'link':link_})
		objectCount+=1


	nextPage = driver.find_element_by_class_name("ui-paginator-next") # page
	nextPageClasses = nextPage.get_attribute('class')
	pLogger('log.txt', True, "[DEBUG] Looping over page num:", str(pageCount + 1), ', scraped ', str(objectCount), ' objects')
	if 'ui-state-disabled' in nextPageClasses: # if button is not clickable it means we are at last page and can break
		break

	pageCount+=1
	nextPage.click()

# In some cases there are more than one jurisdiction with the same signature - we calculate only unique values
pLogger('log.txt', True, '[DEBUG] FINALIZED STEP 1/3, scraped {0} jurisdiction(s) in {1} object(s)'.format(len(outputDict), objectCount))

#####################################################
# SEPARATE OPINIONS FILES SCRAPING
#####################################################

# This method iterates over all jurisdiction objects and searches the signature name
# on the separate opinion's search page and then saves all the separate opinions that
# we found. In case of no separate opinions an empty list is attached to sep_opi field
# of jurisdiction's dictionary.

# Separate opinion's dictionary is as below:
# - link  - link to the separate opinion's website
# - by	  - name and surname of separate opinion's author

# Connection with the separate opinions webpage
pLogger('log.txt', True, '[DEBUG] Opening webpage: ', sepOpinionURL)
driver.get(sepOpinionURL)
pLogger('log.txt', True, '[DEBUG] Page loaded! ', sepOpinionURL)

pageCount = 0
objectCount = 0

while True:
	# hardcoded 0.5s so we are sure that the model showed up (and fortunately hidden)
	time.sleep(0.5)
	wait.until_not(EC.visibility_of_element_located((By.ID, "j_idt24_modal")))
	
	#getting table with all links to separate opinions
	table = driver.find_element_by_class_name('ui-datatable-tablewrapper')
	links = table.find_elements_by_tag_name('a')
	# but to find author we need to specify long xpath - many children to the closest tag.
	# Author is at 5th position in the separate opinion's object
	separateOpinionsAuthors = driver.find_elements_by_xpath("//table[@class='datalist2-noborder2']/tbody/tr[position()=5]/td/div/div/dl")
	for n, link in enumerate(links):
		if link.text in outputDict:
			link_ = link.get_attribute('href') #for each link we get a direct hyperlink
			allAuthors = [x.text for x in separateOpinionsAuthors[n].find_elements_by_tag_name('dt')] #we get all the authors of a single separate opinion
			outputDict[link.text][0]['sep_opi'].append({'link' : link_, 'by' :allAuthors})
			objectCount+=1
			

	nextPage = driver.find_element_by_class_name("ui-paginator-next") #page'
	nextPageClasses = nextPage.get_attribute('class')
	pLogger('log.txt', True, "[DEBUG] Looping over page num:", str(pageCount + 1), ', scraped ', str(objectCount), ' separate opinion(s)')
	if 'ui-state-disabled' in nextPageClasses: #if button is not clickable it means we are at last page and can break
		break

	pageCount+=1
	nextPage.click()

pLogger('log.txt', True, '[DEBUG] FINALIZED STEP 2/4, searched for all separate opinions')

# We are closing the driver as all other operations are don without its use
driver.close()

#####################################################
# JUDGES ACTIVITY
#####################################################

# This method creates a Counter objects that counts occurences of the authors'
# surnames in the list of all separate opinions authors. Then we simply pick 5 judges
# (objects) from the top of the list.

fullSurnames = [x for key in outputDict for item in outputDict[key][0]['sep_opi'] for x in item['by']]
counterSurnames = collections.Counter(fullSurnames)
mostcommon5 = counterSurnames.most_common()[0:5]

print('\n')
pLogger('log.txt', False, '5 most common judges by separate opinions:\n')
for judge in mostcommon5:
	pLogger('log.txt', False, "{: >40} {: >5} separate opinion(s)".format(*judge))
print('\n')
pLogger('log.txt', True, '[DEBUG] FINALIZED STEP 3/4, found 5 most active judges')

#####################################################
# FILE OUTPUT
#####################################################

# While performing the file output we loop through outputDictL
# Previously we have put the appropriate case links in the sepOpi['link']
# Using those links we download both a .pdf and a .html file for each
# case and seperate opinion. The seperate opinions are found in a seperate
# directory. htmldownload is a seperate function that allows us to use a
# similar one-line to the pdf download, for enhanced code readability.

pLogger('log.txt', True, '[DEBUG] Starting download of the files')

for signNum, key in enumerate(outputDict):
	obj = outputDict[key][0]
	#Every 25 downloaded cases we inform about our progress
	if signNum % 25 == 0 and signNum > 0:
		pLogger('log.txt', True, '[DEBUG] Succesfully downloaded {0} file(s)!'.format(signNum))

	#First we create the output directory
	outputDirectory = mainOutputDirectory + str(key).replace("/", "_").replace(" ", "_")
	if not os.path.exists(outputDirectory):
		os.makedirs(outputDirectory)
	separate_opinions = obj['sep_opi']

	#We will attempt to download the seperate opinions only if they exist
	if separate_opinions:
		tempDirectory = outputDirectory + "/" + "seperate_opinions"
		if not os.path.exists(tempDirectory):
			os.makedirs(tempDirectory)

		#Loop through all seperate opinions to download them
		for n, sepOpi in enumerate(separate_opinions):
			filename = (str(n) + "_" + key + "_" + ''.join(sepOpi['by']).replace(' ','_')).replace("/", "_").replace(" ", "_")
			if isPDFOutput:
				sys.stdout = open(os.devnull, 'w')
				pdfkit.from_url(sepOpi['link'], tempDirectory + "/" + filename + ".pdf", configuration = PDFconfig)
				sys.stdout = sys.__stdout__
			try:
				htmldownload(tempDirectory + "/" + filename + ".html", sepOpi['link'])
			except:
				pLogger('log.txt',False, "[ERROR] File {0} could not be saved. Please download it manually via: {2}".format(filename,sepOpi['link']))
				continue

	for case in outputDict[key]:

		#Finally download the case itself
		filename = (str(case['id'])+str(key)).replace("/", "_").replace(" ", "_")
		if isPDFOutput:
			sys.stdout = open(os.devnull, 'w')
			pdfkit.from_url(case['link'], outputDirectory + "/" + filename + ".pdf", configuration = PDFconfig)
			sys.stdout = sys.__stdout__
		try:
			htmldownload(outputDirectory + "/" + filename + ".html", case['link'])
		except:
			continue

pLogger('log.txt', True, '[DEBUG] FINALIZED STEP 4/4, saved all files')