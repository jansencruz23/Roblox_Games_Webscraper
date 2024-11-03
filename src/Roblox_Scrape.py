import re
import sys
import csv
from datetime import datetime
from requests_html import HTMLSession

def get_game_category():
    game_categories = ['Trending in Simulation', 
                       'Trending in Social', 'Trending in Sports & Racing', 'Trending in Strategy',
                       'Trending in Survival']
    return game_categories[int(sys.argv[1])]

def get_game_xpaths():
    xpaths = []
    #There are 15 different categories on roblox discover main page
    for count in range(3, 19):
        xpaths.append(f'//*[@id="games-carousel-page"]/div/div/div[{count}]/div[2]/div/div[1]/ul')
    return xpaths

def get_game_urls(session, option: int):
    xpaths = get_game_xpaths()
    print(f"Using XPath: {xpaths[option]}")
    element = session.html.xpath(xpaths[option], first=True)
    if element is None:
        print("No element found for the given XPath.")
    return element

def get_current_time():
    return str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

#Scrapes attributes 'Active Users', 'Favorites', 'Total Visits', 'Voice Chat', 'Camera', and etc.
def get_game_attributes(session: HTMLSession):   
    try:
        attributes = session.html.find('p.text-lead.font-caption-body')
        attribute_list = []
        index = 0

        for attribute in enumerate(attributes):
            try:
                if index >= 9: 
                    continue

                attribute_list.append(attribute[1].text)
                index += 1
            except Exception as ex:
                attribute_list.append(ex)
        return attribute_list
    except Exception as e:
        print(e)
        return e

def get_game_title(session: HTMLSession):
    try:
        html_title = session.html.find('h1.game-name')
        title = html_title[0].text
        return title
    except:
        return '-'
    
def get_age_recommendation(session: HTMLSession):
    try:
        html_title = session.html.find('#game-age-recommendation-container > a')
        title = html_title[0].text
        return title
    except Exception as e:
        return e

def get_creator_name(session: HTMLSession):
    try:
        creator_by_name = session.html.find('div.game-creator', first=True).text
        creator = re.search('(?<=By ).*', creator_by_name)
        return creator.group(0)
    except:
        return '-'

def get_gameid(game_url: str):
    game_ID_list = re.findall('[\d]*', game_url)
    for gameID in game_ID_list:
        if(len(gameID) > 6):
            return gameID
    return '-'

def get_game_description(session: HTMLSession):
    try:
        html_description = session.html.find('pre.text.game-description.linkify')
        game_description = html_description[0].text
        game_description = game_description.replace('\n','')
        return game_description
    except:
        return '-'

def remove_special_characters(data: list):
    cleaned_data = []
    for item in data:
        cleaned_item = str(item).replace('\"','').replace('\'','').replace('|','').replace('\n','').replace(',','')
        cleaned_data.append(cleaned_item)
    return cleaned_data

def validate_game_data(session:HTMLSession, data:list):
    if(len(data)==14):
        return data
    else:
        print('\n\n ERROR: ROW DID NOT HAVE CORRECT NUMBER OF FEATURES \n\n')
        with open('../data/incompleteData.txt', 'a', newline='', encoding='utf-8') as f:
            f.write(session.text)
            for attribute in data:
                f.write(attribute)
    return []

def data_logger(data:list, game_category:str):
    current_time = get_current_time()

    if(len(data)<=1):
        with open('./data/dataLogs.txt', 'a', newline='', encoding='utf-8') as f:
            final_output = 'Error: No rows written for category "'+game_category+ '" at time '+current_time+'\n'
            f.write(final_output)
        return 
    else:
        with open('./data/dataLogs.txt', 'a', newline='', encoding='utf-8') as f:
            final_output = 'Success: Category "'+game_category+'" at time '+current_time+ ' was entered correctly.'+'\n'
            f.write(final_output)
        return

def write_data_to_csv(data: list):
    file_creation_time = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
    file_location = './data/'+file_creation_time+'.csv'
    head = 'Date|Active Users|Favorites|Total Visits|Voice Chat|Camera|Date Created|Last Updated|Server Size|Genre|Title|Creator|Age Recommendation|gameID|Category|URL\n'

    with open(file_location, 'a', newline='', encoding='utf-8') as f:
        f.write(head)
        output = csv.writer(f, delimiter='|')
        output.writerows(data)
    print('pass!')
    return 