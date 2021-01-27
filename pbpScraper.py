import requests
from bs4 import BeautifulSoup
import pandas as pd
import unidecode

def makeSoup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup

#Prompt the user to enter the years for the scrape
start_year = input('----Input the Start Year:  ')
stop_year = input('----Input the Final Year:  ')
years = range(int(start_year),int(stop_year)+1)

#Nonconfigurable for now:
months = [
#'october', 
#'november',
'december',
#'january',
#'february',
#'march',
#'april',
#'may',
#'june',
#'july',
#'august',
#'september'
]

#Create all the links to loop through
links = []
for year in years:
    for month in months:
        soup = makeSoup('https://www.basketball-reference.com/leagues/NBA_'+str(year)+'_games-'+month+'.html')
        links_tmp = ["https://www.basketball-reference.com" + game['href'] for game in soup.find_all('a', text='Box Score')]
        for link in links_tmp:
            links.append(link)

output = []
for link in links:
    soup = makeSoup(link)

    #Collect Game Data
    date = [str(item).replace(',','') for item in soup.find('h1').getText().split()][-3:]
    game_id = link[47:59]
    season_id = soup.findAll('u')[1].getText().split()[0]

    #Collect Starters:
    teams = [game['href'] for game in soup.find_all('a', {'itemprop': 'name'})]
    team1 = teams[0][7:10]
    team2 = teams[1][7:10]
    def get_starters(team):
        basic_stats = soup.find('table',{'id': 'box-'+team+'-game-basic'})
        player_names = [[th.get('data-append-csv') for th in basic_stats.findAll('tr')[1:][i].findAll('th')] for i in range(len(basic_stats.findAll('tr')[1:]))]
        starters = [player[0] for player in player_names[1:6]]
        return starters

    team1_starters = get_starters(team1)
    team2_starters = get_starters(team2)
    
    soup = makeSoup(link.replace('/boxscores','/boxscores/pbp'))

    pbpTable = soup.find('table',{'id': 'pbp'})
    pbpData = [[td.getText() for td in pbpTable.findAll('tr')[1:][i].findAll('td')]
           for i in range(len(pbpTable.findAll('tr')[1:]))]

    pbpData = [item for item in pbpData if len(item)>0] #Remove Blank Rows
    pbpData = [[game_id] + [season_id] + date + team1_starters + team2_starters + item[:4]
               for item in pbpData]
    pbpData_df = pd.DataFrame(pbpData)
    output.append(pbpData_df)
    break
output = pd.concat(output)
output.to_csv('pbpStats.csv',index=False)


    
    #Pull all Stats from table
#    posData = [[td.getText() for td in posTable.findAll('tr')[1:][i].findAll('td')]
#               for i in range(len(posTable.findAll('tr')[1:]))]

    #Cleaning Operations
#    posData = [item for item in posData if len(item)>0] #Remove Blank Rows
#    posData = [item for item in posData if item[3]!='TOT'] #Remove Cumulative Rows
#    posData = [[year] + item[:11] for item in posData] #Remove Unused Columns
#    for item in posData:
#        item[1] = unidecode.unidecode(item[1]).replace('*','').replace('.','')#Remove Special Characters
#        item[7] = item[7].replace('%','')
#        item[8] = item[8].replace('%','')
#        item[9] = item[9].replace('%','')
#        item[10] = item[10].replace('%','')
#        item[11] = item[11].replace('%','')

    #Convert list to Pandas Dataframe
#    posData_df = pd.DataFrame(posData)
#    output.append(posData_df)

#output = pd.concat(output)
#header = ['Year','Player','Pos','Age','Team','Games','MP','PG%','SG%','SF%','PF%','C%']
#output.columns = header

#output.to_csv('posStats.csv',index=False)
