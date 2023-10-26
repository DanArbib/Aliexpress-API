import os

appkey = os.getenv('APP_KEY_ALI')
appSecret = os.getenv('APP_SECRET_ALI')
url = "https://api-sg.aliexpress.com/rest"
code = "3_501548_qFIbuo7J7Lkoy3NH65wrrxWJ2446"
access_token = '50000501942glPZqpe9biR9KtxfkFwkaGQVAjYmutgKxySotV0dS3x1d3eb96eFuKx01'

# {"refresh_token_valid_time":1696992831000,"havana_id":"17286341979","expire_time":1696906431000,"locale":"zh_CN","user_nick":"il106551989","access_token":"50000501942glPZqpe9biR9KtxfkFwkaGQVAjYmutgKxySotV0dS3x1d3eb96eFuKx01","refresh_token":"50001500742dePKcr8K9vXsPbc1kVFlUCRRddDEv8qs2fIgQG0CUKq189b1600HBZ3Yh","user_id":"106472795","account_platform":"buyerApp","refresh_expires_in":172800,"expires_in":86400,"sp":"ae","seller_id":"106472795","account":"danrg@windowslive.com","code":"0","request_id":"2140e0f016968200309442477"}

def generate_token_sdk():
    client = iop.IopClient(url, appkey, appSecret)
    request = iop.IopRequest('/auth/token/create')
    request.add_api_param('code', code)
    response = client.execute(request)
    print(response.type)
    print(response.body)

# generate_token_sdk()

def areNotEmpty(*args):
    return all(arg is not None and arg != '' for arg in args)

def generate_signature_class(params, api_name):
    sorted_keys = sorted(params.keys())

    query = []
    for key in sorted_keys:
        value = params[key]
        if areNotEmpty(key, value):
            query.append(f"{key}{value}")

    query_string = f"{api_name}{''.join(query)}"

    secret = bytes(appSecret, 'utf-8')  # Replace with your actual secret
    hashed = hmac.new(secret, query_string.encode('utf-8'), hashlib.sha256)
    signature = hashed.hexdigest().upper()

    return signature


def generate_token():
    endpoint = "/auth/token/create"
    full_url = url + endpoint
    timestamp = str(int(round(time.time()))) + "000"

    payload = {
        'app_key': appkey,
        'code': code,
        'sign_method': 'sha256',
        'timestamp': timestamp,
    }

    payload['sign'] = generate_signature_class(payload, endpoint)
    response = requests.get(full_url, params=payload)
    print(response.text)


# generate_token()


def calc():
    client = iop.IopClient(url, appkey, appSecret)
    request = iop.IopRequest('aliexpress.logistics.buyer.freight.calculate')
    request.add_api_param('param_aeop_freight_calculate_for_buyer_d_t_o', '{\"country_code\":\"RU\",\"price\":\"1.89\",\"product_id\":\"777777\",\"city_code\":\"99988777\",\"sku_id\":\"12000000424324\",\"product_num\":\"1\",\"send_goods_country_code\":\"CN\",\"province_code\":\"888777\",\"price_currency\":\"USD\"}')
    response = client.execute(request, access_token)
    print(response.type)
    print(response.body)

# calc()