import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
import random
from tqdm import tqdm

s = requests.session()       
s.keep_alive = False


def get_ret(url, headers, times=20):
    for i in range(times):
        try:
            return requests.get(url, headers=headers)
        except:
            pass
        time.sleep(random.random())
    print (f'url "{url}" not get')
    return None

def find_usr(url='https://www.metacritic.com/game/playstation-4/the-last-of-us-part-ii/user-reviews?sort-by=date&num_items=100',n_iter=10):
    
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}
    
    score_list = []
    usr_list = []
    commit_list = []
    for i in range(n_iter):
        url_now = url + f'&page={i}'
        
        ret = get_ret(url_now, headers)
        if ret == None:
            print ('page Error:', i)
            continue
        print (f'page {i} get ret')
        soup = BeautifulSoup(ret.text, 'html.parser')
    
        scores = soup.find_all('div', class_="review_grade")[:-3]
        score_list += [int(score.find('div').string) for score in scores]
        
        commits = soup.find_all('div', class_="review_body")[:-3]
        commit_list += [commit.text for commit in commits]
        commit_length_list = [len(commit.split()) for commit in commit_list]
        
        users = soup.find_all('div', class_='review_critic')[:-3]

        for user in tqdm(users):
            
            usr_url = 'https://www.metacritic.com' + user.a['href']
            name = user.a.text
            rates = 0
            reviews = 0
            flag = False
            
            for i in range(10):
                try:
                    usr_ret = requests.get(usr_url, headers=headers)
                    usr_soup = BeautifulSoup(usr_ret.text, 'html.parser')
                    rates = int(usr_soup.find('span', class_='total_summary_reviews').span.text)
                    reviews = int(usr_soup.find('span', class_='total_summary_ratings mr20').span.text)
                    flag = True
                    break
                except:
                    pass
            if flag == False:
                print ('user Error:', name)
                
            usr_list.append((rates, reviews, name, flag))
            time.sleep(random.random() * 0.6)
            
        length_count = [[] for _ in range(11)]             
        rates_count = [[] for _ in range(11)]
        reviews_count = [[] for _ in range(11)]
        
        for i in range(len(score_list)):
            score = score_list[i]
            rates_count[score].append(usr_list[i][0])
            
            reviews_count[score].append(usr_list[i][1])
            length_count[score].append(commit_length_list[i])
          
        tmp = np.array(score_list)          
        df = [(sum(tmp==i), str(round(sum(tmp==i) * 100./len(tmp), 1))+'%', round(np.mean(length_count[i]), 1), 
               round(np.mean(rates_count[i]), 1), round(np.mean(reviews_count[i]), 1)) for i in range(11)]
        df = pd.DataFrame(df)
        df.index.name = 'score'
        df.columns = ['count', 'percentage', 'average commit length', 'average usr rates', 'average usr reviews']
        yield df, score_list, commit_list, usr_list
        time.sleep(random.random() * 3)
        
output_path = 'output/death stranding/'
results = []
for i, result in enumerate(find_usr(url='https://www.metacritic.com/game/playstation-4/death-stranding/user-reviews?sort-by=date&num_items=100', 
                               n_iter=10)):
    df = result[0]
    df.to_csv(output_path+f'death-stranding_df_latest_{i}_pages.csv')
    print (f'death-stranding_df_latest_{i}_pages.csv saved')
    results.append(result)
 
output_path = 'output/red dead redemption 2/'
results2 = []
for i, result in enumerate(find_usr(url='https://www.metacritic.com/game/playstation-4/red-dead-redemption-2/user-reviews?sort-by=date&num_items=100', 
                               n_iter=30)):
    df = result[0]
    df.to_csv(output_path+f'red-dead-redemption-2_df_latest_{i}_pages.csv')
    print (f'red-dead-redemption-2_df_latest_{i}_pages.csv saved')
    results2.append(result)
    
output_path = 'output/tlou2/'
results3 = []
for i, result in enumerate(find_usr(n_iter=120)):
    df = result[0]
    df.to_csv(output_path+f'tlou2_df_latest_{i}_pages.csv')
    print (f'tlou2_df_latest_{i}_pages.csv saved')
    results3.append(result)
