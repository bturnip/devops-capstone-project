"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
import random
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status  # HTTP Status Codes
from service.models import db, Account, init_db
from service.routes import app
from service import talisman

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/accounts"

HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        talisman.force_https = False
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Account).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_accounts(self, count):
        """Factory method to create accounts in bulk"""
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Account",
            )
            new_account = response.get_json()
            account.id = new_account["id"]
            accounts.append(account)
        return accounts

    ######################################################################
    #  A C C O U N T   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_create_account(self):
        """It should Create a new Account"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], account.name)
        self.assertEqual(new_account["email"], account.email)
        self.assertEqual(new_account["address"], account.address)
        self.assertEqual(new_account["phone_number"], account.phone_number)
        self.assertEqual(new_account["date_joined"], str(account.date_joined))

    def test_bad_request(self):
        """It should not Create an Account when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Account when sending the wrong media type"""
        account = AccountFactory()
        response = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    # ADD YOUR TEST CASES HERE ...
    def test_read_an_account(self):
        """NEW: Read an Account, return account details"""
        #--Make a self.client.post() call to accounts to create a new account 
        #  passing in some account data
        test_account01 = AccountFactory()

        response = self.client.post(
            BASE_URL,
            json=test_account01.serialize(),
            content_type="application/json"
        )
        
        #--Get back the account id that was generated from the json
        test_data01 = response.get_json()
        test01_id = test_data01["id"]
        self.assertIsNotNone(test01_id)

        #--Make a self.client.get() call to /accounts/{id} passing in
        #  that account id.  Assert return code was "200 OK"
        get_acct_url = f"{BASE_URL}/{test01_id}"
        response = self.client.get(get_acct_url)
        self.assertEqual('200 OK',response.status)

        #--Check the json that was returned and assert that it is equal 
        #  to the data that you sent.
        test_data02 = response.get_json()
        compare_fields = ['name','email','address','phone_number','date_joined']
        for this_field in compare_fields:
            expected_result = str(getattr(test_account01, this_field))
            test_result = test_data02[this_field]
            self.assertEqual(expected_result, test_result)

    def test_account_not_found(self):
        """ Return a 404 NOT FOUND status when an account id is not found """
        test_id = 0
        expected_status = "404 NOT FOUND"

        test_url = f"{BASE_URL}/{test_id}"
        response = self.client.get(test_url)
        self.assertEqual(expected_status,response.status)

    def test_get_account_list(self):
        """It should Get a list of Accounts"""
        expected_status = "200 OK"
        expected_record_count =  5
        self._create_accounts(expected_record_count)
        # send a self.client.get() request to the BASE_URL
        # query_string=""
        response = self.client.get(BASE_URL)

        # assert that the resp.status_code is status.HTTP_200_OK
        self.assertEqual("200 OK", response.status)
        # get the data from resp.get_json()
        test_data01 = response.get_json()
        # assert that the len() of the data is 5 (the number of accounts you created)
        self.assertIsInstance(test_data01,list)
        self.assertEqual(expected_record_count,len(test_data01))

    def test_empty_account_database(self):
        """Any empty list of Accounts should be [] and '200 OK' """
        
        expected_record_count = 0
        expected_status = "200 OK"
        
        response = self.client.get(BASE_URL)
        test_data02 = response.get_json()
        
        self.assertEqual(expected_status,response.status)
        self.assertEqual(expected_record_count,len(test_data02))

    def test_update_account(self):
        """It should Update an existing Account"""
        # create an Account to update

        test_account01 = AccountFactory()
        # send a self.client.post() request to the BASE_URL with a json payload of test_account.serialize()
        response = self.client.post(
            BASE_URL,
            json=test_account01.serialize(),
            content_type="application/json")
    
        # assert that the resp.status_code is status.HTTP_201_CREATED
        expected_status = '201 CREATED'
        self.assertEqual(expected_status,response.status)

        # update the account
        new_account = response.get_json()
        update_name = 'Foo X. Bar'

        new_account["name"] = update_name
        target_id = new_account["id"]
        acct_id_url = f"{BASE_URL}/{target_id}"

        response = self.client.put(acct_id_url,json=new_account)

        expected_status = '200 OK'
        self.assertEqual(expected_status,response.status)
        
        updated_acct = response.get_json()
        self.assertEqual(update_name, updated_acct["name"])

    def test_update_with_bad_date(self):
        """ Non-existant account returns 404 on update request """
        bad_acct_url = f"{BASE_URL}/0"
        response = self.client.put(bad_acct_url)
        expected_status = '404 NOT FOUND'
        self.assertEqual(expected_status,response.status)

    def test_delete_account(self):
        """ Test deleting accounts by id """
        #--create some records, pick a random record to delete
        expected_record_count =  10
        random_record_num = random.randrange(0, expected_record_count)
        
        self._create_accounts(expected_record_count)
        response = self.client.get(BASE_URL)
        test_data = response.get_json()
        target_id = test_data[random_record_num]["id"]

        #--delete the record, check response status
        delete_url = f"{BASE_URL}/{target_id}"
        response = self.client.delete(delete_url)

        expected_status = '204 NO CONTENT'
        self.assertEqual(expected_status,response.status)

        #--check that the id is no longer found
        response = self.client.get(delete_url)
        expected_status = "404 NOT FOUND"
        self.assertEqual(expected_status,response.status)

    def test_delete_non_existant_account(self):
        """ Test deleting non-existant id """
        #--attempt to delete a known non-existant record
        delete_url = f"{BASE_URL}/0"
        response = self.client.delete(delete_url)

        expected_status = '204 NO CONTENT'
        self.assertEqual(expected_status,response.status)
    
    def test_method_not_supported(self):
        """ Test error handler for HTTP-405 """
        test_url = f"{BASE_URL}/0"
        bad_request_response = self.client.patch(test_url)
        expected_status = '405 METHOD NOT ALLOWED'
        self.assertEqual(expected_status,bad_request_response.status)
    
    def test_http_environ(self):
        """ HTTPS_ENVIRON should return the XSS/Security Headers """
        expected_results = {'X-Frame-Options': 'SAMEORIGIN'
                            ,'X-XSS-Protection': '1; mode=block'
                            ,'X-Content-Type-Options': 'nosniff'
                            ,'Content-Security-Policy': 'default-src \'self\'; object-src \'none\''
                            ,'Referrer-Policy': 'strict-origin-when-cross-origin'}
        
        response = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
        
        for this_header,expected_val in expected_results.items():
            self.assertEqual(expected_val
                             ,response.headers.get(this_header))




        



