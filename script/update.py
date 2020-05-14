# coding=utf-8
"""
请将此脚本加入计划任务中，自动更新日历
"""
import json
import logging
import os
import sqlite3
import time

import brotli
import requests

from bot_prcdCampaignCategory import parse_campaign

logger = logging.getLogger(__name__)
localdir = os.path.join(os.path.dirname(__file__), '../data')
distpath = os.path.join(os.path.dirname(__file__), '../app/calendar/dist')
if not os.path.exists(localdir):
    os.makedirs(localdir)
if not os.path.exists(distpath):
    os.makedirs(distpath)

formater = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
filehandler = logging.FileHandler(
    os.path.join(localdir, 'update.log'),
    encoding='utf-8',
)
filehandler.setFormatter(formater)
consolehandler = logging.StreamHandler()
consolehandler.setFormatter(formater)
logger.addHandler(filehandler)
logger.addHandler(consolehandler)
logger.setLevel(logging.INFO)


def update(name, verurl, dburl):
    localver = os.path.join(localdir, os.path.basename(verurl))
    localdb = os.path.join(localdir, name+'.sqlite')
    if os.path.exists(localver):
        with open(localver, 'r', encoding='utf-8') as lv:
            lvj = json.load(lv)
            localversion = int(lvj.get('TruthVersion', 0))
    else:
        localversion = 0
        logger.info('本地数据库不存在')
    rmver_res = requests.get(verurl)
    if rmver_res.status_code != 200:
        logger.info('服务器状态码错误')
        return -1
    rmver = int(rmver_res.json().get('TruthVersion', 0))
    if rmver <= localversion:
        logger.info('本地数据库已经是最新')
        return 0
    with open(localver, 'w') as lv:
        lv.write(rmver_res.text)
    rmdb_res = requests.get(dburl)
    if rmdb_res.status_code != 200:
        logger.info('服务器状态码错误')
        return -1
    rmdb = brotli.decompress(rmdb_res.content)
    with open(localdb, 'wb') as ld:
        ld.write(rmdb)
    data = []
    with sqlite3.connect(localdb) as con:
        for row in con.execute("""
            SELECT start_time, end_time
            FROM clan_battle_period
        """):
            data.append({
                'name': '公会战',
                'start_time': row[0],
                'end_time': row[1],
            })
        for row in con.execute("""
            SELECT start_time, end_time
            FROM campaign_freegacha
        """):
            data.append({
                'name': '免费十连',
                'start_time': row[0],
                'end_time': row[1],
            })
        for row in con.execute("""
            SELECT campaign_category, value, start_time, end_time
            FROM campaign_schedule
        """):
            campaign_name = parse_campaign(row[0])
            if campaign_name is None:
                continue
            data.append({
                'name': campaign_name+str(row[1]/1000)+'倍',
                'start_time': row[2],
                'end_time': row[3],
            })
        for row in con.execute("""
            SELECT start_time, end_time
            FROM tower_schedule
        """):
            data.append({
                'name': '露娜塔',
                'start_time': row[0],
                'end_time': row[1],
            })
        for row in con.execute("""
            SELECT a.start_time, a.end_time, b.title
            FROM hatsune_schedule AS a JOIN event_story_data AS b ON a.event_id = b.value
        """):
            data.append({
                'name': '活动：' + row[2],
                'start_time': row[0],
                'end_time': row[1],
            })
    with open(os.path.join(distpath, name+'.json'), 'w') as j:
        json.dump(data, j, ensure_ascii=True, separators=(',', ':'))
        logger.info('更新成功')


logger.info('更新国服数据')
try:
    update(
        'cn',
        'https://redive.estertion.win/last_version_cn.json',
        'https://redive.estertion.win/db/redive_cn.db.br',
    )
except Exception as e:
    logger.exception(e)

logger.info('更新日服数据')
try:
    update(
        'jp',
        'https://redive.estertion.win/last_version_jp.json',
        'https://redive.estertion.win/db/redive_jp.db.br',
    )
except Exception as e:
    logger.exception(e)
