# Web Scraping: Top Cities in the United States

The files in this repo contain the codes to scrap data regarding the top cities in the United States from both the main Wikipedia page and each city's individual Wikipedia page. The codes are written in Python and are provided in the format of .py file, jupyter notebook, and HTML file for the purpose of easier reading and interpretation.

More specifically, three parts of codes are written including:
- Scraping data from the main wikipedia page
- Collecting additional information from each city's wikipedia page
- Adjusting the data and file format for BigQuery use

## Data Source

Main Wikipedia Page: https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population

Each City's Individual Wikipedia Page for 314 Top US Cities:

e.g. for New York City: https://en.wikipedia.org/wiki/New_York_City

You can find the full list of links in the `wikilinks` list created in the codes.

## Environment

In this assignment, I used the library `requests` to make HTTP requests and access the web page while using `BeautifulSoup` from the `bs4` package to parse the HTML and XML files to retrieve data. In addition, `pandsa` and `re` were also used to build and preprocess the dataset.

Please note that the libraries `requests` and `BeautifulSoup` need to be installed on your laptop first via terminal commands such as `pip3 install requests` before improting them.

## Resulting Dataset

The final dataset is stored in a CSV file which contains 314 rows representing 314 top cities in the United States and 29 columns containing the city's 28 characteristics and 1 description.

**It should be noted that all the areas in the data frame are measured in square miles and the population density is measured as the number of residents per unit of land area.**

The 29 variables include:

'Rank2018', 'City', 'State', 'Population Estimate2018', 'Population Estimate2010', 'Population Change Percentage',
'Land Area2016', 'Population Density2016', 'Location', 'Named For', 'Government Type', 'Mayor', 'Land Area Latest',
'Water Area Latest', 'Metro Area Latest', 'Elevation', 'Demonyms', 'Time Zone', 'Summer DST', 'Zip Codes','Area Codes', 
'FIPS Code', 'GNIS Feature Id', 'Website', 'County', 'Incorporated', 'Urban Area Latest', 'City Manager', 'Description'

## Variables Description
The variables in the dataset contain the following information:
1. The city rank by population as of July 1, 2018, as estimated by the United States Census Bureau
2. The city name
3. The name of the state in which the city lies
4. The city population as of July 1, 2018, as estimated by the United States Census Bureau
5. The city population as of April 1, 2010, as enumerated by the 2010 United States Census
6. The city percent population change from April 1, 2010, to July 1, 2018
7. The city land area as of January 1, 2016 (measured in square miles)
8. The city population density as of July 1, 2016 (residents per unit of land area (square mile))
9. The city latitude and longitude coordinates
10. The person that the city is named for
11. The city's government type
12. The name of the city mayor
13. The city land area as of latest (measured in square miles)
14. The city water area as of latest (measured in square miles)
15. The city metro area as of latest (measured in square miles)
16. The city's elevation
17. The demonyms of the city
18. The time zone that the city is in
19. The time zone during the summer time
20. The zip codes of the city 
21. The area codes of the city
22. The FIPS (Federal Information Processing Standards) code of the city
23. The GNIS (Geographic Names Information System) feature id of the city
24. The city's official website
25. The city's counties 
26. The date when the city was incorporated
27. The city urban area as of latest (measured in square miles)
28. The name of the city's city manager 
29. The brief description of the city
