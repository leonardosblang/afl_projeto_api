import random
from datetime import date

import requests
from faker import Faker

fake = Faker()

BASE_URL = "http://127.0.0.1:8000"


def get_jwt_token():
    email = fake.email()
    password = "testpassword"

    register_response = requests.post(f"{BASE_URL}/register", json={"email": email, "password": password})
    if register_response.status_code == 400:
        print("Usuário já registrado, prosseguindo para login.")
    else:
        print("Resposta do registro:", register_response.json())

    login_response = requests.post(f"{BASE_URL}/token", data={"username": email, "password": password})
    if login_response.status_code != 200:
        print("Falha no login:", login_response.text)
        exit(1)
    else:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Token JWT:", token)
        return headers


headers = get_jwt_token()

company_id = input("Digite o ID da empresa: ")

departments = ["Departamento A", "Departamento B"]
department_ids = {}

for dept in departments:
    response = requests.post(f"{BASE_URL}/departments", json={"name": dept}, headers=headers)
    if response.status_code != 200:
        print(f"Falha ao criar {dept}:", response.text)
    else:
        department_ids[dept] = response.json()["id"]
print("IDs dos Departamentos:", department_ids)

services = ["COMPRA", "VENDA", "TROCA"]
service_ids = {department_ids["Departamento A"]: [], department_ids["Departamento B"]: []}

for dept_name, dept_id in department_ids.items():
    for service in services:
        response = requests.post(f"{BASE_URL}/services", json={"name": service, "department_id": dept_id},
                                 headers=headers)
        if response.status_code != 200:
            print(f"Falha ao criar serviço {service} para {dept_name}:", response.text)
        else:
            service_ids[dept_id].append(response.json()["id"])
print("IDs dos Serviços:", service_ids)

contract_data_1 = {
    "start_date": date.today().strftime("%Y-%m-%d"),
    "signature_date": date.today().strftime("%Y-%m-%d"),
    "rate": random.uniform(1, 10),
    "company_id": company_id,
    "departments": list(department_ids.values()),
    "services": list(service_ids[department_ids["Departamento A"]] + service_ids[department_ids["Departamento B"]])
}

response_1 = requests.post(f"{BASE_URL}/contracts", json=contract_data_1, headers=headers)
print("Resposta da criação do primeiro contrato:", response_1.json())

contract_data_2 = {
    "start_date": date.today().strftime("%Y-%m-%d"),
    "signature_date": date.today().strftime("%Y-%m-%d"),
    "rate": random.uniform(1, 10),
    "company_id": company_id,
    "departments": list(department_ids.values()),
    "services": list(service_ids[department_ids["Departamento A"]] + service_ids[department_ids["Departamento B"]])
}

response_2 = requests.post(f"{BASE_URL}/contracts", json=contract_data_2, headers=headers)
print("Resposta da criação do segundo contrato:", response_2.json())

delete_confirmation = input("Deseja excluir a empresa? (s/n): ").strip().lower()
if delete_confirmation == 's':
    delete_response = requests.delete(f"{BASE_URL}/companies/{company_id}", headers=headers)
    print("Resposta da exclusão da empresa:", delete_response.json())
else:
    print("Empresa não foi excluída.")

dashboard_response = requests.get(f"{BASE_URL}/dashboard/contracts", headers=headers)
print("Todos os contratos:", dashboard_response.json())
