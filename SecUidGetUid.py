# 根据用户主页ID，获取指定时间段内用户所有视频链接,并可下载对应视频
# copy改编自https://github.com/wanglu58/douyincrawler
import datetime
import json
import os
import re
import time
import uuid
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dateutil.relativedelta import relativedelta
from openpyxl import Workbook

downloadvideo = 1       # 0 不下载视频，1 下载视频
issue_start = '2020.02' # 从哪个时间开始爬取（2018年1月：输入2018.01）
issue_end   = '2020.03' # 爬取2月1日到3月1日直接的视频

# 此版本可以获取视频连接
def get_data(start, end, chinesename):

    workbook = Workbook()
    worksheet = workbook.active
    save_file = "videoinfo.xlsx"

    # 每个workbook创建后，默认会存在一个worksheet，对默认的worksheet进行重命名
    worksheet.title = "Sheet1"


    beginarray = time.strptime(start, '%Y-%m-%d %H:%M:%S')
    endarray = time.strptime(end, '%Y-%m-%d %H:%M:%S')
    t1 = int(time.mktime(beginarray) * 1000)
    t2 = int(time.mktime(endarray) * 1000)

    params = {
        'sec_uid': sec_uid,
        'count': 200,
        'min_cursor': t1,
        'max_cursor': t2,
        'aid': 1128,
        '_signature': 'PtCNCgAAXljWCq93QOKsFT7QjR'
    }

    awemehtml = requests.get(url=awemeurl, params=params, headers=headers).text
    videodata = json.loads(awemehtml)
    awemenum = len(videodata['aweme_list'])
    time_str = f"{start.split('-')[0]}.{start.split('-')[1]}"
    num = 0
    for j in range(awemenum):
        num += 1

        if downloadvideo:
            os.makedirs(f'{Path}/{time_str}-{awemenum}', exist_ok=True)

        videotitle = videodata['aweme_list'][j].get('desc')
        if not videotitle:
            videotitle = str(uuid.uuid1())
        for s in '\\/:*?\"<>|':
            videotitle = videotitle.replace(s, '')
            # videotitle = f'{num}-{videotitle}'

        videourl = videodata['aweme_list'][j]['video']['play_addr']['url_list'][0]
        json_data[videourl] = f'{Path}/{time_str}-{awemenum}/{videotitle}.mp4'

        videoid = videodata['aweme_list'][j].get('aweme_id')
        videourl = 'https://www.douyin.com/video/' + videoid
        videotime = videodata['aweme_list'][j]['video'].get('duration') # 单位ms

        infourl =  'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids=' + videoid
        response = requests.get(url=infourl,headers=headers).text
        otherinfodata = json.loads(response)

        row = []
        row.append(chinesename) # 账号名称
        row.append(videourl)    # 视频链接
        row.append(videotitle)  # 视频标题
        row.append(videotime)   # 视频时长
        row.append(otherinfodata["item_list"][0]["statistics"]["digg_count"])    # 点赞数
        row.append(otherinfodata["item_list"][0]["statistics"]["comment_count"]) # 评论数
        row.append(otherinfodata["item_list"][0]["statistics"]["share_count"])   # 转发数
        # 收藏数显示为0，可以根据视频链接通过selenium爬取
        worksheet.append(row)  # 把每一行append到worksheet中

    workbook.save(filename=save_file)  # 写入excel ,不能忘记


def get_video(url, title):
    global total_num
    total_num += 1
    with open(title, 'wb') as v:
        try:
            v.write(requests.get(url=url, headers=headers).content)
            return f'{title.split("/")[-1][:-4]} ===> 下载成功。'
        except Exception as e:
            total_num -= 1
            with open(f'{Path}/失败链接.txt', 'a', encoding='utf-8') as t:
                t.write(url)
                t.write('\n')
            return f'{title.split("/")[-1][:-4]} ===> 下载失败。'


if __name__ == '__main__':

    data = [] # 存放每个用户主页ID数据
    for line in open("SecUid.txt", "r"):
        data.append(line)

    df = pd.read_excel('data.xlsx', header=0)  # 导入抖音账号名信息
    username = df.iloc[:, 1]

    awemeurl  = 'https://www.iesdouyin.com/web/api/v2/aweme/post/?'
    douyinurl = 'https://www.iesdouyin.com/web/api/v2/user/info/?'
    videoinfourl  = 'https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?item_ids='

    headers = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/' + \
                      '537.36(KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36'
    }

    if issue_start.split('.')[-1][0] == '0':
        month = int(issue_start.split('.')[-1][-1])
    else:
        month = int(issue_start.split('.')[-1])
    year = int(issue_start.split('.')[0])

    if issue_end.split('.')[-1][0] == '0':
        month_end = int(issue_end.split('.')[-1][-1])
    else:
        month_end = int(issue_end.split('.')[-1])
    year_end = int(issue_end.split('.')[0])

    current = datetime.date(year, month, 1)
    endtime = datetime.date(year_end,month_end,1)

    timepool = []
    while current <= endtime:
        timepool.append(current.strftime('%Y-%m-%d 00:00:00'))
        current += relativedelta(months=1)
    # timepool.append(current.strftime('%Y-%m-%d 00:00:00'))

    print("爬取时间段：",timepool)

    for i in range(2):#range(len(data)):
        sec_uid = data[i]
        chinesename = username[i]

        getname = requests.get(url=f'{douyinurl}sec_uid={sec_uid}', headers=headers).text
        userinfo = json.loads(getname)
        name = userinfo['user_info']['nickname']
        Path = name

        if downloadvideo:
            os.makedirs(f'{Path}', exist_ok=True)
        print(f'\n获取 {chinesename} 视频链接中，请稍候。。。。。。\n')
        json_data = {}
        total_num = 0
        k = len(timepool)

        for i in range(k):
            if i < k - 1:
                get_data(timepool[i], timepool[i + 1],chinesename)

    if downloadvideo:
        with ThreadPoolExecutor() as executor:
            task_list = []
            for key, value in json_data.items():
                task = executor.submit(get_video, key, value)
                task_list.append(task)
            for res in as_completed(task_list):
                print(res.result())

                print(f'\n{name}共下载 {total_num} 个抖音视频，请在当前目录下查看。')

        print('Enjoy it')
        print('Powered by wanglu58\n')


