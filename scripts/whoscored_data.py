# coding: utf-8

def clean_whoscored_data(data_csv='../data/whoscored/whoscored_10000_matches.csv', tournment_id=7):

    import pandas as pd
        
    df = pd.read_csv(data_csv)
    
    print('all matchs:',df.shape)
    df = df.loc[df['home_possession'] != 'null']
    print('all detailed matchs:',df.shape)

    df['match_id']=df['match_report-href'].str.extract('(\d+)',expand=False).astype(int)
    df.drop('match_report-href',axis=1,inplace=True)
    df=df.sort_values(by='match_id', ascending=1)

    df['home_team_id']=df['home_team-href'].str.extract('(\d+)',expand=False).astype(int)
    df['away_team_id']=df['away_team-href'].str.extract('(\d+)',expand=False).astype(int)
    df.drop(['home_team-href','away_team-href'],axis=1,inplace=True)
    df['tournament_id']=df['tournament-href'].str.extract('Tournaments\/(\d+)',expand=False).astype(int)
    df.drop(['tournament-href'],axis=1,inplace=True)

    df = df.loc[df['tournament_id'] == tournment_id]

    # convert percentage to fraction
    import numpy as np
    df['away_possession']=df['away_possession'].replace('%','',regex=True).astype('float')/100
    df['home_possession']=df['home_possession'].replace('%','',regex=True).astype('float')/100
    df['away_aerial_duel_success']=df['away_aerial_duel_success'].replace('%','',regex=True).astype('float')/100
    df['home_aerial_duel_success']=df['home_aerial_duel_success'].replace('%','',regex=True).astype('float')/100
    df['home_pass_success']=df['home_pass_success'].replace('%','',regex=True).astype('float')/100
    df['away_pass_success']=df['away_pass_success'].replace('%','',regex=True).astype('float')/100

    # extract home and away goal
    df_ht=df['half_time'].str.split(':',expand=True)
    df_ht.columns=['home_half_time_goal','away_half_time_goal']
    df_ft=df['full_time'].str.split(':',expand=True)
    df_ft.columns=['home_full_time_goal','away_full_time_goal']

    df = pd.concat([df, df_ht], axis=1, join_axes=[df.index])
    df = pd.concat([df, df_ft], axis=1, join_axes=[df.index])

    # change data type to integer
    df['home_full_time_goal']=df['home_full_time_goal'].astype(int)
    df['away_full_time_goal']=df['away_full_time_goal'].astype(int)
    df['home_half_time_goal']=df['home_half_time_goal'].astype(int)
    df['away_half_time_goal']=df['away_half_time_goal'].astype(int)
    df['home_shots']=df['home_shots'].astype(int)
    df['away_shots']=df['away_shots'].astype(int)
    df['home_shots_on_target']=df['home_shots_on_target'].astype(int)
    df['away_shots_on_target']=df['away_shots_on_target'].astype(int)
    df['home_dribbles_won']=df['home_dribbles_won'].astype(int)
    df['away_dribbles_won']=df['away_dribbles_won'].astype(int)
    df['home_tackles']=df['home_tackles'].astype(int)
    df['away_tackles']=df['away_tackles'].astype(int)
    
    #pase date
    df['date']=pd.to_datetime(df['date'])

    #find goal difference
    df['half_time_goal_diff']=df['home_half_time_goal']-df['away_half_time_goal']
    df['full_time_goal_diff']=df['home_full_time_goal']-df['away_full_time_goal']

    return df
