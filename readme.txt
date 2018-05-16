#####################################################
#                   WEBSCRAPPING                    #
#           POLISH CONSTITUTIONAL TRIBUNAL          #
#                                                   #
#         MATEUSZ BUCZYNSKI & OSKAR RYCHLICA        #
#####################################################

#####################################################
# REQUIREMENTS:
#####################################################

*Please download wkthmltopdf.exe, install it and specify 
path to it in variable pathwkthmltopdf.
*Please install newest selenium driver
*Please download geckodriver and specify path to it in 
variable driver(executable_path=...)

#####################################################

Below code is aimed at scraping jurisdiction accompanied
by separate opinions.

Specify filters and necessary parameters at PARAMETRIZATION
section!!!

Each method is described more thoroughly throughout the code

#####################################################
# OUTPUT:
#####################################################

Output is as below:
- outputL - main list containing:

* outputLDict - list of dictionaries in a form of JSON
containing fields:
** id      - id of a jurisdiction
** link    - direct link to the jurisdiction
** sign    - signature name of a jurisdiction
** sep_opi - list of (if available) separate opinions
             in a form of dictionaries with fields:
			   *** link - direct link to the separate
                        opinion
			   *** by   - name and surname of the
                        separate opinion's author

* mostcommon5 - list of tuples with 5 most active
authors in separate opinions in a form of:
(name , number of separate opinions)

* file output saved in folders in a following way:
** /ID_SIGNATURE - here are all PDF and HTML files
   relating to a separate jurisdiction stored, each file
   named as ID_SINGATURE.PDF (.HTML)
** /ID_SIGNATURE/separate_opinions - here are all
   PDF and HTML files relating to each separate opinion
   of a single jurisdiction stored, named as
   ID_SIGNATURE_BY.PDF (.HTML)

Program also produces a log file containing DEBUG info.