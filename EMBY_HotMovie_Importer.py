import os,requests,json,time,base64,csv
from bs4 import BeautifulSoup
import urllib.parse
from configparser import ConfigParser


config = ConfigParser()
with open('config.conf', encoding='utf-8') as f:
    config.read_file(f)
use_proxy = config.getboolean('Proxy', 'use_proxy', fallback=False)
if use_proxy:
    os.environ['http_proxy'] = 'http://127.0.0.1:7890'
    os.environ['https_proxy'] = 'http://127.0.0.1:7890'
else:
    os.environ.pop('http_proxy', None)
    os.environ.pop('https_proxy', None)

class Get_Detail(object):

    def __init__(self):
        self.noexist = []
        self.ctls = []

        # 获取配置项的值
        self.emby_server = config.get('Server', 'emby_server')
        self.emby_api_key = config.get('Server', 'emby_api_key')
        self.tmdb_api_key = config.get('Server', 'tmdb_api_key')
        self.collection_id = config.get('Collection', 'collection_id')
        self.collection_name = config.get('Collection', 'collection_name')
        self.movies_per_page = config.get('Collection', 'movies_per_page') 

            
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39"
        }
        self.start_url = f"https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit={self.movies_per_page}&page_start={{}}"
        self.urllist = [self.start_url.format(i*self.movies_per_page) for i in range(1)] 
        

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
        url = f"{self.emby_server}/emby/Items?api_key={self.emby_api_key}&Recursive=true&IncludeItemTypes=Movie&AnyProviderIdEquals=imdb.{imdb_id}"
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
        url = f"{self.emby_server}/emby/Collections?IsLocked=false&Name={encoded_collection_name}&Ids={emby_id}&api_key={self.emby_api_key}"
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
        print("开始获取豆瓣电影，避免防爬虫设置了每2秒请求间隔，因此会比较慢。。。")
        total_movies = len(urllist) * self.movies_per_page  # 使用类的成员变量
        current_movie = 0
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
                current_movie += 1
                print(f"\r进度: {current_movie}/{total_movies}", end='')
        print()
        return cont_dict_list

    def add_movie_to_collection(self, emby_id, collection_id):
        url = f"{self.emby_server}/emby/Collections/{collection_id}/Items?Ids={emby_id}&api_key={self.emby_api_key}"
        headers = {"accept": "*/*"}
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.status_code == 204

    def replace_cover_image(self, library_id, image_url):
        response = requests.get(image_url)
        image_content = response.content
        base64_image = base64.b64encode(image_content).decode('utf-8')

        url = f'{self.emby_server}/emby/Items/{library_id}/Images/Primary?api_key={self.emby_api_key}'

        headers = {
            'Content-Type': 'image/jpeg'
        }

        response = requests.post(url, headers=headers, data=base64_image)

        if response.status_code == 204:
            print(f'成功更新合集封面 {library_id}.')
        else:
            print(f'合集封面更新失败 {library_id}.')

    def check_collection_exists(self, collection_id):
        url = f"{self.emby_server}/Items?Ids={collection_id}&api_key={self.emby_api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if len(data["Items"]) > 0 and data["Items"][0]["Type"] == "BoxSet":
                return True
        return False
    

    def get_tmdb_popular_movies(self, api_key):
        print("开始获取TMDB热门电影...")
        base_url = "https://api.themoviedb.org/3"
        headers = {
            "Accept": "application/json",
        }
        # 注意这里添加了language=zh-CN参数
        response = requests.get(f"{base_url}/movie/popular?api_key={api_key}&language=zh-CN", headers=headers)
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
            # print(f"An error occurred: {response.status_code}")
            return None

    def run(self):
        # 先获取豆瓣和TMDB的电影信息
        
        self.ctls = self.get_value(self.urllist)
        tmdb_movies = self.get_tmdb_popular_movies(self.tmdb_api_key)

        # 将TMDB热门电影列表转化为与豆瓣电影同样的格式
        for movie in tmdb_movies:
            details = self.get_movie_details(movie['id'], self.tmdb_api_key)
            self.ctls.append({
                '影名': movie['title'],
                'imdb_id': details['imdb_id'] if details else None,
            })

        collection_id = self.collection_id


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
                image_url = f"{self.emby_server}/emby/Items/{emby_id}/Images/Primary?api_key={self.emby_api_key}"
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
                        print(f"电影 '{movie['影名']}' 加入到合集成功.")
                    else:
                        print(f"电影 '{movie['影名']}' 加入到合集内失败.")
                    # print("电影:", movie["影名"])
                    # print("IMDb ID:", imdb_id)
                    # print("Emby ID:", emby_id)
                else:
                    print(f"当前Emby库内还没有 '{movie['影名']}' {imdb_id}")
                    message = [movie['影名'], imdb_id]
                    self.noexist.append(message)
            self.write_to_csv()      
        else:
            print("该电影似乎缺失海报.")


    def write_to_csv(self):
        with open('noexist.csv', 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['电影名', 'imdbID'])  # writing the header
            writer.writerows(self.noexist)  # writing the data
                
if __name__ == "__main__":
    gd = Get_Detail()
    gd.run()
