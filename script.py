# import libraries
import sys
import requests
import pandas as pd
from bs4 import BeautifulSoup

# import missing cities file
try:
    input = sys.argv[1]
except:
    input = 'input.csv'

try:
    output = sys.argv[2]
except:
    output = 'output.csv'

df = pd.read_csv(input)

# create CIK list
CIK_list = []
for index, row in df.iterrows():
    CIK_list.append(row['CIK'])

# create year list
year_list = []
for index, row in df.iterrows():
    year_list.append(row['Year'])

# determines whether mail line contains city and state


def address_zip(x):
    y = (x[::-1]).strip()
    try:
        if (y[:5].isnumeric() and y[5] == ' ' and y[6:8].isalpha() and y[8] == ' '):
            return True
        else:
            return False
    except:
        return False

# alternate formula to determines whether mail line contains city and state


def address_zip2(x):
    y = (x[::-1]).strip()
    try:
        if (y[:4].isnumeric() and y[4] == '-' and y[5:10] and y[10] == ' ' and y[11:13].isalpha() and y[13] == ' '):
            return True
        else:
            return False
    except:
        return False


# base URL for the SEC EDGAR browser
endpoint = r"https://www.sec.gov/cgi-bin/browse-edgar"

# initalize our list for storage
city_list = []
state_list = []
link_list = []
form_list = []
date_list = []

for i in range(len(CIK_list)):

    # define our parameters dictionary
    param_dict = {'action': 'getcompany',
                  'CIK': CIK_list[i],
                  'type': '10-Q',
                  'dateb': str(year_list[i]) + '1231',
                  'owner': 'exclude',
                  'output': 'atom',
                  'count': '10'}

    # request the url, and then parse the response
    response = requests.get(url=endpoint, params=param_dict)
    soup = BeautifulSoup(response.content, 'lxml')
    entry = soup.find('entry')

    # find the latest entry in the year
    if entry == None:
        param_dict['type'] = ''
        response = requests.get(url=endpoint, params=param_dict)
        soup = BeautifulSoup(response.content, 'lxml')
        entry = soup.find('entry')

    # go forward 1 year and find the earliest entry
    if entry == None:
        try:
            param_dict['dateb'] = str(year_list[i] + 1) + '1231'
            # 100 is the highest value possible for count
            param_dict['count'] = '100'
            response = requests.get(url=endpoint, params=param_dict)
            soup = BeautifulSoup(response.content, 'lxml')
            entry = soup.find_all('entry')[-1]
        except:
            entry = ''

    # find link, form, & date
    try:
        link = entry.find('content').find('filing-href').text
        form = entry.find('content').find('filing-type').text
        date = entry.find('content').find('filing-date').text
    except:
        link = ''
        form = ''
        date = ''

    # finding city & state
    if link == '':
        city = ''
        state = ''
    else:
        # request the link url to parse for city & state info
        child_response = requests.get(url=link)
        child_soup = BeautifulSoup(child_response.content, 'html.parser')
        addresses = child_soup.find_all('div', id='filerDiv')

        # to ensure the right company addresses are selected
        sub_string = str(CIK_list[i]) + ' (see all company filings)'
        for add in addresses:
            if sub_string in str(add):
                company_addresses = add
        company_addresses = company_addresses.find_all('div', class_='mailer')

        # finding business and mailing lines
        for c_add in company_addresses:
            if 'Business Address' in str(c_add):
                business_lines = c_add.find_all('span')
            elif 'Mailing Address' in str(c_add):
                mailing_lines = c_add.find_all('span')

        # assigning city & state
        city = ''
        state = ''

        for line in business_lines:
            if address_zip(line.text):
                city = line.text.strip()[:-9]
                state = line.text.strip()[-8:-6]
            elif address_zip2(line.text):
                city = line.text.strip()[:-14]
                state = line.text.strip()[-13:-11]

        if city == '' and state == '':
            for line in mailing_lines:
                if address_zip(line.text):
                    city = line.text.strip()[:-9]
                    state = line.text.strip()[-8:-6]
                elif address_zip2(line.text):
                    city = line.text.strip()[:-14]
                    state = line.text.strip()[-13:-11]

    # assigning values to list
    city_list.append(city)
    state_list.append(state)
    link_list.append(link)
    form_list.append(form)
    date_list.append(date)


# assigning columns to df dataset
df['City'] = city_list
df['new_state'] = state_list
df['SEC Filing'] = link_list
df['Form Type'] = form_list
df['Date Filed'] = date_list

# export dataset for manual analysis and to double check work
df.to_csv(output, encoding='utf-8', index=False)
