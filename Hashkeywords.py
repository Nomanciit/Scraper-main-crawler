import snscrape.modules.twitter as sntwitter
import pandas as pd
import tweepy
import os
import datetime
import ast



class ScrapeData:
    def __init__(self):
    
        consumer_key = "ZSRMZCgmtfsa3FfLbslsREMPB"
        consumer_secret = "7O5jDknZ6hOFwhHnAIQIs5KmYYGWA5x2ZZf38A4k9FoaIE7hZt"
        access_token = "976412463460691968-fartQnLGNM0cn9lWnAt9rTg7Fxzv4OY"
        access_token_secret = "ATbMDgJjiSbCE1zKD0yaX8bHe6mcDOh0fwNh3qZjuockm"

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)
    
    def crawl_hashtags_keywords(self,search,start_date,end_date,limit):
        new_tweets_list = []
        new_search = search+" "+"since:"+""+start_date +" "+"until:"+""+end_date
        print(new_search)
        for i,tweet in enumerate(sntwitter.TwitterSearchScraper(new_search).get_items()):
            if i>limit:
                print(tweet)
                break
            new_tweets_list.append([tweet.url])
        print(new_tweets_list)
        data_frame = pd.DataFrame(new_tweets_list, columns=["URLS"])
        print("Length of the Dataset: ",len(data_frame))
#        path = "Macintosh HD\\Users\\hussainkhawaja\\Downloads\\test.csv"
        path = "test.csv"
        data_frame.to_csv(path)
        print("Data Stored Successfully----------------------------------------------")
        
        
    def crawl_more_features(self):
    
        
        # Open your text file/snscrape output
#        path = "Macintosh HD\\Users\\hussainkhawaja\\Downloads\\test.csv"
        print("inside --- Crawl function")
        path = "test.csv"
        tweet_url = pd.read_csv(path, index_col= None, header = None, names = ["links"])
        # Extract the tweet_id using .split function
        af = lambda x: x["links"].split("/")[-1]
        tweet_url['id'] = tweet_url.apply(af, axis=1)
        # Convert our tweet_url Series into a list
        ids = tweet_url['id'].tolist()

        # Process the ids by batch or chunks.
        total_count = len(ids)
        chunks = (total_count - 1) // 50 + 1
      
        # Username, date and the tweet themselves, so my code will only include those queries.
        def fetch_tw(ids):
            list_of_tw_status = self.api.lookup_statuses(ids, include_entities = True,tweet_mode= "extended")
            empty_data = pd.DataFrame()
            for status in list_of_tw_status:
                tweet_elem = {
                              "created_at":status.created_at,
                              "screen_name": status.user.screen_name,
                              "text":status.full_text,
                              'hashtags':status.entities['hashtags'],
                              'is_quote':status.is_quote_status,
                              "is_retweet":'',
                              "retweet_count": status.retweet_count,
                              "like_count": status.favorite_count,
                              "lang":status.lang,
                              'source':status.source,
                              "entities_normalizes_text":'',
                              "entities_type":'',
                              'mentions_screen_name':status.entities['user_mentions'],
                              "location":status.user.location,
                              "name":status.user.name,
                              "account_created_at":status.user.created_at,
                              "tweet_count":status.user.statuses_count,
                              'followers_count':status.user.followers_count,
                              'following_count':status.user.friends_count,
                              "description":status.user.description,
                              "Tweet_id": status.id_str,}
                empty_data = empty_data.append(tweet_elem, ignore_index = True)
            empty_data.to_csv("data.csv", mode="a")
        
        # Create another for loop to loop into our batches while processing 50 entries every loop
        for i in range(chunks):
            batch = ids[i*50:(i+1)*50]
            result = fetch_tw(batch)
        print("Data Downloaded Successfully----------------------------------------------")
        
    def get_url(self,id):
        url = "https://twitter.com/twitter/statuses/"
        url = url +str(id)
        return url
        
    def get_mentioned_names(self,mention):
        str_1 = ""
        try:
          res = ast.literal_eval(mention)
          for i in res:
            str_1 =str_1+" "+str(i['screen_name'])+","
          return str_1
        except Exception as e:
          print("Something went wrong",e)

    def get_hashtags_names(self,mention):
        str_1 = ""
        try:
          res = ast.literal_eval(mention)
          for i in res:
            str_1 =str_1+" "+str(i['text'])+","
          return str_1
        except Exception as e:
          print("Something went wrong",e)
        
    def get_data(self,search,start_date,end_date,limit):
        try:
            search = str(search)
            start_date = str(start_date)
            end_date = str(end_date)
            self.crawl_hashtags_keywords(search,start_date,end_date,limit)
            self.crawl_more_features()
            data = pd.read_csv("data.csv",lineterminator='\n',error_bad_lines=False)
            data['created_at'] = pd.to_datetime(data['created_at'],errors='coerce')
            data['created_at'] = data['created_at'].apply(lambda x: x + datetime.timedelta(hours=5))
            data=data[data['Tweet_id']!='Tweet_id']
            data['Tweet_urls'] = data['Tweet_id'].apply(self.get_url)
            data['mentions_screen_name'] = data['mentions_screen_name'].apply(self.get_mentioned_names)
            data['hashtags'] = data['hashtags'].apply(self.get_hashtags_names)
            data = data[["created_at", "screen_name", "text", "hashtags", "is_quote", "is_retweet",
                          "retweet_count", "like_count","lang","source","entities_normalizes_text",
                          "entities_type","mentions_screen_name","location","name","account_created_at",
                          "tweet_count","followers_count","following_count","description","Tweet_id","Tweet_urls"]]
            os.remove("data.csv")
            print("Data Saved Successfully--------")
            return data
        except Exception as e:
            print("Something went wrong while scraping data....",e)
            try:
                os.remove("data.csv")
            except:
                pass




