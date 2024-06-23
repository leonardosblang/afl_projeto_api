import os
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


class TestAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Registering user...")
        cls.connection = engine.connect()
        cls.email = fake.email()
        cls.password = "testpassword"

        response = requests.post(f"{BASE_URL}/register", json={
            "email": cls.email,
            "password": cls.password
        })
        if response.status_code == 400:
            print("User already registered")
        else:
            print(response.json())

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

    def test_register_user(self):
        print("Running test_register_user...")
        new_email = fake.email()
        response = requests.post(f"{BASE_URL}/register", json={
            "email": new_email,
            "password": "new_testpassword"
        })
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())

    def test_login_user(self):
        print("Running test_login_user...")
        response = requests.post(f"{BASE_URL}/token", data={
            "username": self.email,
            "password": self.password
        })
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())


if __name__ == "__main__":
    unittest.main()
