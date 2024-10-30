def get_headers(user_agent: str, token: str = None) -> dict:
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'ru',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Host': 'api.paws.community',
        'Origin': 'https://app.paws.community',
        'Referer': 'https://app.paws.community/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': user_agent
    }
    
    if token:
        headers['Authorization'] = f'Bearer {token}'
        
    return headers