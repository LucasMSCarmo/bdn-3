import os
import redis
import pymongo
from pymongo.server_api import ServerApi
import hashlib
from bson import ObjectId

r = redis.Redis(
    host='redis-19281.crce216.sa-east-1-2.ec2.redns.redis-cloud.com',
    port=19281,
    decode_responses=True,
    username="default",
    password="OicLGVQAaatf4inEp1375RvXp7fm6E2G",
)
client = pymongo.MongoClient("mongodb+srv://LucasMartins:12345aeiou@teste.ikohdgy.mongodb.net/?retryWrites=true&w=majority&appName=teste", server_api=ServerApi('1'))
mydb = client.commerce

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

while True:
    print("=== LOGIN ===")
    email = input("Email: ")
    senha = hashlib.sha256(input("Senha: ").encode()).hexdigest()
    cliente = mydb.cliente.find_one({'email': email, 'senha': senha})
    if cliente:
        print(f"\nBem-vindo, {cliente['nome']}!\n")
        break
    else:
        print("Credenciais inválidas.\n")
        if input("Tentar novamente? (s/n): ").lower() != 's':
            exit()
        limpar()

while True:
    print("""
============================================================
➕ CADASTRAR
------------------------------------------------------------
|  1  | 👤 Endereço

🔍 CONSULTAR
------------------------------------------------------------
|  2  | 👤 Perfil

🔄 ATUALIZAR
------------------------------------------------------------
|  3  | 👤 Dados pessoais  |  4  | 🏠 Endereço
------------------------------------------------------------

🗑️  DELETAR
------------------------------------------------------------
|  5  | 🏠 Endereço
============================================================
🔚 SISTEMA
------------------------------------------------------------
| 0  | ❌ Sair
============================================================
    """)
    opcao = int(input("Digite a opção desejada: "))
    limpar()

    if opcao == 1:
        print("\n--- CADASTRAR ENDEREÇO ---\n")
        enderecos = []
        while True:
            logradouro = input("Logradouro: ").strip()
            numero = input("Número: ").strip()
            complemento = input("Complemento: ").strip()
            bairro = input("Bairro: ").strip()
            cidade = input("Cidade: ").strip()
            estado = input("Estado: ").strip()
            
            dados = {
                "_id": ObjectId(),
                "logradouro": logradouro,
                "numero": numero,
                "complemento": complemento,
                "bairro": bairro,
                "cidade": cidade,
                "estado": estado
            }

            if input("Confirmar endereço? (s/n): ").lower() == 's':
                enderecos.append(dados)

            if input("\nDeseja adicionar outro endereço? (s/n): ").lower() != 's':
                break

        if enderecos:
            resposta = mydb.cliente.update_one(
                {"_id": cliente['_id']},
                {"$push": {"enderecos": {"$each": enderecos}}}
            )
            if resposta.modified_count > 0:
                print("\nEndereço(s) cadastrado(s) com sucesso.")
                cliente['enderecos'].extend(enderecos)
            else:
                print("\nFalha ao cadastrar o endereço.")
        else:
            print("\nNenhum endereço foi cadastrado.")
    elif opcao == 2:
        print("\n--- PERFIL ---\n")
        print(
            f"Nome: {cliente['nome']}",
            f"\nCPF: {cliente['cpf']}",
            f"\nEmail: {cliente['email']}",
            f"\nTelefone: {cliente['telefone']}",
            )
        numero_enderecos = len(cliente["enderecos"])
        if numero_enderecos > 0:
            print(f"Endereço:" if numero_enderecos == 1 else "Endereços:")
            for endereco in cliente["enderecos"]:
                numero_enderecos -= 1
                print(
                    f"\n    {endereco['logradouro']}, {endereco['numero']}{' - ' + endereco['complemento'] if endereco['complemento'] else ''}",
                    f"\n    {endereco['bairro']}",
                    f"\n    {endereco['cidade']} - {endereco['estado']}"
                )
                if numero_enderecos != 0:
                    print(f"    --------------------------------")

    elif opcao == 3:
        print("\n--- ATUALIZAR DADOS ---\n")
        print("Dados atuais:",
                f"\n    --------------------------------",
                f"\n    Nome: {cliente['nome']}",
                f"\n    CPF: {cliente['cpf']}",
                f"\n    Email: {cliente['email']}",
                f"\n    Telefone: {cliente['telefone']}")

        print("\nNovos dados (deixe vazio para manter o atual):")
        print("    --------------------------------")
        nome = input("    Nome: ").strip()
        cpf = input("    CPF: ").strip()
        email = input("    Email: ").strip()
        senha_raw = input("    Senha: ").strip()
        telefone = input("    Telefone: ").strip()

        dados = {}
        if nome:
            dados['nome'] = nome
        if cpf:
            dados['cpf'] = cpf
        if email:
            dados['email'] = email
        if senha_raw:
            dados['senha'] = hashlib.sha256(senha_raw.encode('utf-8')).hexdigest()
        if telefone:
            dados['telefone'] = telefone

        for dado in dados:
            result = mydb.cliente.update_one(
                {"_id": cliente['_id']},
                {"$set": {dado: dados[dado]}},
            )
            if result.modified_count > 0:
                print(f"{dado.title()} atualizado com sucesso.")
                cliente[dado] = dados[dado]
            else:
                print(f"Falha ao atualizar {dado}.")

    elif opcao == 4:
        print("\n--- CADASTRO DE VENDEDOR ---\n")
        insertVendedor(mydb.vendedor)
    elif opcao == 5:
        print("\n--- LISTA DE CLIENTES ---\n")
        findClientes(mydb.cliente)
    elif opcao == 0:
        print("Saindo do sistema...")
        break
    else:
        limpar()