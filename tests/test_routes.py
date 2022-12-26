"""
Account API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
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


######################################################################
#  T E S T   C A S E S
######################################################################
class TestAccountService(TestCase):
    """Account Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
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
        self._create_accounts(5)
        # send a self.client.get() request to the BASE_URL
        #query_string=""
        response = self.client.get(BASE_URL)

        # assert that the resp.status_code is status.HTTP_200_OK
        self.assertEqual("200 OK", response.status)
        # get the data from resp.get_json()
        test_data01 = response.get_json()
        # assert that the len() of the data is 5 (the number of accounts you created)
        self.assertIsInstance(test_data01,list)
        self.assertEqual(5,len(test_data01))
