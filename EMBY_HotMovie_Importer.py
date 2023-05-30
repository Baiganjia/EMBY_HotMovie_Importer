import requests
import json
from bs4 import BeautifulSoup
import time
import base64
import urllib.parse


EMBY_SERVER = 'https://XXXXX'
API_KEY = 'XXXX'  # 这里填入你自己的eMBY API密钥
TMDB_API_KEY = 'XXXXX' # 这里填入你自己的TMDB API密钥

COLLECTION_ID = "2719225"
COLLECTION_NAME = "【豆瓣TMDB热门电影】"

class Get_Detail(object):
    def __init__(self):
        self.ctls = []
        self.emby_server = EMBY_SERVER
        self.api_key = API_KEY
        self.collection_id = COLLECTION_ID
        self.collection_name = COLLECTION_NAME
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39"
        }
        self.start_url = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start={}"
        self.urllist = [self.start_url.format(i*20) for i in range(1)] 
        

    def get_imdb_id(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        imdb_info = soup.find('span', string='IMDb:')
        imdb_id = None
        if imdb_info:
            imdb_id = imdb_info.find_next_sibling(string=True)
            if imdb_id:
                imdb_id = imdb_id.strip()
        return imdb_id

    def search_emby_by_imdb_id(self, imdb_id):
        url = f"{self.emby_server}/emby/Items?api_key={self.api_key}&Recursive=true&IncludeItemTypes=Movie&AnyProviderIdEquals=imdb.{imdb_id}"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get('TotalRecordCount', 0) > 0:
            return data
        else:
            return None

    def create_collection(self):
        collection_name = self.collection_name

        first_movie_imdb_id = self.ctls[0]["imdb_id"]
        emby_data = self.search_emby_by_imdb_id(first_movie_imdb_id)
        if emby_data:
            emby_id = emby_data["Items"][0]["Id"]
        else:
            print(f"Emby内没有匹配到该IMDbID的电影: {first_movie_imdb_id}")
            return None

        encoded_collection_name = urllib.parse.quote(collection_name, safe='')
        url = f"{self.emby_server}/emby/Collections?IsLocked=false&Name={encoded_collection_name}&Ids={emby_id}&api_key={self.api_key}"
        headers = {
            "accept": "application/json"
        }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            collection_id = response.json().get('Id')
            print(f"成功创建合集: {collection_id}")
            return collection_id
        else:
            print("创建合集失败.")
            return None

    def get_value(self, urllist):
        cont_dict_list = []
        for each in urllist:
            response = requests.get(each, headers=self.headers)

            dictionary = json.loads(response.text)
            for eachdict in dictionary["subjects"]:
                content = {}
                content["影名"] = eachdict["title"]
                content["评分"] = eachdict["rate"]
                content["url"] = eachdict["url"]
                content["封面"] = eachdict["cover"]
                content["imdb_id"] = self.get_imdb_id(eachdict["url"])
                cont_dict_list.append(content)
                time.sleep(2)
        return cont_dict_list

    def add_movie_to_collection(self, emby_id, collection_id):
        url = f"{self.emby_server}/emby/Collections/{collection_id}/Items?Ids={emby_id}&api_key={self.api_key}"
        headers = {"accept": "*/*"}
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.status_code == 204

    def replace_cover_image(self, library_id, image_url):
        response = requests.get(image_url)
        image_content = response.content
        base64_image = base64.b64encode(image_content).decode('utf-8')

        url = f'{self.emby_server}/emby/Items/{library_id}/Images/Primary?api_key={self.api_key}'

        headers = {
            'Content-Type': 'image/jpeg'
        }

        response = requests.post(url, headers=headers, data=base64_image)

        if response.status_code == 204:
            print(f'成功替换合集封面 {library_id}.')
        else:
            print(f'合集封面替换失败 {library_id}.')

    def check_collection_exists(self, collection_id):
        url = f"{self.emby_server}/emby/Items/{collection_id}?api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} when checking collection {collection_id}.")
            return False
        data = response.json()
        if data.get('Type') != 'BoxSet':
            print(f"Error: Item {collection_id} exists but it is not a collection.")
            return False
        print(f"Collection {collection_id} exists.")
        return True
    

    def get_tmdb_popular_movies(self, api_key):
        base_url = "https://api.themoviedb.org/3"
        headers = {
            "Accept": "application/json",
        }
        response = requests.get(f"{base_url}/movie/popular?api_key={api_key}", headers=headers)
        if response.status_code == 200:
            return response.json()['results']
        else:
            print(f"An error occurred: {response.status_code}")
            return []

    def get_movie_details(self, movie_id, api_key):
        base_url = "https://api.themoviedb.org/3"
        headers = {
            "Accept": "application/json",
        }
        response = requests.get(f"{base_url}/movie/{movie_id}?api_key={api_key}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"An error occurred: {response.status_code}")
            return None

    def run(self):
        # 先获取豆瓣和TMDB的电影信息
        self.ctls = self.get_value(self.urllist)
        tmdb_movies = self.get_tmdb_popular_movies(TMDB_API_KEY)

        # 将TMDB热门电影列表转化为与豆瓣电影同样的格式
        for movie in tmdb_movies:
            details = self.get_movie_details(movie['id'], TMDB_API_KEY)
            self.ctls.append({
                '影名': movie['title'],
                'imdb_id': details['imdb_id'] if details else None,
            })

        collection_id = self.collection_id
        print(collection_id)

        if not self.check_collection_exists(collection_id):
            print('指定合集不存在合集，开始重新创建合集')
            collection_id = self.create_collection()
            if not collection_id:
                return
        else:
            print('指定合集存在，项目将直接添加到该指定ID内')
            collection_id = collection_id

        emby_id = None
        image_url = None

        for movie in self.ctls:
            imdb_id = movie["imdb_id"]
            emby_data = self.search_emby_by_imdb_id(imdb_id)
            if emby_data:
                emby_id = emby_data["Items"][0]["Id"]
                image_url = f"{self.emby_server}/emby/Items/{emby_id}/Images/Primary?api_key={self.api_key}"
                response = requests.head(image_url)
                if response.status_code == 200:
                    break

        if emby_id and image_url:
            self.replace_cover_image(collection_id, image_url)
            for movie in self.ctls:
                imdb_id = movie["imdb_id"]
                emby_data = self.search_emby_by_imdb_id(imdb_id)
                if emby_data:
                    emby_id = emby_data["Items"][0]["Id"]
                    added_to_collection = self.add_movie_to_collection(emby_id, collection_id)
                    if added_to_collection:
                        print(f"电影 {emby_id} 加入到合集 {collection_id} 内成功.")
                    else:
                        print(f"电影 {emby_id} 加入到合集 {collection_id} 内失败.")
                    print("电影:", movie["影名"])
                    print("IMDb ID:", imdb_id)
                    print("Emby ID:", emby_id)
                    print()
                else:
                    print(f"Emby内没有匹配到该IMDbID的电影: {imdb_id}")
                    print()
        else:
            print("该电影似乎缺失海报.")


if __name__ == "__main__":
    gd = Get_Detail()
    gd.run()