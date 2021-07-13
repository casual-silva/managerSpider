import sys

import os
import traceback

import requests
import json

headers = {
 "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
 "accept-encoding": "gzip, deflate, br",
 "accept-language": "zh-CN,zh;q=0.9",
 "cookie": "session-id=135-1220550-5612754; session-id-time=2082787201l; i18n-prefs=USD; skin=noskin; ubid-main=133-6987697-9472907; session-token=OF+pFEhZkD65+RGB79iW1taJ67S7G2gt8YYEkk1reyZA89olIGdywPsMiZV+dMQo7QvDQITX17WokHeBmdhY2PHRGAPwAGiCAC1AOHGxxhOLbrAhsXmqGvViDfjyzcWbqHCU/rDyWneW0P2wOxEuKnoJ3wL73DQ3nLwU0MdeGbnSnkIUDrFRu+udx14YnTm3; lc-main=en_US; csm-hit=tb",
 "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}
# 经过验证 cookie是否过期对抓取没有影响
rsp = requests.get('https://www.amazon.com/PetSafe-Drinkwell-Mini-Water-Fountain/dp/B00G15EGOE/ref=sr_1_15?_encoding=UTF8&c=ts&dchild=1&keywords=Cat+Fountains&qid=1623496443&s=pet-supplies&sr=1-15&ts_id=2975263011',
                   headers=headers)
print(rsp.text)
