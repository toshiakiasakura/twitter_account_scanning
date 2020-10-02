import tweepy
import json
import os
import glob
import requests 
import webbrowser

class AccountUtils():
    user = "@e_aki_ro" 
    path2data = "./data"
    profile_img_prefix = "https://pbs.twimg.com/profile_images" 
    default_keys = ["name", "screen_name", "id", "location", "profile_location",
         "description", "followers_count", "friends_count", "following"] 
    
    def set_api(self):
        """Set api instance using environmental variables. 
        Save your twitter api keys and tokens to your environmental variables.
        """
        # 認証キーの設定
        consumer_key =  os.getenv("TWITTER_CONSUMER_KEY") #"API key"
        consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")  #"API secret key"
        access_token = os.getenv("TWITTER_ACCESS_TOKEN") # "Access token"
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")   #  "Access token secret"
        
        # OAuth認証
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # APIのインスタンスを生成
        self.api = tweepy.API(auth)
    
    def collect_user_id(self,user_, tp="followers",n=1, check_limit=False):
        """Return 5000 user ids for one account.
        
        Args:
            user_ (int) : user id should be given. 
            tp (str) : type of accounts. "followers" or "friends".
            n (int) : number of pagination. In default 1, meaning that maximum 5000 ids. 
            check_limit (bool) : print rate limit.
        
        Return:
            list : user ids. 
        """
        user_IDs = []
        if tp == "followers":
            method = self.api.followers_ids
        elif tp == "friends":
            method = self.api.friends_ids
        else:
            raise Exception("Unknown type of a variable.")
        
        for i, page in enumerate(tweepy.Cursor(method, id=user_).pages(n)):
            for j, user_ID in enumerate(page):
                user_IDs.append(user_ID)
        
        if check_limit:
            self.check_api_rate_limit(f"API.{tp}_ids")
        return(user_IDs)
    
    def check_api_rate_limit(self, method):
        """Print out api rate limite for each type. 

        method (str) : API.<something>. see source code. 
        """
        status = self.api.rate_limit_status()
        self.status = status # for checking purpose.
        if method   == "API.followers":
            s = status["resources"]["followers"]["/followers/list"]
        elif method == "API.friends":
            s = status["resources"]["friends"]["/friends/list"]
        elif method == "API.followers_ids":
            s = status["resources"]["followers"]["/followers/ids"]
        elif method == "API.friedns_ids":
            s = status["resources"]["friends"]["/friends/ids"]
        elif method == "API.show_friendship":
            s = status["resources"]["friendships"]["/friendships/show"]
        elif method == "API.search":
            s = status["resources"]["search"]["/search/tweets"]
        elif method == "API.rate_limit_status":
            s = status["resources"]["application"]["/application/rate_limit_status"]
        elif method == "API.get_user":
            s = status["resources"]["users"]["/users/:id"]
        else:
            s = f"{tp} was not found. Type appropriate type"

        print(method)
        print(s)
        return(s)
        
    def save_user_info(self, id_, check_limit=False, user_info=None):
        """Save user information as json format. 
        Each file contains only one user information and 
        each file name represents user id. 

        Args: 
            id_ (int) : user id. 
            check_limit (bool) : print rate limit.
            user_info (User) : if None, obtain tweepy User object using "API.get_user", 
                else use user_info variable. 
        """
        if not os.path.exists(self.path2data):
            os.mkdir(self.path2data)

        path = self.get_path2data(id_)
        if os.path.exists(path):
            return

        if user_info == None:
            user_info = self.api.get_user(user_id = id_)._json

        with open(path, "w") as f:
            json.dump(user_info, f)

        if check_limit:
            self.check_api_rate_limit("API.get_user")
    
    def save_multiple_user_info(self,ids, check_limit=False):
        """Save multiple user information. 

        Args: 
            ids (list): user ids. 
        """
        for i, id_ in enumerate(ids):
            self.save_user_info(id_)
            if i % 100 == 0:
                status = self.check_api_rate_limit("API.get_user")
                if status["remaining"] < 100:
                    break
                
        if check_limit:
            self.check_api_rate_limit("API.get_user")


    def read_user_info(self, id_, save=False):
        """Read one user information from "path2data" directory. 
        If id_ is not saved in "path2data" directory, 
        fetch and save data using api. 
        Becareful about exceeding api rate limit. 

        Args:   
            id_ (int) : user id. 
            save (bool) : if True, if id can not be found, 
                save that id using "API.get_user".

        Return: 
            json : user information. 
        """
        path = self.get_path2data(id_)
        if not os.path.exists(path): 
            if save:
                self.save_user_info(id_)
            else:
                return

        with open(path, "r") as f:
            user_info = json.load(f)
        return(user_info)

    def read_multiple_user_info(self, ids):
        """Read multiple user information. 

        Args:
            ids (list): user ids. 

        Return:
            list : multiple user information.
        """
        user_infos = []
        for id_ in ids:
            user_info = self.read_user_info(id_)
            if user_info:
                user_infos.append(user_info)
        return(user_infos)

    def convert_screen_name_into_id(self, screen_name, check_limit=False):
        """Convert screen_name into id. 
        This function uses "API.get_user". 
        If "data2path" does not include this id, save id.  

        """
        user_info = self.api.get_user(screen_name= screen_name)._json
        id_ = user_info["id"]
        self.save_user_info(id_,user_info=user_info)
        if check_limit:
            self.check_api_rate_limit("API.get_user")
        return(id_)


    def get_path2data(self,id_):
        path = f"{self.path2data}/{id_}.json"
        return(path)

    def display_one_user(self, user_info, keys=None):
        """Display one user information. 

        Args: 
            user_info (dict): json format of User Object. 
        """
        
        if keys == None: 
            keys = self.default_keys

        print("#" * 50)
        for k in keys:
            print(f"# {k: <17} : {user_info[k]}")
        
        # print url 
        k = "urls"
        urls = self.get_expanded_urls(user_info)
        urls = "\n".join(urls)
        print(f"# {k: <17} : {urls}")
        
        # print account url 
        print(f"# account url : https://twitter.com/{user_info['screen_name']}")

    def display_multiple_users(self, multi_user_info, keys=None):
        """Display multiple user information. 

        Args: 
            multi_user_info (list) : contaning json formats of User Object. 
        """ 
        
        for user_info in multi_user_info:
            self.display_one_user(user_info, keys)

    def markdown_one_user(self, user_info, keys=None): 
        """Return markdown formatted text. 

        Args:
            user_info (dict): json format of User Object. 
            
        Returns:
            str : markdown formatted text. 
        """
        s = "" 
        if keys == None: 
            keys = self.default_keys

        s += "* * *\n"
        for k in keys:
            s += f"- {k: <17} : {user_info[k]}\n"

        # print url 
        k = "urls"
        urls = self.get_expanded_urls(user_info)
        urls = "\n".join(urls)
        s += f"- {k: <17} : {urls}\n"

        # print account url
        account_url = f"https://twitter.com/{user_info['screen_name']}"
        s += f"- account url : [{account_url}]({account_url})\n"

        # with profile picture. 
        _,path = self.get_profile_jpg_path(user_info)
        if not os.path.exists(path):
            self.fetch_profile_jpg(user_info)
        s += f"""\n\n<img src=".{path}" width="200px">\n"""

        return(s)

    def markdown_multiple_users(self, multi_user_info, keys=None):
        """Return multiple user information formatted as markdown. 

        Args: 
            multi_user_info (list) : contaning json formats of User Object. 

        Returns:
            str : markdown formatted text. 
        """ 
        s = [self.markdown_one_user(user_info, keys) for user_info in multi_user_info ] 
        s = "\n".join(s)
        return(s)

    def get_expanded_urls(self, user_info): 
        """Given user information of json format, return expanded_url. 
        If not exist, return None. 

        Args: 
            user_info (dict) : json format of User Object. 

        Return:
            list : expanded urls. 
        """
        entities = user_info["entities"] 
        urls = entities.get("url")
        urls = urls.get("urls") if urls else None 
        expanded_urls = []
        if urls:
            for url in urls:
                expanded_urls.append(url["expanded_url"])
        return(expanded_urls) 

    def judge_user_info(self, user_info):
        """Judge user infomation matches some criteria or not.

        Args: 
            user_info (dict) : json format of User Object. 

        Return:
            bool : match criteria or not.
        """
        
        n_followers = 1000
        n_friends   = 1000
        s_ = "男"

        b1  = user_info["followers_count"] <= n_followers
        b2  = user_info["friends_count"] <= n_friends
        b3  = s_ not in user_info["name"]
        
        res = all([b1, b2, b3])
        return(res) 

    def get_filtered_users(self, multi_user_info):
        """Only return users which pass "judge_user_info" function.

        Args: 
            multi_user_info (list) : contaning json formats of User Object. 
        """
        filtered = [ user for user in multi_user_info if self.judge_user_info(user)]
        return(filtered)

    def display_target_followers(self, screen_name): 
        """Display filtered followers information of target account. 
        Given screen_name, display filtered user information.

        Args: 
            screen_name (str): target account's screen name. 
        """
        user_IDs = self.collect_user_id(user_= screen_name, tp="followers") 
        self.save_multiple_user_info(user_IDs) 
        multi_user_info = self.read_multiple_user_info(user_IDs)
        filtered_user_infos = self.get_filtered_users(multi_user_info)
        self.display_multiple_users(filtered_user_infos)

    def markdown_target_accounts(self, screen_name,tp="followers",open_=False):
        """Save and Open followers information of target account as markdown format. 
        Given screen_name, save filtered user information to markdown text. 

        Args: 
            screen_name (str): target account's screen name. 
            open_ (bool) : After saving file, open it in the browser or not.
        """
        user_IDs = self.collect_user_id(user_= screen_name, tp=tp) 
        self.save_multiple_user_info(user_IDs) 
        multi_user_info = self.read_multiple_user_info(user_IDs)
        filtered_user_infos = self.get_filtered_users(multi_user_info)
        s = self.markdown_multiple_users(filtered_user_infos)

        target_id = self.convert_screen_name_into_id(screen_name)
        target_info = self.read_user_info(target_id) 
        target_md = "# Target Account\n"
        target_md += self.markdown_one_user(target_info)
        target_md += f"\n\n## Filtered {tp} information\n\n"

        res = target_md + s 
        path = f"./markdown/{target_id}.md"
        with open(path, "w") as f:
            f.write(res)
        if open_:
            webbrowser.open(path, new=2)

        
    
    def get_user_infos_in_data(self, n=30):
        """get user information from "path2data" directory. 

        Args:
            n (int) : number of data this function fetches. 

        Return:
            list : contaning json formats of User Object. 
        """
        paths = glob.glob(self.path2data + "/*.json")
        ids = [s.lstrip(self.path2data+"/").rstrip(".json") for s in paths]
        multiple_user_info = self.read_multiple_user_info(ids)
        return(multiple_user_info)

    def fetch_profile_jpg(self, user_info):
        """Fetch profile jpg form user_info json. 

        Args: 
            user_info (dict) : json format of User Object. 
        """
        url = user_info["profile_image_url_https"]
        dir_, path = self.get_profile_jpg_path(user_info)

        
        if not os.path.exists(dir_):
            os.mkdir(dir_)
        if not os.path.exists(path):
            res = requests.get(url)
            img = res.content
            with open(path, "wb") as f:
                f.write(img)
        
    def get_profile_jpg_path(self, user_info):
        """Return profile jpg path. 

        Args: 
            user_info (dict) : json format of User Object. 

        Return: 
            dir_ (str) : path to the directory.
            path (str) : path to the picture.
        """
        id_ = user_info["id"]
        url = user_info["profile_image_url_https"]
        name = url.split("/")[-1] 
        dir_ = f"./profile_jpg/{id_}"
        path = f"./profile_jpg/{id_}/{name}"
        return(dir_, path)







