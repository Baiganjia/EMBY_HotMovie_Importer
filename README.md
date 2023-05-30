# Emby服务器自动创建豆瓣+TMDB热门电影合集

设计狗一只，没学过Python，啥都不会，GPT写的，我只管Pua它。
脚本大概能用，应该。。。

获取豆瓣热门电影和TMDB热门电影的数据，
然后将Emby服务器中有的电影，添加到合集中去。 
如果不指定合集，则会自动创建一个。
之后会更新合集封面，让合集封面保持最新。
Emby中还没有的电影，会以[片名，IMDBID]的格式输出到CSV文件内，方便取用

---

![2023-05-30_082943](https://github.com/Baiganjia/EMBY_HotMovie_Importer/assets/134911905/7e05402a-b048-4b98-a854-57447b2c1015)

![2023-05-30_082944](https://github.com/Baiganjia/EMBY_HotMovie_Importer/assets/134911905/9055735c-44e9-4d5e-960a-2524a2f749cd)

### 运行方式
文本编辑器打开py脚本，设定并替换你自己的内容
```Plain Text
如果不想要输出csv文件 就删掉220行 self.write_to_csv()
```

### 运行脚本
```Plain Text
python EMBY_HotMovie_Importer.py
```
### 运行前请注意以上扩展依赖是否安装
```Plain Text
# requests、json、BeautifulSoup、time、base64和urllib.parse等模块。
# 安装方式
pip install XXXXXX

```

