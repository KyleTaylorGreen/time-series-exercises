import os
import pandas as pd
import datetime

my_path = '/Users/kylegreen/codeup-data-science/time-series-exercises/riot_api_data/'
_, _, filenames = next(os.walk(my_path), (None, None, []))
print(filenames)
count= 0
sum = 0
total_df = pd.DataFrame()
def our_files():
    for filename in filenames:
        if 'histories' in filename:
            count+=1
            histories_df = pd.read_csv(my_path+filename)
            
            for col in histories_df.columns:
                if 'Unnamed' in col:
                    histories_df.drop(columns=col, inplace=True)
            
            total_df = pd.concat([total_df, histories_df])
            
        
def drop_duplicates():
    total_df = pd.read_csv('all_stats.csv')
    total_df = total_df.drop_duplicates()
    total_df.to_csv(my_path+'all_stats.csv', index=False)

    print(total_df)

def read_stats(filename):
    return pd.read_csv(filename)

def time_columns():
    stats = read_stats('/Users/kylegreen/codeup-data-science/time-series-exercises/riot_api_data/NA1_4169245913_histories.csv')
    columns= [col for col in stats.columns]
    #stats.game_end = stats.game_end.fillna(0)
    print(stats.game_end)
    stats['game_end'] = stats.apply(lambda x: datetime.datetime.fromtimestamp((x.game_start + x.game_duration)/1000) if x.game_end else datetime.datetime.fromtimestamp(x.game_end / 1000), axis=1)
    stats['game_start'] = stats.game_start.apply(lambda x: datetime.datetime.fromtimestamp(x/1000))
   # stats['game_duration'] = stats.apply(lambda x: x.game_end - x.game_start, axis=1)
    stats['game_duration'] = stats.apply(lambda x: pd.Timedelta(x.game_end - x.game_start).seconds / 60.0, axis=1)
    stats = stats.sort_values(by=['summoner_name', 'game_start'], ascending=False)
    #print(pd.Timedelta(stats.game_end.iloc[1,] - stats.shift(1).game_start.iloc[1,]).seconds/60 < 45)
    #stats['is_session'] = stats.apply(lambda x: 1 if pd.Timedelta(x.game_end - x.shift(-1).game_start).seconds/60 < 45 and x.summoner_name == x.shift(1).summoner_name else 0, axis=1)
    stats['time_between_games'] = (stats['game_start'] - stats.shift(-1)['game_end']).apply(lambda x: pd.Timedelta(x).seconds/60)
    another_df = stats.shift(-1)
    print(another_df)
    stats['same_player_as_prev'] = stats['summoner_name'] == another_df['summoner_name']
    #print(stats.time_between_games)
    #print(stats.same_player_as_prev)
    stats['is_session'] = stats.apply(lambda x: True if x.time_between_games < 45 and x.same_player_as_prev == True else False, axis=1)
    #print(stats.is_session)
    columns.append('is_session')
    columns.append('time_between_games')

    def make_session_counts(df):
        truth_counter= 0
        session_series = []
        
        for x in df.is_session:

            if x == True:
                truth_counter += 1
            else:
                for i in range(truth_counter, -1, -1):
                    session_series.append(i)
                truth_counter = 0

        return session_series
    
    total_df = stats[columns]

    session = make_session_counts(total_df)
    total_df['session_count'] = [num+1 for num in session]

    
    return total_df
