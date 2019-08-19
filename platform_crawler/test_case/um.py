import requests

url = "https://apptrack.umeng.com/index.php"

querystring = {"c":"apps","a":"getplanlist","appid":"50594"}

headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
    'cookie': "UM_distinctid=16ab9636dcc641-0dd9957d5a2941-353166-1fa400-16ab9636dcd83d; cna=To5hFVM8jGICAXFhIhecmOtO; uc_session_id=2510bb47-5415-42ca-b64c-6f99ee5a4624; umplus_uc_token=1_DVAWsjOdXLjk3xUBhIFrw_4b20be5040af44cf8510220090e522ff; umplus_uc_loginid=wangxueping; isg=BNHRDxLKaQfHx4UTu4FpvTEi4N2rlncLE6M-K7NmaRi5WvGs-41zgSOz_G4Z0t3o; ap_ckid=1_1558681764_87b93334f65f916d243ca3a33d4212ca_67417_wangxueping; CNZZDATA1260676274=607033618-1558678819-https%253A%252F%252Fpassport.umeng.com%252F%7C1558678819; CNZZDATA1271963207=1905171273-1558679542-https%253A%252F%252Fpassport.umeng.com%252F%7C1558679542; cn_1271963207_dplus=1%5B%7B%7D%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%2216ab9636dcc641-0dd9957d5a2941-353166-1fa400-16ab9636dcd83d%22%2C%221558679542%22%2C%22https%3A%2F%2Fapptrack.umeng.com%2Findex.php%3Fc%3Dapps%22%2C%22apptrack.umeng.com%22%5D; cn_1258498910_dplus=1%5B%7B%7D%2C0%2C1558683245%2C0%2C1558683245%2C%22%24direct%22%2C%2216ab9636dcc641-0dd9957d5a2941-353166-1fa400-16ab9636dcd83d%22%2C%221557885527%22%2C%22%24direct%22%2C%22%24direct%22%5D",
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    # 'Postman-Token': "8c0ec0ed-f913-44ab-a63c-bf1639b4f3be,3c411ff1-7630-4a70-b3d9-e3843ae0ee3f",
    'Host': "apptrack.umeng.com",
    # 'Connection': "keep-alive",
    # 'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)