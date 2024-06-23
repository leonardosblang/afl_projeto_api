import os
import random
import unittest
from datetime import date

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


class TestContract(unittest.TestCase):
    connection = None
    session = None
    company_id = None
    department_ids = []
    service_ids = []

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

        cnpj = f"00.000.000/{random.randint(1000, 9999)}-00"
        nickname = str(fake.unique.company_suffix()) + " " + str(random.randint(1, 1000))
        company_response = requests.post(f"{BASE_URL}/companies", json={
            "nickname": nickname,
            "trade_name": f"{nickname} Fantasia",
            "legal_name": f"{nickname} Razão Social",
            "cnpj": cnpj,
            "state": "SP",
            "city": "Sao Paulo"
        }, headers=cls.headers)
        cls.company_id = company_response.json()["id"]

        file_path = "logo3.png"
        with open(file_path, "rb") as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/companies/{cls.company_id}/upload-logo", files=files,
                                     headers=cls.headers)
            if response.status_code != 200:
                raise Exception("Failed to upload logo")

        departments = ["Department A", "Department B"]
        for dept in departments:
            dept_response = requests.post(f"{BASE_URL}/departments", json={"name": dept}, headers=cls.headers)
            cls.department_ids.append(dept_response.json()["id"])

        services = ["COMPRA", "VENDA", "TROCA"]
        for dept_id in cls.department_ids:
            for service in services:
                service_response = requests.post(f"{BASE_URL}/services",
                                                 json={"name": service, "department_id": dept_id}, headers=cls.headers)
                cls.service_ids.append(service_response.json()["id"])

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

    def test_create_contract(self):
        print("Running test_create_contract...")
        response = requests.post(f"{BASE_URL}/contracts", json={
            "start_date": date.today().strftime("%Y-%m-%d"),
            "signature_date": date.today().strftime("%Y-%m-%d"),
            "rate": 5.0,
            "services": self.service_ids,
            "departments": self.department_ids,
            "company_id": self.company_id
        }, headers=self.headers)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.content}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.json())
        TestContract.contract_id = response.json()["id"]

    def test_get_contract(self):
        print("Running test_get_contract...")

        create_response = requests.post(f"{BASE_URL}/contracts", json={
            "start_date": date.today().strftime("%Y-%m-%d"),
            "signature_date": date.today().strftime("%Y-%m-%d"),
            "rate": 5.0,
            "services": self.service_ids,
            "departments": self.department_ids,
            "company_id": self.company_id
        }, headers=self.headers)

        print(f"Create response status: {create_response.status_code}")
        print(f"Create response content: {create_response.content}")

        self.assertEqual(create_response.status_code, 200, "Failed to create contract")

        create_data = create_response.json()
        self.assertIn("id", create_data, "Contract creation response doesn't contain 'id'")
        contract_id = create_data["id"]

        import time
        time.sleep(1)

        get_response = requests.get(f"{BASE_URL}/contracts/{contract_id}", headers=self.headers)

        print(f"Get response status: {get_response.status_code}")
        print(f"Get response content: {get_response.content}")

        self.assertEqual(get_response.status_code, 200,
                         f"Failed to retrieve contract. Status: {get_response.status_code}")

        try:
            get_data = get_response.json()
            self.assertIn("rate", get_data, "Retrieved contract data doesn't contain 'rate'")
            self.assertEqual(get_data["rate"], 5.0, "Contract rate doesn't match")
        except requests.exceptions.JSONDecodeError as e:
            self.fail(f"Failed to decode JSON. Error: {str(e)}. Content: {get_response.content}")


if __name__ == "__main__":
    unittest.main()
