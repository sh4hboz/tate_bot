import requests

Token = "q6AUI7RYhksYMQ2HbhDDBA6pA16HS4l4YGYbgvn/OfKXyuEjfPPTMlb?BNC-?NWbC168ne0r8=zDWmAPHe3ogFQdNimC4UfVhK?L41wqn1D?2qOZn2YntAf=JTUG5gg=949v697L-DD5aU9Zm1peZDQ!QPLq1lNOLUPC?BPGe4hsK=ClQw!6Gvv7uhPZNWUUaIJDYS?oA/Eq6k!EcK8u-TE3X8jAyPxc4gnywT24LSAu2GStTkc/1BvkukuKC85x"
urls = "http://127.0.0.1:8000/authorize"

telegram_id = {"telegram_id":"7840305"}

jsonv = {"telegram_id": 7840305,
         "balance": 0,
        }
# req = requests.get(url=urls, headers={"Token": Token})
# requ = requests.post(url="http://127.0.0.1:8000/add_user", headers={"Token": Token}, json=jsonv)
requ = requests.post(url=urls, headers={"Token": Token}, json=telegram_id)

print(requ.text)

