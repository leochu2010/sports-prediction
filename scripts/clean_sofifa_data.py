
# coding: utf-8

# In[2]:

def get_cleaned_sofifa_data():

    import pandas as pd

    sofifa_df = pd.read_csv('../data/sofifa/sofifia-english-league-championship.csv')
    
    
    # In[3]:
    
    sofifa_df.head()
    
    
    # In[4]:
    
    sofifa_df['sofifa_team_id']=sofifa_df['clubs-href'].str.extract('(\d+)',expand=False).astype(int)
    sofifa_df.drop('clubs-href',axis=1,inplace=True)
    
    sofifa_df.drop(['web-scraper-order'],axis=1,inplace=True)
    
    
    # In[5]:
    
    #clean transfer budget
    sofifa_df[['transfer_budget_num','transfer_budget_amount']]=sofifa_df['transfer_budget'].str.extract('€\s+(\d+\.?\d?)(\D)',expand=False)
    
    #make sure only M and K
    #sofifa_df.loc[sofifa_df['transfer_budget_amount'].str.contains('M|K')==False]['transfer_budget_amount']
    
    sofifa_df['transfer_budget_num']=sofifa_df['transfer_budget_num'].astype(float)
    sofifa_df['transfer_budget_total']=sofifa_df['transfer_budget_num']
    sofifa_df.loc[sofifa_df.transfer_budget_amount == 'M','transfer_budget_total'] = 100000*sofifa_df['transfer_budget_num']
    sofifa_df.loc[sofifa_df.transfer_budget_amount == 'K','transfer_budget_total'] = 1000 * sofifa_df['transfer_budget_num']
    #sofifa_df[['transfer_budget','transfer_budget_total','transfer_budget_num','transfer_budget_amount']].head()
    
    sofifa_df.drop(['transfer_budget','transfer_budget_num','transfer_budget_amount'],axis=1,inplace=True)
    #double check if K can be multiplied by 1000
    #sofifa_df.loc[sofifa_df.transfer_budget_amount == 'K']['transfer_budget_total']
    
    
    # In[6]:
    
    #extract last_update_datetime
    sofifa_df[['fifa_edition','last_update']]=sofifa_df['edition_date'].str.extract('(.*)\s+(\D+\s\d+\,\s+\d+)',expand=False)
    sofifa_df['last_update_datetime']=pd.to_datetime(sofifa_df['last_update'])
    sofifa_df.drop(['fifa_edition_date','fifa_edition_date-href','edition_date','last_update'],axis=1,inplace=True)
    sofifa_df[['fifa_edition','last_update_datetime']].head()
    
    
    # In[7]:
    
    sofifa_df[['clubs','starting_avg_age','whole_team_avg_age']].head()
    
    
    # In[8]:
    
    #clean ages
    sofifa_df['starting_avg_age']=sofifa_df['starting_avg_age'].str.extract('Starting 11 average age\\n(\d+\.?\d+?)',expand=False).astype(float)
    sofifa_df['whole_team_avg_age']=sofifa_df['whole_team_avg_age'].str.extract('(\d+\.?\d?)',expand=False).astype(float)
    sofifa_df[['clubs','starting_avg_age','whole_team_avg_age']].head()
    
    
    # In[9]:
    
    #Clean the following metrics and convert to interger data type
    def extractNumberFromFifaMetrix(df,column):
        df.loc[df[column] == 'null',column]='0'
        df[column]=sofifa_df[column].str.extract('(\d+)',expand=False)
        df[column].fillna(value='0', inplace=True)
        df[column]=sofifa_df[column].astype(int)
        
    extractNumberFromFifaMetrix(sofifa_df,'build_up_play_speed')
    extractNumberFromFifaMetrix(sofifa_df,'build_up_play_dribbling')
    extractNumberFromFifaMetrix(sofifa_df,'build_up_play_passing')
    extractNumberFromFifaMetrix(sofifa_df,'chance_creation_passing')
    extractNumberFromFifaMetrix(sofifa_df,'chance_creation_crossing')
    extractNumberFromFifaMetrix(sofifa_df,'chance_creation_shooting')
    extractNumberFromFifaMetrix(sofifa_df,'defence_pressure')
    extractNumberFromFifaMetrix(sofifa_df,'defence_aggression')
    extractNumberFromFifaMetrix(sofifa_df,'defence_team_width')
    
    
    # In[10]:
    
    sofifa_df[list(sofifa_df.columns[0:10])].head()
    
    
    # In[11]:
    
    sofifa_df[list(sofifa_df.columns[10:20])].head()
    
    
    # In[12]:
    
    sofifa_df[list(sofifa_df.columns[20:30])].head()
    
    
    # In[13]:
    
    sofifa_df[['sofifa_team_id','clubs']].groupby(['sofifa_team_id','clubs']).count()
    
    
    # In[14]:
    
    sofifa_to_whoscored_team_id_dict={
    2:24,
    1932:142,
    88:157,
    3:158,
    1925:189,
    1808:211,
    1919:182,
    15015:1786,
    1961:188,
    91:20,
    144:170,
    1939:166,
    94:165,
    8:19,
    13:23,
    1792:168,
    14:174,
    1801:181,
    15:171,
    1793:94,
    1797:210,
    1807:25,
    1917:194,
    110:161}
    sofifa_df["whoscored_team_id"]=sofifa_df["sofifa_team_id"].replace(sofifa_to_whoscored_team_id_dict)
    sofifa_df[['sofifa_team_id','clubs','whoscored_team_id','fifa_edition']].groupby(['sofifa_team_id','clubs','whoscored_team_id']).count()
    
    return sofifa_df