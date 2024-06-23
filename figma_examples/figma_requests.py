import random
from datetime import date
import requests
from faker import Faker

fake = Faker()

BASE_URL = "http://127.0.0.1:8000"

# Figma 1: Registro e Login

# Gerar email e senha aleatórios
email = fake.email()
password = "testpassword"

# Passo 1: Registro (pular se já estiver registrado)
register_data = {
    "email": email,
    "password": password
}

register_response = requests.post(f"{BASE_URL}/register", json=register_data)
if register_response.status_code == 400:
    print("Usuário já registrado, prosseguindo para login.")
else:
    print("Resposta do Cadastro:", register_response.json())

# Passo 2: Login para obter o token JWT
login_data = {
    "username": email,
    "password": password
}

login_response = requests.post(f"{BASE_URL}/token", data=login_data)
if login_response.status_code != 200:
    print("Falha no login:", login_response.text)
    exit(1)
else:
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Token JWT:", token)

# Figma 2: Listar todas as empresas
response = requests.get(f"{BASE_URL}/companies", headers=headers)
if response.status_code != 200:
    print("Falha ao listar empresas:", response.text)
else:
    companies = response.json()
    print("Empresas:", companies)

if companies:
    company_id = companies[0]["id"]
else:
    company_id = None

# Figma 3: Registrar uma nova empresa (Novo Cadastro - Empresa)
nickname = str(fake.unique.company_suffix()) + " " + str(random.randint(1, 1000))
cnpj = f"00.000.000/{random.randint(1000, 9999)}-00"
company_data = {
    "nickname": nickname,
    "trade_name": f"{nickname} Fantasia",
    "legal_name": f"{nickname} Razão Social",
    "cnpj": cnpj,
    "state": "SP",
    "city": "Sao Paulo"
}

response = requests.post(f"{BASE_URL}/companies", json=company_data, headers=headers)
if response.status_code != 200:
    print("Falha ao cadastrar empresa:", response.text)
else:
    try:
        company = response.json()
        company_id = company["id"]
        print("ID da Empresa:", company_id)
    except requests.exceptions.JSONDecodeError:
        print("Erro ao decodificar resposta JSON ao cadastrar empresa:", response.text)

# Fazer upload do logo da empresa no S3
if company_id:
    file_path = "logo1.png"  
    with open(file_path, "rb") as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/companies/{company_id}/upload-logo", files=files, headers=headers)
        if response.status_code != 200:
            print("Falha ao fazer upload do logo:", response.text)
        else:
            logo_response = response.json()
            company['logo_url'] = logo_response['logo_url']
            print("Resposta do upload do logo:", logo_response)

    # Mostrar detalhes da empresa
    print("\nDetalhes da Empresa:")
    print(f"i. Apelido da empresa: {company['nickname']}")
    print(f"ii. Nome Fantasia: {company['trade_name']}")
    print(f"iii. Razão social: {company['legal_name']}")
    print(f"iv. CNPJ: {company['cnpj']}")
    print(f"v. UF: {company['state']}")
    print(f"vi. Cidade: {company['city']}")
    print(f"vii. Logo da empresa: {company['logo_url']}")

# Figma 4: Registrar novos departamentos e serviços (Novo Cadastro - Contrato)

# Criar departamentos
departments = ["Departmento A", "Departmento B"]
department_ids = {}

for dept in departments:
    response = requests.post(f"{BASE_URL}/departments", json={"name": dept}, headers=headers)
    if response.status_code != 200:
        print(f"Falha ao criar {dept}:", response.text)
    else:
        department_ids[dept] = response.json()["id"]
print("IDs dos Departamentos:", department_ids)

# Criar serviços
services = ["COMPRA", "VENDA", "TROCA"]
service_ids = {department_ids["Departmento A"]: [], department_ids["Departmento B"]: []}

for dept_name, dept_id in department_ids.items():
    for service in services:
        response = requests.post(f"{BASE_URL}/services", json={"name": service, "department_id": dept_id},
                                 headers=headers)
        if response.status_code != 200:
            print(f"Falha ao criar serviço {service} para {dept_name}:", response.text)
        else:
            service_ids[dept_id].append(response.json()["id"])
print("IDs dos Serviços:", service_ids)

# Garantir que company_id está definido antes de criar o contrato
if 'company_id' in locals() and company_id is not None:
    # Criar contrato
    contract_data = {
        "start_date": date.today().strftime("%Y-%m-%d"),
        "signature_date": date.today().strftime("%Y-%m-%d"),
        "rate": 5.0,
        "company_id": company_id,
        "departments": list(department_ids.values()),
        "services": list(service_ids[department_ids["Departmento A"]] + service_ids[department_ids["Departmento B"]])
    }

    response = requests.post(f"{BASE_URL}/contracts", json=contract_data, headers=headers)
    if response.status_code != 200:
        print("Falha ao criar contrato:", response.text)
    else:
        contract = response.json()
        contract_id = contract["id"]
        print("ID do Contrato:", contract_id)
        print("Informações do Contrato:")
        print(f"Data de Vigência: {contract['start_date']}")
        print(f"Data Assinatura: {contract['signature_date']}")
        print(f"Valor: {contract['rate']}")
        departments_names = [dep['name'] for dep in contract['departments']]
        print(f"Departamentos: {', '.join(departments_names)}")
        services_names = [srv['name'] for srv in contract['services']]
        print(f"Serviços: {', '.join(services_names)}")

    # Figma 5: Exibir todos os contratos e Dashboard
    response = requests.get(f"{BASE_URL}/contracts", headers=headers)
    if response.status_code != 200:
        print("Falha ao obter informações dos contratos:", response.text)
    else:
        contracts = response.json()
        print("Informações dos Contratos:", contracts)

        for contract in contracts:
            company = contract.get('company', {})
            company_nickname = company.get('nickname', 'Unknown')
            print(f"Cliente: {company_nickname}")
            print(f"Data de Vigência: {contract['start_date']}")
            print(f"Data Assinatura: {contract['signature_date']}")
            print(f"Valor: {contract['rate']}")
            departments_names = [dep['name'] for dep in contract['departments']]
            print(f"Departamentos: {', '.join(departments_names)}")
            print("---")

    response = requests.get(f"{BASE_URL}/dashboard/metrics", headers=headers)
    if response.status_code != 200:
        print("Falha ao obter métricas do dashboard:", response.text)
    else:
        metrics = response.json()
        print("Métricas do Dashboard:")
        print(f"Valor Total: {metrics['total_value']}")
        print(f"Meta Financeira: {metrics['indicator_1']}")
        print(f"Quantidade: {metrics['active_contracts_count']}")
        print(f"Meta Qtde: {metrics['indicator_2']}")
else:
    print("company_id não está definido, não é possível criar um contrato.")
