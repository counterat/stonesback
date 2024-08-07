import hmac
import hashlib
from urllib.parse import unquote
from config import API_TOKEN_FOR_TGBOT


def validate_initdata(init_data: str, bot_token: str):
     vals = {k: unquote(v) for k, v in [s.split('=', 1) for s in init_data.split('&')]}
     data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(vals.items()) if k != 'hash')

     secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
     h = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256)

     return h.hexdigest() == vals['hash'], vals