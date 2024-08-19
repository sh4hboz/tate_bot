import requests
import json
from tonsdk.utils import to_nano


async def check_ton_wallet(owner_wallet: str, from_wallet: str, value: float):
    url = "https://toncenter.com/api/v2/getTransactions"
    params = {
        "address": owner_wallet,
        "limit": 20
    }
    vlnano = to_nano(value, 'ton')
    resp = requests.get(url=url, params=params)
    if resp.status_code == 200:
        transactions = resp.json()

        try:
            for i in range(20):
                source = transactions.get("result", [])[i].get("in_msg", {}).get("source", None)
                # formatted_json = json.dumps(transactions.get("result", [])[i].get("in_msg", {}), indent=4,
                #                             ensure_ascii=False)
                # print(formatted_json)
                if source == from_wallet:
                    source = transactions.get("result", [])[i].get("in_msg", {}).get("value", None)
                    # print(f"src:{source}")
                    # print(f"val:{vlnano}")
                    if int(source) == int(vlnano):
                        return {"status": "success"}
            return {"status": "error", "error": "can't find transaction"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    else:
        return {"status": "error", "error": f"Ошибка при запросе данных: {resp.status_code}"}
