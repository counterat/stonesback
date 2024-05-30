import uuid
import requests
import json
import hashlib
import base64

"""Configuration.account_id = '279766'
Configuration.secret_key = 'test_mCOp94-o-3DjFG5NHGk0mkD0YXcp1EuPpuWeyat3uvE'"""
"""
def create_payment_for_user(amount, currency='RUB'):
    idempotence_key = uuid.uuid4()
    payment = Payment.create({
    "amount": {
        "value": f"{amount}",
        "currency": f"{currency}"
    },
    "confirmation": {
        "type": "embedded"
  
    },
    "capture": True,
    "description": "Заказ",
    "save_payment_method": True
},idempotence_key)
    
    return payment, idempotence_key
"""

def cryptomus(data:dict, url:str):
    encoded_data = base64.b64encode(
        json.dumps(data).encode("utf-8")
    ).decode("utf-8")
    merchant ='f6771c05-4fb6-4080-b67b-241dd1ca864c'
    key = 'mHc0WYZGw4dK67nkkHkkUbFv8mVWzUxFdN8HU5yU7DOOQ95iSmMAZ0fq5Ld00h1CpjA3es4AzCQ4LZYqenXnKhOcocln6zSaBO4B5zQVP9HEPRXwdGZ0tuscImdMkPjv'
    if url == 'https://api.cryptomus.com/v1/payout':
        key = 'mDcgqIanEENcuULU7SDR1DPoSZl9uuc4Lef6FHlpuzFhWYNBI8MvRYM1kBwTLL7qqt7pQ0IrfVXiD9ZwdmGB12gnDLqzlfS7CBaHxOtZYcCiEwIi2Rzuvq1DhC95LJNw'
    signature = hashlib.md5(f"{encoded_data}{key}".
                            encode("utf-8")).hexdigest()

    response = requests.post(url, headers={
        "merchant": merchant,
        "sign": signature,
    }, json=data)
    return (response.json())