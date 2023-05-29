import requests
import json
from bs4 import BeautifulSoup
import time
import base64
import urllib.parse


# 导入库和定义全局变量

# Emby服务器的地址和API密钥
EMBY_SERVER = 'https://EMBY.SERVER.com'
API_KEY = 'ccXXXXXXXXXX61SXXXXXXXXXb6XXX0f'


# 设置要添加电影到指定合集的ID，不指定则自动创建
COLLECTION_ID = "2719594"

# 设置要创建的合集的名称
COLLECTION_NAME = "【豆瓣热门电影】"

class Get_Detail(object):
    
    # 初始化，这些属性用于存储全局变量的值，以及设置请求头部信息和起始 URL。
    def __init__(self):
        self.emby_server = EMBY_SERVER
        self.api_key = API_KEY
        self.collection_id = COLLECTION_ID
        self.collection_name = COLLECTION_NAME
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39"
        }
        # 取豆瓣热门前20个电影 
        self.start_url = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start={}"
        self.urllist = [self.start_url.format(i*20) for i in range(1)] 
        
    # 发送请求到指定的 URL，使用 BeautifulSoup 解析响应的 HTML，并通过查找特定元素来获取 IMDb ID。最后返回 IMDb ID。
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
        
    # 您根据 IMDb ID 构建请求 URL，然后发送请求到 Emby 服务器判断是否存在对应的电影
    # 注意这里只解析电影 IncludeItemTypes=Movie 可根据需求修改成Series
    def search_emby_by_imdb_id(self, imdb_id):
        url = f"{self.emby_server}/emby/Items?api_key={self.api_key}&Recursive=true&IncludeItemTypes=Movie&AnyProviderIdEquals=imdb.{imdb_id}"
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get('TotalRecordCount', 0) > 0:
            return data
        else:
            return None
    # 根据指定的合集名称构建请求 URL，并发送 POST 请求到 Emby 服务器。
    # 如果创建成功，则从返回的数据中获取合集的 ID，并将其打印出来。
    def create_collection(self):
        collection_name = self.collection_name
        # 获取第一个电影的Emby ID
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

    # 根据给定的 URL 列表，循环发送请求，获取电影数据，
    # 并将其解析为字典形式的内容，最后返回包含电影内容的列表。
    def get_value(self, urllist):
        cont_dict_list = []
        for each in urllist:
            response = requests.get(each, headers=self.headers)
            # print(response.text)  # 添加这行打印语句
            dictionary = json.loads(response.text)
            for eachdict in dictionary["subjects"]:
                content = {}
                content["影名"] = eachdict["title"]
                content["评分"] = eachdict["rate"]
                content["url"] = eachdict["url"]
                content["封面"] = eachdict["cover"]
                content["imdb_id"] = self.get_imdb_id(eachdict["url"])
                cont_dict_list.append(content)
                time.sleep(2)  # 每次请求之间暂停一秒，以避免触发豆瓣的防爬机制
        return cont_dict_list

    # 用Emby ID 和合集 ID 构建请求 URL，并发送 POST 请求到 Emby 服务器。
    # 检查响应状态码，如果返回的状态码为 204，表示成功添加电影到合集中
    def add_movie_to_collection(self, emby_id, collection_id):
        url = f"{self.emby_server}/emby/Collections/{collection_id}/Items?Ids={emby_id}&api_key={self.api_key}"
        headers = {"accept": "*/*"}
        response = requests.post(url, headers=headers)
        return response.status_code == 204

    # 构建URL替换合集的封面，让合集封面保持最新
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

    # 判断指定的合集是否存在
    def check_collection_exists(self, collection_id):
        url = f"{self.emby_server}/emby/Items?Ids={collection_id}&api_key={self.api_key}"
        response = requests.get(url)
        data = response.json()
        return response.status_code == 200 and data.get('TotalRecordCount', 0) > 0
    
    def run(self):
        ctls = self.get_value(self.urllist)
        collection_id = self.collection_id  # 设置要添加电影的合集 ID

        # 检查合集是否存在，若不存在则创建新合集
        if not self.check_collection_exists(collection_id):
            print('指定合集不存在合集，开始重新创建合集')
            collection_id = self.create_collection()
            if not collection_id:
                return
        else:
            print('指定合集存在，项目将直接添加到该指定ID内')
            collection_id = collection_id
        # 获取第一个具有Primary封面图的电影的Emby ID和封面图URL
        emby_id = None
        image_url = None

        for movie in ctls:
            imdb_id = movie["imdb_id"]
            emby_data = self.search_emby_by_imdb_id(imdb_id)
            if emby_data:
                emby_id = emby_data["Items"][0]["Id"]
                image_url = f"{self.emby_server}/emby/Items/{emby_id}/Images/Primary?api_key={self.api_key}"
                response = requests.head(image_url)
                if response.status_code == 200:
                    break

        if emby_id and image_url:
            # 替换合集封面图为找到的电影的Primary封面图
            self.replace_cover_image(collection_id, image_url)

            for movie in ctls:
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
