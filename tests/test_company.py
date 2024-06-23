import os
import random
import unittest

import requests
from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session

load_dotenv()

fake = Faker()

BASE_URL = "http://127.0.0.1:8000"
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"{os.getenv('POSTGRES_HOST')}:"
    f"{os.getenv('POSTGRES_PORT')}/"
    f"{os.getenv('POSTGRES_DB')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
metadata = MetaData()


class TestCompany(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Registering and logging in user...")
        cls.email = fake.email()
        cls.password = "testpassword"

        requests.post(f"{BASE_URL}/register", json={
            "email": cls.email,
            "password": cls.password
        })
        response = requests.post(f"{BASE_URL}/token", data={
            "username": cls.email,
            "password": cls.password
        })
        cls.token = response.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        cls.connection = engine.connect()

    @classmethod
    def tearDownClass(cls):
        SessionLocal.remove()
        cls.connection.close()

    def setUp(self):
        print("Setting up test case...")
        self.transaction = self.connection.begin_nested()

    def tearDown(self):
        print("Tearing down test case...")
        self.transaction.rollback()
        SessionLocal.remove()

    def test_create_company(self):
        print("Running test_create_company...")
        nickname = str(fake.unique.company_suffix()) + " " + str(random.randint(1, 1000))
        cnpj = f"00.000.000/{random.randint(1000, 9999)}-00"
        response = requests.post(f"{BASE_URL}/companies", json={
            "nickname": nickname,
            "trade_name": f"{nickname} Fantasia",
            "legal_name": f"{nickname} Razão Social",
            "cnpj": cnpj,
            "state": "SP",
            "city": "Sao Paulo"
        }, headers=self.headers)
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        TestCompany.company_id = response.json()["id"]

    def test_upload_logo(self):
        print("Running test_upload_logo...")
        if not hasattr(TestCompany, 'company_id'):
            self.skipTest("Skipping test_upload_logo because company_id is not set.")
        file_path = "logo2.png"
        with open(file_path, "rb") as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/companies/{TestCompany.company_id}/upload-logo", files=files,
                                     headers=self.headers)
        print(response.json())
        self.assertEqual(response.status_code, 200)

    def test_get_company(self):
        print("Running test_get_company...")
        if not hasattr(TestCompany, 'company_id'):
            self.skipTest("Skipping test_get_company because company_id is not set.")
        response = requests.get(f"{BASE_URL}/companies/{TestCompany.company_id}", headers=self.headers)
        try:
            response_json = response.json()
            print(response_json)
            self.assertEqual(response.status_code, 200)
            self.assertIn("nickname", response_json)
        except requests.exceptions.JSONDecodeError:
            print("Response content is not valid JSON")
            self.fail("Response content is not valid JSON")

    def test_list_companies(self):
        print("Running test_list_companies...")
        response = requests.get(f"{BASE_URL}/companies", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        companies = response.json()
        print("Companies:", companies)
        self.assertIsInstance(companies, list)
        nicknames = [company['nickname'] for company in companies]
        self.assertEqual(len(nicknames), len(set(nicknames)), "Duplicate company nicknames found")


if __name__ == "__main__":
    unittest.main()
