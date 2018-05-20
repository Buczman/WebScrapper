import os
import time
import urllib
import urllib.request
import html.parser
import requests
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pdfkit
import json
import collections
import sys
from concurrent.futures import ThreadPoolExecutor

#pLogger saves log to file and prints it
def pLogger(filename, ifPrintTime = True, *args):
	if ifPrintTime:
		print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), ''.join(args))
		with open(filename, 'a+') as file:
			file.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' ' + ''.join(args) + '\n')
	else:
		print(''.join(args))
		with open(filename, 'a+') as file:
			file.write(''.join(args) + '\n')

def pLoggerInit(filename = 'log.txt'):
	if os.path.isfile(filename):
		os.remove(filename)

def driverdownload(driver,filename,url):
	#The function will download a given file (from url) and save it with given
	#filename, using the selenium webdriver method. It is slower, but should
	#produce less errors (if we requests files to fast, the server responds
	#with errors more often, maybe because of some kind of flood protection)

	driver.get(url)
	time.sleep(0.5)
	WebDriverWait(driver, 30).until_not(EC.visibility_of_element_located((By.ID, "j_idt24_modal")))
	page = driver.page_source
	file_ = open(filename, 'w+', encoding='utf-8')
	file_.write(page)
	file_.close()
	time.sleep(1.5)
	pass

def htmldownload(filename,url):
	#This uses the requests/urllib approach to downloading files.

	req=urllib.request.Request(url, None, {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; G518Rco3Yp0uLV40Lcc9hAzC1BOROTJADjicLjOmlr4=) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3','Accept-Encoding': 'gzip, deflate, sdch','Accept-Language': 'en-US,en;q=0.8','Connection': 'keep-alive'})
	cookieJar = CookieJar()
	opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
	response = opener.open(req)
	rawResponse = response.read().decode('utf8', errors='ignore')
	with open(filename, 'w+', encoding='utf-8') as fid:
		fid.write(rawResponse)
	response.close()
	pass

def check(filename):
	#Function returns False if word "java" isn't found inside the file
	#Returns true otherwise. The word appears in the error code "Nieoczekiwany
	#błąd aplikacji" which signalizes an issue
	
	if (open(filename, 'r', encoding='UTF-8').read().find('java')) > 1:
		return False
	return True