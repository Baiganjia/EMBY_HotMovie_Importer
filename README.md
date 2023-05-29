# EMBY\_Douban\_HotMovie\_Importer
这个脚本是用来获取豆瓣热门电影的数据， 并将库内匹配的电影添加到的一个指定的合集中。 如果不指定合集，则会自动创建一个。 之后会更新合集封面，让合集封面保持最新

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
# 安装方式
pip install XXXXXX
```
