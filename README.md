- 这是旧版，最新版请移步：https://github.com/Baiganjia/EMBY_HotMovie_Importer_V2/

# Emby服务器自动创建热门影剧合集

设计狗一只，没学过Python，啥都不会，GPT写的，我只管Pua它。
脚本大概能用，应该。。。

获取豆瓣热门电影和TMDB热门[电影&剧集]的数据，
然后将Emby服务器中有的电影，添加到合集中去。 
如果不指定合集，则会自动创建一个。
之后会更新合集封面，让合集封面保持最新。
Emby中还没有的电影，会以[片名，IMDBID]的格式输出到CSV文件内，方便取用

# 主要工作流程如下：


- 初始配置: 初始化各类需要的参数，如Emby服务器地址、Emby API密钥、TMDB API密钥、合集名称和ID等。
- 获取豆瓣电影信息: 首先从豆瓣网站获取热门电影信息，包括电影名、评分、豆瓣网址、封面以及对应的IMDb ID。
- 获取TMDB电影信息: 然后从TMDB获取热门电影信息，将TMDB的电影信息格式化为与豆瓣电影相同的格式后，添加到电影信息列表中。
- 检查或创建合集: 检查Emby中是否存在指定的合集，如果不存在，则会根据指定的电影创建新的合集。
- 更新合集封面: 查找电影信息列表中的第一部电影，获取其封面，然后更新Emby中对应合集的封面。
- 添加电影到合集: 对电影信息列表中的每一部电影，通过IMDb ID在Emby中查找对应的电影，如果找到，则将该电影添加到指定的合集中。
- 获取豆瓣电视剧信息: 从豆瓣网站获取指定标签的电视剧信息，然后将这些电视剧信息添加到电视剧信息列表中。
- 添加电视剧到合集: 对电视剧信息列表中的每一部电视剧，通过IMDb ID在Emby中查找对应的电视剧，如果找到，则将该电视剧添加到指定的合集中。
- 输出未找到的项目: 如果有些电影或电视剧在Emby中没有找到，将这些项目的信息写入CSV文件中。

注意：这段代码涉及到的各种API密钥、服务器地址等敏感信息在实际使用时应当妥善保管，防止泄漏导致的安全问题。




---

![2023-05-30_082943](https://github.com/Baiganjia/EMBY_HotMovie_Importer/assets/134911905/7e05402a-b048-4b98-a854-57447b2c1015)

![2023-05-30_082944](https://github.com/Baiganjia/EMBY_HotMovie_Importer/assets/134911905/9055735c-44e9-4d5e-960a-2524a2f749cd)

```Plain Text
脚本会输出一个noexist.csv文件没用来记录哪些热门电影是你的Emby库中没有的
如果不想要输出csv文件 就删掉230行 self.write_to_csv()
```
![image](https://github.com/Baiganjia/EMBY_HotMovie_Importer/assets/134911905/811c38b6-9ece-42f6-8c76-343112fea5ba)



## 运行方式

#### 配置文件
文本编辑器打开config.conf文件，设定并替换你自己的内容
```Plain Text
[Server]
# 这里填入你Emby服务器地址
emby_server = https://BAIGAN.SERVER.EMBY
# 这里填入你Emby API密钥
emby_api_key = cXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXf
# 这里填入你自己的TMDB API密钥
tmdb_api_key = fXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX3

[Collection]
# 要指定添加影片到某个合集内，就填入那个合集的ID，不指定则按下面指定的名称自动创建
collection_id = 23333333
# 设置要创建的合集的名称
collection_name = 【热门电影】
# 这里设置你要获取的豆瓣电影数量（默认20）
movies_per_page = 20

# 指定是否需要使用代理，如果是WIN本地Clash，则开启
[Proxy]
use_proxy = False
# use_proxy = True

http_proxy = http://127.0.0.1:7890
https_proxy = https://127.0.0.1:7890
```

#### 安装依赖
```Plain Text
pip install -r requirements.txt
```
#### 运行脚本
```Plain Text
python EMBY_HotMovie_Importer.py
```


