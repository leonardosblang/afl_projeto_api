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


class TestServices(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("Registering and logging in user...")

        email = fake.email()
        password = "testpassword"
        requests.post(f"{BASE_URL}/register", json={
            "email": email,
            "password": password
        })
        response = requests.post(f"{BASE_URL}/token", data={
            "username": email,
            "password": password
        })
        cls.token = response.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {cls.token}"}
        cls.connection = engine.connect()

        department_response = requests.post(f"{BASE_URL}/departments", json={
            "name": "Department A"
        }, headers=cls.headers)
        cls.department_id = department_response.json()["id"]

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

    def test_create_service(self):
        print("Running test_create_service...")
        response = requests.post(f"{BASE_URL}/services", json={
            "name": "COMPRA",
            "department_id": self.department_id
        }, headers=self.headers)
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        TestServices.service_id = response.json()["id"]

    def test_get_service(self):
        print("Running test_get_service...")

        response = requests.post(f"{BASE_URL}/services", json={
            "name": "VENDA",
            "department_id": self.department_id
        }, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        service_id = response.json()["id"]

        response = requests.get(f"{BASE_URL}/services/{service_id}", headers=self.headers)
        try:
            response_json = response.json()
            print(response_json)
            self.assertEqual(response.status_code, 200)
            self.assertIn("name", response_json)
        except requests.exceptions.JSONDecodeError:
            print("Response content is not valid JSON")
            self.fail("Response content is not valid JSON")

    def test_delete_service(self):
        print("Running test_delete_service...")
        response = requests.delete(f"{BASE_URL}/services/{TestServices.service_id}", headers=self.headers)
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})


if __name__ == "__main__":
    unittest.main()
