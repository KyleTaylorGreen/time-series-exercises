import os
import pandas as pd
import numpy as np
import datetime

my_path = '/Users/kylegreen/codeup-data-science/time-series-exercises/riot_api_data/'
_, _, filenames = next(os.walk(my_path), (None, None, []))

def create_player_histories():
    my_path = '/Users/kylegreen/codeup-data-science/time-series-exercises/riot_api_data/'
    _, _, filenames = next(os.walk(my_path), (None, None, []))
    
    if os.path.isfile(my_path + 'all_stats_histories.csv'):
        return pd.read_csv(my_path+ 'all_stats_histories.csv')
    
    else:
        total_df = pd.DataFrame()
        for filename in filenames:
            if 'histories' in filename:
                histories_df = pd.read_csv(my_path+filename)
                
                for col in histories_df.columns:
                    if 'Unnamed' in col:
                        histories_df.drop(columns=col, inplace=True)
                
                total_df = pd.concat([total_df, histories_df])
   
    total_df= total_df.drop_duplicates()
    total_df.to_csv(my_path+'all_stats_histories.csv', index=False)
    return total_df


def drop_duplicates():
    total_df = pd.read_csv('all_stats_histories.csv')
    total_df = total_df.drop_duplicates()
    total_df.to_csv(my_path+'all_stats_histories.csv', index=False)

    print(total_df)

def read_stats(filename):
    return pd.read_csv(filename)

def time_columns(filename):
    stats = read_stats(f'/Users/kylegreen/codeup-data-science/time-series-exercises/riot_api_data/{filename}')
    columns= [col for col in stats.columns]
    #stats.game_end = stats.game_end.fillna(0)
    #print(stats.game_end)
    stats['game_end'] = stats.apply(lambda x: x.game_start + (x.game_duration * 1000), axis=1)
   # stats['game_duration'] = stats.apply(lambda x: x.game_end - x.game_start, axis=1)
    stats = stats.sort_values(by=['summoner_name', 'game_start'], ascending=False)
    #print(pd.Timedelta(stats.game_end.iloc[1,] - stats.shift(1).game_start.iloc[1,]).seconds/60 < 45)
    #stats['is_session'] = stats.apply(lambda x: 1 if pd.Timedelta(x.game_end - x.shift(-1).game_start).seconds/60 < 45 and x.summoner_name == x.shift(1).summoner_name else 0, axis=1)
    stats['time_between_games'] = (stats['game_start'] - stats.shift(-1)['game_end']) / 1000 / 60
    another_df = stats.shift(-1)
    print(another_df)
    stats['same_player_as_prev'] = stats['summoner_name'] == another_df['summoner_name']
    #print(stats.time_between_games)
    #print(stats.same_player_as_prev)
    stats['is_session'] = stats.apply(lambda x: True if x.time_between_games < 45 and x.same_player_as_prev == True else False, axis=1)
    #print(stats.is_session)
    columns.append('is_session')
    columns.append('time_between_games')
    columns.append('game_end')

    def make_session_counts(df):
        truth_counter= 1
        session_series = []
        session_cnt = 0
        sessions = [[]]
        wins_losses = []
        copy= [[]]

        win_counter = 0
        loss_counter = 0
        num_of_wins_in_session = 1
        
        for i, x in enumerate(df.is_session):
            if x == True:
                if df.win.iloc[i]:
                    win_counter +=1
                else:
                    loss_counter +=1
                truth_counter += 1
                sessions[session_cnt].append(i)
            else:
                for k in range(truth_counter, 0, -1):
                    session_series.append(k)
                
                truth_counter = 1
                sessions[session_cnt].append(i)
                sessions.append([])
                session_cnt+=1

        copy = sessions[:][:]
        counter = 0
        for l, session in enumerate(sessions):
            copy[l] = np.array(copy[l])

            for k, game in enumerate(session):
                print(counter)
                print(df.win.iloc[counter])
                if df.win.iloc[counter]:
                    copy[l][k] = 1
                else:
                    copy[l][k] = 0
                counter+=1
            copy[l] = np.flip(copy[l])
            copy[l] = np.cumsum(copy[l])
            copy[l] = np.flip(copy[l])

        copy = copy[:-1]
        final_wins = [elem for elements in copy for elem in elements]
        #print(final_wins)
        #print(session_series)
        print(len(final_wins))

        return session_series, final_wins

    total_df = stats[columns]
    total_df = total_df.reset_index()

    our_session, final_wins = make_session_counts(total_df)
    print(len(our_session))
    total_df['session_count'] = our_session
    total_df['session_wins']  = final_wins
    total_df['session_losses']= total_df.session_count - total_df.session_wins

    return total_df
