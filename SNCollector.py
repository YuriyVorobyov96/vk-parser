#!/usr/bin/env python
# coding: utf-8

# # Сбор данных из ВКонтакте 

# Автор: Воробьев Юрий (https://vk.com/vorobyevyuri)
# 
# Данный скрипт собирает данные постов в группе из социальной сети ВКонтакте
# 
# Следуйте инструкциям 

# ## Скрипт 1 - Создание таблицы данных 

# ### Столбцы таблицы:
# * дата публикации (unix time) / конвертер: https://www.cy-pr.com/tools/time/
# * ссылка на публикацию
# * количество лайков
# * количество репостов

# 1. Подключение библиотек 

# In[1]:


import requests


# 2. Для получения токена перейдите по ссылке и скопируйте нужную часть в блок ниже
# https://oauth.vk.com/authorize?client_id=5453402&display=page&redirect_uri=http://localhost&scope=&response_type=token&v=5.53
# ![alt](https://api.monosnap.com/rpc/file/download?id=H72wV79ObVw7rLBfJO8T4jOJ25szXW)

# In[2]:


token = '2fb0e77cfe900ca8f180debe5867a9cb3151e6bacf681b0a6d5b2ef6cb3e8cd07f95d013df3cc4415b684'


#  3. Укажите id группы

# In[3]:


group = -48632629


# 4. Укажите выборку по постами (целочисленное значение):

# In[4]:


posts = 100


# 5. Запустите скрипт:

# In[19]:


r = requests.get('https://api.vk.com/method/wall.get',params={'access_token':token,'owner_id':group,'count':posts,'v': 5.68})
post = r.json()['response']['items']
print('Дата публикации','|','          Ссылка         ','|','Лайки','|','Репосты')
for i in range(1,posts):
    post_date = post[i]['date']
    post_id = post[i]['id']
    group_id = post[i]['from_id']
    likes = post[i]['likes']['count']
    repost = post[i]['reposts']['count']
    print(post_date,'     |','vk.com/wall'+str(group_id)+'_'+str(post_id),'|',likes,'    |',repost)


# ## Скрипт 2 - Запись данных в файл 

# ### Расположение:
# Все созданные файлы создаются в корне пользователя, пример: C:\Users\\<имя_пользователя>
# 
# ### Наименование:
# * Файл данных json - posts.json
# * Файл данных csv - posts_data.csv

# 1. Подключение библиотек

# In[1]:


import requests
import json
import csv
import pymongo
from time import sleep


# 2. Для получения токена перейдите по ссылке и скопируйте нужную часть в блок ниже
# https://oauth.vk.com/authorize?client_id=5453402&display=page&redirect_uri=http://localhost&scope=&response_type=token&v=5.53
# ![alt](https://api.monosnap.com/rpc/file/download?id=H72wV79ObVw7rLBfJO8T4jOJ25szXW)

# In[2]:


token = '563fbc6dc0b5b7916d1709141f1c13303d7a390ce8051ae11294b7e36b129d0f6fa436fc19dfee434b373'


# 3. Укажите id группы

# In[3]:


group_id = '-48632629'


# 4. Укажите выборку по постами (целочисленное значение):

# In[4]:


post = 100


# 5. Укажите сдвиг выборки (целочисленное значение):

# In[5]:


offset = 0


# 6. Создание файла данных (json):

# In[6]:


def write_json(data):
	with open('posts.json', 'w', encoding="utf-8") as file:
		json.dump(data, file, indent=2, ensure_ascii=False)

def main():
	
	r = requests.get('https://api.vk.com/method/wall.get',params={'access_token':token,'owner_id':group_id,'count':post,'offset':offset,'v':5.68})
	
	write_json(r.json())

if __name__ == '__main__':
	main()


# 6. 1.|опционально| Вывод файла данных (json):

# In[7]:


print (r.json())


# 7. Создание файла данных (csv):

# In[17]:


def write_csv(data):
	with open('posts_data.csv', 'a', encoding="utf-8") as file:
		writer = csv.writer(file)
		writer.writerow((data['likes'],
						 data['reposts'],
						 data['text']
						))

def get_data(postdict):
	try:
		post_id = postdict['id']
	except:
		post_id = 0
		
	try:
		likes = postdict['likes']['count']
	except:
		likes = 'zero'
	
	try:
		reposts = postdict['reposts']['count']
	except:
		reposts = 'zero'	
		
	try:
		text = postdict['text']
	except:
		reposts = '***'
		
	data = {
		'id': post_id,
		'likes': likes,
		'reposts': reposts,
		'text': text
	}
	
	return data

def main():

	all_posts = []

	sleep(1)
	r = requests.get('https://api.vk.com/method/wall.get',params={'access_token':token,'owner_id':group_id,'count':post,'offset':offset,'v':5.68})
	posts = r.json()['response']['items']

	all_posts.extend(posts)

	data_posts = []

	for postdict in all_posts:
		post_data = get_data(postdict)
		write_csv(post_data)

if __name__ == '__main__':
	main()
	


# 7. 1.|опционально| Вывод файла данных (csv):

# In[8]:


with open('posts_data.csv', 'r', encoding="utf-8") as fp:
    reader = csv.reader(fp, delimiter=',', quotechar='"')
    # next(reader, None)  # skip the headers
    data_read = [row for row in reader]
print(data_read)    


# ## Скрипт 3 - Загрузка данных в хранилище 

# ### Расположение:
# Данные загружаются в БД "ictis", коллекцию "group"

# In[24]:


my_client = pymongo.MongoClient(
'mongodb+srv://YuriV:Juraass123@sncollector-ytivf.azure.mongodb.net/test?retryWrites=true&w=majority'
)

my_database = my_client.ictis3
my_collection = my_database.group


def save_posts(posts):
    flat_posts = []
    for post in posts:
        flat_posts.append({
            "post_id": post['id'],
            "date": post['date'],
            "text": post['text'],
            "likes_count": post['likes']['count'],
            "reposts_count": post['reposts']['count'],
            "comments_count": post['comments']['count'],
            "views_count": post['views']['count'],
            "url": "vk.com/wall{0}_{1}".format(post['owner_id'], post['id'])
        })

    my_collection.insert_many(flat_posts)


def main():

    # https://api.vk.com/method/users.get?user_id=210700286&v=5.52
    # https://oauth.vk.com/authorize?client_id=5453402&display=page&redirect_uri=http://localhost&scope=&response_type=token&v=5.53
    # e9c870e462f3976bc3dcfb2cec433656246127bcc76bfd562de09e92021c80087940c642d9d6251825e97

    all_posts = []
    date_x = 1559909249



    sleep(1)
    r = requests.get('https://api.vk.com/method/wall.get',params={'access_token':token,'owner_id':group_id,'count':postint,'offset':offset,'v':5.68})
    posts = r.json()['response']['items']
    save_posts(posts)
    #posts = r.json()['response']

   
if __name__ == '__main__':
    main()


# In[ ]:




