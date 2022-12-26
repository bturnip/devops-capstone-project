import os
import logging

from unittest import TestCase 
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)
BASE_URL = "/accounts"


app.config["TESTING"] = True
app.config["DEBUG"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
app.logger.setLevel(logging.CRITICAL)
init_db(app)


client = app.test_client()
'''
test_account01 = AccountFactory()
compare_fields = ['name','email','address','phone_number','date_joined']

for this_field in compare_fields:
    print(getattr(test_account01, this_field))


resp = client.post(BASE_URL
                   ,json=test_account01.serialize()
                   ,content_type="application/json")

test_data01 = resp.get_json()
print(f"+++DEBUG resp json (test_data01):\n {test_data01}\n")

for f in compare_fields:
    print(test_data01[f])

test01_id = test_data01["id"]
get_acct_url = f"{BASE_URL}/{test01_id}"
print(f"+++DEBUG: get_acct_url:{get_acct_url}")

#response = client.get(BASE_URL, json={'id':id}, content_type="application/json")
response = client.get(get_acct_url)
test_data02 = response.get_json()

print(f"+++DEBUG: status: {response.status}")

print(f"+++DEBUG: raw resp: {response}")
print(f"+++DEBUG: resp json (test_data02) {test_data02}")

test_id=0
print(f"=Testing with id={test_id} =========================================")

this_url = f"{BASE_URL}/{test_id}"
response = client.get(this_url)
test_data03 = response.get_json()

print(f"+++DEBUG: status: {response.status}")

print(f"+++DEBUG: raw resp: {response}")
print(f"+++DEBUG: resp json (test_data03) {test_data03}")


print("=Testing getting all accounts========================================")
print("+++DEBUG: creating accounts...")
for i in range(0,3):
    x = AccountFactory()
    client.post(BASE_URL, json=x.serialize(), content_type="application/json")


print(f"+++DEBUG: calling client.get(BASE_URL), BASE_URL: {BASE_URL}")
response = client.get(BASE_URL)

print("+++DEBUG: getting json from response...")
test_data04 = response.get_json()

print(f"+++DEBUG: status: {response.status}")

print(f"+++DEBUG: raw resp: {response}")
#print(f"+++DEBUG: resp json (test_data04) {test_data04}")
print(f"+++DEBUG: number of records: {len(test_data04)}")
'''

test_account01 = AccountFactory()
#compare_fields = ['name','email','address','phone_number','date_joined']
#for this_field in compare_fields:
#    print(getattr(test_account01, this_field))

print("+++DEBUG: creating account ++++++++++++++++++++++++++++++++++++++++")
resp = client.post(BASE_URL
                   ,json=test_account01.serialize()
                   ,content_type="application/json")

created_acct = resp.get_json()
target_id = created_acct["id"]

print(f"+++DEBUG: account creation status:{resp.status}")
print(f"+++DEBUG: target_id:{target_id}")


print("+++DEBUG: starting update process +++++++++++++++++++++++++++++++++")

created_acct["name"] = 'Foo X. Bar'
acct_id_url = f"{BASE_URL}/{target_id}"


response = client.put(acct_id_url,json=created_acct)

updated_record = response.get_json()

print(f"+++DEBUG: status: {response.status}")

print(f"+++DEBUG: raw resp: {response}")
print(f"+++DEBUG: resp json (updated_record) {updated_record}")

response = client.put(acct_id_url)
print(f"+++DEBUG: status is: {response.status}")

'''
bad_acct_url = f"{BASE_URL}/0"
response = client.put(bad_acct_url)
print(f"+++DEBUG: status is: {response.status}")
'''