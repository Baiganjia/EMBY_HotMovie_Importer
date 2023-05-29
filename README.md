# Emby服务器自动创建豆瓣热门电影合集
摄影美工一只，没学过python，啥都不会，GPT写的，我只管Pua它。
脚本大概能用，应该。。。

这个脚本是用来获取豆瓣热门电影的数据， 并将Emby库内匹配的电影添加到的一个指定的合集中。 如果不指定合集，则会自动创建一个。 之后会更新合集封面，让合集封面保持最新

### 运行方式
打开py脚本，替换你自己的内容

```Plain Text
# Emby服务器的地址和API密钥
EMBY_SERVER = '替换你的EMBY服务器'
API_KEY = '替换你的EmbyAPI'

# 设置要添加电影到指定合集的ID，不指定则自动创建
COLLECTION_ID = "2719594"

# 设置要创建的合集的名称
COLLECTION_NAME = "【热门电影】"
```
### 运行脚本
```Plain Text
python EMBY_Douban_HotMovie_Importer.py
```
### 运行前请注意以上扩展依赖是否安装
```Plain Text
# requests、json、BeautifulSoup、time、base64和urllib.parse等模块。
# 安装方式
pip install XXXXXX

```
