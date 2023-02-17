#!/usr/bin/env python
# coding: utf-8

# # Web Scraping: Top Cities in the United States
# 
# *written by: yg2619*
# 
# In order to collect data from Wikipedia about the top cities in the United States, three parts of codes are written including:
# - Scraping data from the main wikipedia page
# - Collecting additional information from each city's wikipedia page
# - Cleaning and Preprocessing data for BigQuery use
# 
# ## Part I - Scraping data from the main wikipedia page
# 
# ### import libraries
# 
# In this assignment, I used the library `requests` to make HTTP requests and access the web page while using `BeautifulSoup` from the `bs4` package to parse the HTML and XML files to retrieve data. In addition, `pandsa` and `re` were also used to build and preprocess the dataset.
# 
# Please note that the libraries `requests` and `BeautifulSoup` need to be installed on your laptop first via terminal commands such as `pip3 install requests` before improting them.

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


# ### retrieve data
# 
# In order to retrieve data from the wikipedia page, I first built a function to send the requests to the web page while checking if the request is successful. 

# In[2]:


def get_page(url):
    response = requests.get(url)    #make the HTTP requests
    try:
        if response.status_code == 200:  #code 200 indicates a successful request
            return response              #return the response content
        else:
            return None
    except RequestException as e:       #if the request is not successful, print out the exceptions content
        print('Requests Failed: '+str(e))


# Then I used the function to make HTTP requests to the main wikipedia page as follows.

# In[3]:


main_page = get_page("https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population")


# After that, I used BeautifulSoup to parse the content of the response using lxml's HTML parser.

# In[4]:


soup = BeautifulSoup(main_page.text,'lxml')  #other parsers like 'html.parser' and 'xml' can also be considered


# After carefully inspecting the source code of the main wikipedia page, I found that the data that needs to be retrieved are located inside the `table` element with attributes `class='wikitable sortable'`. Therefore, the following codes were used to find the data inside the table element and transform them into a data frame.

# In[5]:


cities = soup.find('table', attrs={'class':'wikitable sortable'})   #find the table element


# In[6]:


df = pd.read_html(str(cities))  #read the html content into strings
newdf = df[0]                  #build data frame
columns = newdf.iloc[0].tolist(); columns #retrieve the column names of the data frame from the first row


# ### modify column names and remove duplicated columns

# In[7]:

#This is the part of the code that starts breaking now when you try it on the new Wikipedia page.
newdf = newdf.drop([7,9],axis=1)        #remove duplicated columns
colname = ['2018 Rank','City','State','2018 Population Estimate','2010 Population Estimate','Population Change','2016 Land Area','2016 Population Density','Location']
newdf.columns = colname             #rename the columns of the data frame for easier interpretation
newdf = newdf.drop([0],axis=0)             #remove the first row


# ### clean the `City` column
# Finally, I further cleaned the data in the `city` column to remove meaningless annotation symbols.

# In[8]:


for i in range(0,len(newdf)):
    newdf.iloc[i,1] = re.sub('\[.*?\]','',newdf.iloc[i,1])    #remove the annotation symbol
newdf.head()


# ## Part II - Collecting additional information from each city's wikipedia page
# 
# ### retrieve each city's wikipedia link from the main page
# 
# It can be seen from the main wikipedia page that each city's name in the table contains a link directing to the city's own wikipedia page. The links are all in the elements `a` with the label `href`. 
# 
# Therefore, I first retrieved all the top cities' names and transformed them into a list. After that, I used BeautifulSoup to find all the content inside the `a` elements and then iterated through each of them to add its link to a new list as long as the link's text is exactly one of the names that we are looking for.

# In[9]:


citynames = newdf['City'].tolist()    #find all the top cities' names
links = cities.find_all('a')      #find all the a elements in the table
wikilinks = []                  #create a new list to contain the links of wikipedia links

for link in links:         #for each a element
    if link.text in citynames:     #if the text of the link matches any of the city names
        wikilinks.append("https://en.wikipedia.org"+link.get('href'))  #concatenate the link with the wikipedia's url and add them to the wikilinks list


# ### retrive additional information from individual web page - InfoBox
# 
# After inspecting the wikipedia pages of the first few top cities, I noticed that each wikipedia page includes a information box on the right which contains critical characteristics of the city such as the mayor, the elevation, and the time zone. The information box is in the `table` element with the attribute `class="infobox"`.
# 
# Therefore, I decided to write a loop to extract the data in each city's information box and add them to the orginal data frame.

# In[10]:


num = 0
for link in wikilinks:
    cityres = get_page(link)      #for each link in the wikilinks list, make HTTP requests to the web page
    
    citysoup = BeautifulSoup(cityres.text,'lxml')   #parse each HTML file using BeautifulSoup
    info = citysoup.find('table',attrs={"class":"infobox"})  #find the information box in each HTML file
    
    df = pd.read_html(str(info))   #read the content of the information box into strings
    clist = df[0]
    
    ind = clist[clist[0]=='Country'].index[0]   
    clist = clist.drop(clist.index[range(0,ind+1)])   #remove the redundant information of the city's pic & map
   
    for i in range(0,len(clist)):         #for each row of clist where the 1st column contains attributes name and 2nd column contains values
        if type(clist.iloc[i,0])==str:    #if the attribute name is string (not NA or null)
            clist.iloc[i,0] = re.sub('^•\s|\[.*?\]','',clist.iloc[i,0])  #remove redundant symbols
            clist.iloc[i,0] = re.sub('[\(\)]','',clist.iloc[i,0])
            if len(clist.iloc[i,0].split())<=4 and clist.iloc[i,0] not in colname:   #if the attribute name is less than 5 words and does not have duplicates in the original dataset
                clist.iloc[i,0] = clist.iloc[i,0].lower()       #change the attribute name into lowercase letters to aviod duplications
                if clist.iloc[i,0] not in newdf.columns:    #if the attribute name is not already a column name in the original data frame
                    newdf[clist.iloc[i,0]] = ""           #add a new column to the original data frame with the attribute name and set the default value as blank strings
                index = newdf.columns.get_loc(clist.iloc[i,0])    #find the index of the column that the new data should belong to
                newdf.iloc[num,index]=clist.iloc[i,1]         #add the new data into corresponding columns in the orginal data frame
    num=num+1     #store the index of the city


# ### combine data from similar columns and remove useless columns
# 
# In order to preprocess the data in the data frame for easier interpretation and avioding duplications, I first copied the data in the original data frame into a new data frame called `topcities`. Then I wrote a function to combine the data in columns `zip code` and `zip codes`, `area code` and `area codes`, `demonym` and `demonym`,`county` and `counties`.
# 
# After that, I removed columns in `topcities` that contain less than 100 non-null values (which means that more than 2/3 of the top cities do not contain such information).

# In[11]:


topcities = newdf.copy()    #make a copy of the newdf

def combine(origin,new):  #define a function to insert the data from the 'new' column into the 'origin' column
    for i in topcities[topcities[new]!=""].index:  #for each row of the 'new' column which contains non-null value
        topcities.iloc[i-1,topcities.columns.get_loc(origin)] = topcities.iloc[i-1,topcities.columns.get_loc(new)] #insert the value in the row into the 'origin' column

combine('zip codes','zip code')  #call the function to modify the columns
combine('area codes','area code')
combine('demonyms','demonym')
combine('county','counties')

for column in topcities.columns:        #for each column in the topcities data frame
    if sum(topcities[column]!="")< 100:   #if the columns contains less than 100 non-null values
        topcities = topcities.drop(column,axis=1)   #remove the column


# Later on, I further modified the columns names of the data frame to follow the naming rules in BigQuery and for easier intepretation. 
# 
# Then I removed the columns that contain useless information.

# In[12]:


topcities.columns = ['Rank2018', 'City', 'State', 'Population Estimate2018',
       'Population Estimate2010', 'Population Change Percentage',
       'Land Area2016', 'Population Density2016',
       'Location', 'Named For', 'government', 'Government Type', 'Mayor', 'area', 'total',
       'Land Area Latest', 'Water Area Latest', 'Metro Area Latest', 'Elevation', 'population 2010', 'rank',
       'density', 'Demonyms', 'Time Zone', 'Summer DST', 'Zip Codes',
       'Area Codes', 'FIPS Code', 'GNIS Feature Id', 'Website', 'County',
       'Incorporated', 'estimate 2017', 'Urban Area Latest', 'City Manager']      #modify the column names for easier interpretation

uselessvar = ['government', 'area','total','population 2010', 'rank',
       'density', 'estimate 2017']      #list of useless column names
for var in uselessvar:   #for each column in the useless columns
    index = topcities.columns.get_loc(var)    #find the index of the column
    topcities = topcities.drop(topcities.columns[index],axis=1)    #remove the column from the data frame


# ### retrive additional information from individual web page - Text Description
# 
# In addition, I also found that the first paragraph in each city's wikipedia page is a brief introduction of the city and describes the city's basic features in a precise way. Therefore, I decided to add the first paragraph as a new column named as `Description` to the original data frame.
# 
# **Note**: according to the source codes, the text of the first paragraphs are contained in a `p` element with no attributes which is inside the `div` element with a `class` of `mw-parser-output`.

# In[13]:


topcities['Description'] = ''  #add a new column Description and set the default value as blank strings
index = topcities.columns.get_loc('Description')   #store the index of the Description column in a variable
num = 0
for link in wikilinks:      #for each city's wikipedia link
    cityres = get_page(link)    #make HTTP requests
    citysoup = BeautifulSoup(cityres.text,'lxml')   #parse the HTML files
    desp = citysoup.find('div',attrs={"class":"mw-parser-output"})   #find the div element
    df = desp.find_all('p',attrs={'class': None})  #find all the p elements in div
    description = re.sub('\[.*?\]|\\n|\\xa0|\s\(listen\)','', df[0].text)     #find the text of the first paragraph and remove meaningless symbols
    topcities.iloc[num,index] = description     #add the text into the new column
    num+=1    #document the index of the city


# In[14]:


topcities.head()  #inspect the first few rows in topcities


# ## Part III - Cleaning and Preprocessing data for BigQuery use
# 
# In order to prepare the data frame for further queries, the data that I have collected need to be cleaned and converted to suitable format. 
# 
# The cleaning and preprocessing process mainly includes the following steps:
# - remove duplicated data in a cell (e.g. the land area column contains data measured in both square miles and square kilometers)
# - remove the unit of the data such as `sq mi`, `ft`, and `%`
# - remove meaningless symbols or information retrieved from the web
# - convert the column to approporiate data type
# 
# **Please note that after preprocessing, all the areas in the data frame are measured in square miles, the population density is measured as the number of residents per unit of land area, and the elevation is measured in feet.**
# 
# ### Remove the Annotation Symbol From All Values
# It should be noted that many information on Wikipedia contains an annotation symbol which points to its reference. Therefore, the first cleaning step is to remove these annotation symbols which could impact the data quality.

# In[15]:


ustopcities = topcities.copy()      #copy the data in topcities to ustopcities

for i in range(0,len(ustopcities)):    #for each row
    for j in range(0,len(ustopcities.columns)):  #for each column
        ustopcities.iloc[i,j] = re.sub('\[.*?\]','',ustopcities.iloc[i,j])  #remove annotation symbols


# ### Clean and Convert the Values in the `Population Change Percentage` Column to Float Format

# In[16]:


pop = ustopcities.columns.get_loc("Population Change Percentage") #find and store the index of the 'Population Change Percentage' column

for i in range(0,len(ustopcities)):    #for each value
    ustopcities.iloc[i,pop] = re.sub('\[.*?\]|[+]|[%]','',ustopcities.iloc[i,pop])  #remove redundant data and symbols
    ustopcities.iloc[i,pop] = re.sub('−','-',ustopcities.iloc[i,pop]) #change the negative symbol for further transformation
    if ustopcities.iloc[i,pop] != "": #if the value is not null
        ustopcities.iloc[i,pop] = float(ustopcities.iloc[i,pop])  #transform the value into float format


# ### Clean and Convert the Values in the `areas` Column to Float Format

# In[17]:


areas = ['Land Area2016','Land Area Latest', 'Water Area Latest', 'Metro Area Latest', 'Urban Area Latest']  #create a list to contain the column names

for area in areas:  #for each area column
    index = ustopcities.columns.get_loc(area)  #find and store the index of the column
    for i in range(0,len(ustopcities)):    #for each value
        ustopcities.iloc[i,index] = re.sub('sq|mi|\(.*?\).*?$|\[.*?\]|,|[A-Za-z]+|:|–|\\xa0.*?$','',ustopcities.iloc[i,index])  #remove redundant data and symbols
        if 'km2' in ustopcities.iloc[i,index]:   #if the remaining data's unit is in km2
            ustopcities.iloc[i,index] = re.sub('km2','',ustopcities.iloc[i,index])  #remove the text km2
            ustopcities.iloc[i,index] = round(float(ustopcities.iloc[i,index])*0.386102,2)  #transform the data into square miles
        if ustopcities.iloc[i,index] != "" and area != 'Urban Area Latest':    #for strings that are not empty in the first three columns
            ustopcities.iloc[i,index] = float(ustopcities.iloc[i,index])        #transform the value into float format


# ### Clean and Convert the Values in the `Population Density2016` Column to Integer Format

# In[18]:


den = ustopcities.columns.get_loc("Population Density2016") #find and store the index of the 'Population Density2016' column

for i in range(0,len(ustopcities)):    #for each value
    ustopcities.iloc[i,den] = re.sub('\/sq|mi|,','',ustopcities.iloc[i,den])  #remove redundant data and symbols
    ustopcities.iloc[i,den] = int(ustopcities.iloc[i,den])  #transform the value into integer format


# ### Clean the Values in the `Location` Column

# In[19]:


loc = ustopcities.columns.get_loc("Location") #find and store the index of the 'Location' column

for i in range(0,len(ustopcities)):    #for each value
    ustopcities.iloc[i,loc] = re.sub('\/.*?$','',ustopcities.iloc[i,loc]) #remove redundant and duplicated data


# ### Clean and Convert the Values in the `Elevation` Column to Integer Format

# In[20]:


ele = ustopcities.columns.get_loc("Elevation") #find and store the index of the 'Elevation' column

for i in range(0,len(ustopcities)):    #for each value
    ustopcities.iloc[i,ele] = re.sub('\(.*?\).*?$|ft|,|\[.*?\]','',ustopcities.iloc[i,ele])  #remove redundant data and symbols
    ustopcities.iloc[i,ele] = re.sub('\sto\s|-|–|\s-\s',',',ustopcities.iloc[i,ele]) #change the seperation symbol to ','
    if 'm' in ustopcities.iloc[i,ele]:   #if the remaining data's unit is in m
        ustopcities.iloc[i,ele] = re.sub('m','',ustopcities.iloc[i,ele])  #remove the text m
        ustopcities.iloc[i,ele] = round(float(ustopcities.iloc[i,ele])*3.28084,0)  #transform the data into feet
    if ustopcities.iloc[i,ele] != "": #if the value is not null
        try:
            ustopcities.iloc[i,ele] = int(round(float(ustopcities.iloc[i,ele]),1))  #transform the value into integer
        except:
            lst = ustopcities.iloc[i,ele].split(',') #for values that contain a range of evelation
            lst[0] = lst[0].replace('−','-')
            lst[1] = lst[1].replace('\xa0 ','')
            ustopcities.iloc[i,ele] = int((float(lst[0])+float(lst[1]))/2) #calculate the average evelation and transform to integer
            


# Lastly, in order to make this data frame suitable for BigQuery, I adjusted the data and file format to follow the requirements:
# 
# - Values in TIMESTAMP columns must be in the following format: YYYY-MM-DD (year-month-day) hh:mm:ss (hour-minute-second)
# - The CSV file should be UTF-8 encoded
# - When using the classic BigQuery web UI, files loaded from a local data source must be 10 MB or less and must contain fewer than 16,000 rows.
# 
# ### Clean and Convert the Values in the `Incorporated` Column to TIMESTAMP Format
# 
# In order the modify the data format in the `Incorporated` column, I wrote a loop to iterate through every row, remove redundant symbols, and transform the original data into datetime format as `YYYY-MM-DD hh:mm:ss`.

# In[21]:


incop = ustopcities.columns.get_loc('Incorporated')     #find and store the index of the column Incorporated
dlist = []    #build a new list to store the index of the rows that have raised exceptions
for i in range(0,len(ustopcities)):     #for each row in the data frame
    ustopcities.iloc[i,incop] = re.sub('\[.*?\]|\s\(.*?\)|\(.*?$|,\s[a-z].*$|\s[a-z].*$|;\s[1-9].*?$|:[1-9].*?$','',ustopcities.iloc[i,incop]) #remove meaningless symbols
    try:     #use try-except block to catch exceptions
        ustopcities.iloc[i,incop] = pd.to_datetime(ustopcities.iloc[i,incop])  #transform the data into datetime format
    except:
        print(i,ustopcities.iloc[i,incop])  #if there appears any exceptions, print out the row index and value
        dlist.append(i)  #add the row indexes into the list


# After inspecting the data that cannot be transformed into datetime format, there appears to be numerous years and dates in the row because some cities are first incorporated as town and then as cities. Therefore, I decided to use the latest year and transform them into datetime.

# In[22]:


for i in dlist:  #for each row in the list
    dlength = len(ustopcities.iloc[i,incop])   #calculate the length of the string in the row
    ustopcities.iloc[i,incop] = pd.to_datetime(ustopcities.iloc[i,incop][dlength-4:],errors='coerce')  #select the last 4 digitd and transform it into datetime format, remaining errors are coerced


# **The final dataset contains 314 rows representing 314 top cities in the United States and 29 columns including 6 integer variables, 5 float variables, 1 TimeStamp variable, and 17 string variables.**

# In[23]:


ustopcities.describe()   #inspect the summary of ustopcities


# ### export CSV file with UTF-8 encoding
# 
# Finally, I exported the data frame `ustopcities` into a CSV file that is UTF-8 encoded and set the `index` as False. The resulting CSV file contains 314 rows and 29 columns with a size of 336KB, which is ready to be uploaded to a BigQuery table.

# In[24]:


ustopcities.to_csv('TopUSCities_Yirou.csv',encoding='utf-8', index=False)


# In[ ]:




