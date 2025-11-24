import os
import redis
import pymongo
from pymongo.server_api import ServerApi
import hashlib
from bson import ObjectId
import json

r = redis.Redis(
    host='redis-12456.crce181.sa-east-1-2.ec2.cloud.redislabs.com',
    port=12456,
    decode_responses=True,
    username="default",
    password="k2Gx1BSLjgTRizl0ftGv1i1YceljluuN",
)
global session
client = pymongo.MongoClient("mongodb+srv://LucasMartins:12345aeiou@teste.ikohdgy.mongodb.net/?retryWrites=true&w=majority&appName=teste", server_api=ServerApi('1'))
mydb = client.commerce

def limpar():
    os.system("cls" if os.name == "nt" else "clear")

def tempo_restante_sessao(user_id):
    ttl = r.ttl(f"session:{user_id}")
    if ttl >= 3600:
        tempo = f"{ttl // 3600} hora(s)"
        if ttl % 3600 >= 60:
            tempo += f", { (ttl % 3600) // 60 } minuto(s)"
        if ttl % 60 > 0:
            tempo += f" e { ttl % 60 } segundo(s)"
    elif ttl >= 60:
        tempo = f"{ttl // 60} minuto(s)"
        if ttl % 60 > 0:
            tempo += f" e { ttl % 60 } segundo(s)"
    else:
        tempo = f"{ttl} segundo(s)"
    if ttl == -2:
        print("Sessão expirada ou não encontrada.")
        return 0
    elif ttl == -1:
        print("Sessão ativa, sem tempo limite.")
        return None
    else:
        print(f"Sua sessão expira em {tempo}. Salve seu progresso.")
        return ttl

def cliente_to_redis_dict(cliente):
    cliente['_id'] = str(cliente['_id'])
    if 'enderecos' in cliente and isinstance(cliente['enderecos'], list):
        for endereco in cliente['enderecos']:
            if '_id' in endereco:
                endereco['_id'] = str(endereco['_id'])
    return cliente

while True:
    print("=== LOGIN ===")
    email = input("Email: ")
    senha = hashlib.sha256(input("Senha: ").encode()).hexdigest()
    cliente = mydb.cliente.find_one({'email': email, 'senha': senha})
    if cliente:
        r.setex(f"session:{str(cliente['_id'])}", 5, json.dumps(cliente_to_redis_dict(cliente), default=str))
        session = json.loads(r.get(f"session:{str(cliente['_id'])}"))
        print(f"\nBem-vindo, {cliente['nome']}!\n")
        break
    else:
        print("Credenciais inválidas.\n")
        if input("Tentar novamente? (s/n): ").lower() != 's':
            exit()
        limpar()



while True:
    tempo_restante_sessao(session['_id'])
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
                "_id": str(ObjectId()),
                "logradouro": logradouro,
                "numero": numero,
                "complemento": complemento,
                "bairro": bairro,
                "cidade": cidade,
                "estado": estado
            }

            if input("Confirmar endereço? (s/n): ").lower() == 's':
                enderecos.append(dados)

            if input("\nDeseja adicionar outro endereço? (s/n): ") .lower() != 's':
                break

        if enderecos:
            if 'enderecos' not in session or not isinstance(session['enderecos'], list):
                session['enderecos'] = []
            session['enderecos'].extend(enderecos)
            sucesso = r.setex(f"session:{session['_id']}", 3600, json.dumps(session, default=str))

            if sucesso:
                print("\nEndereço(s) cadastrado(s) com sucesso.")
            else:
                print("\nFalha ao cadastrar o endereço.")
        else:
             print("\nNenhum endereço foi cadastrado.")
    elif opcao == 2:
        print("\n--- PERFIL ---\n")
        print(
            f"Nome: {session['nome']}",
            f"\nCPF: {session['cpf']}",
            f"\nEmail: {session['email']}",
            f"\nTelefone: {session['telefone']}",
            )
        numero_enderecos = len(session["enderecos"])
        if numero_enderecos > 0:
            print(f"Endereço:" if numero_enderecos == 1 else "Endereços:")
            for endereco in session["enderecos"]:
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
                f"\n    Nome: {session['nome']}",
                f"\n    CPF: {session['cpf']}",
                f"\n    Email: {session['email']}",
                f"\n    Telefone: {session['telefone']}")

        print("\nNovos dados (deixe vazio para manter o atual):")
        print("    --------------------------------")
        nome = input("    Nome: ").strip()
        cpf = input("    CPF: ").strip()
        email = input("    Email: ").strip()
        senha = input("    Senha: ").strip()
        telefone = input("    Telefone: ").strip()

        session['nome'] = nome if nome else session['nome']
        session['cpf'] = cpf if cpf else session['cpf']
        session['email'] = email if email else session['email']
        session['telefone'] = telefone if telefone else session['telefone']
        session['senha'] = hashlib.sha256(senha.encode()).hexdigest() if senha else session['senha']

        sucesso = r.setex(f"session:{session['_id']}", 3600, json.dumps(session, default=str))
        if sucesso:
            print("\nDados atualizados com sucesso.")
        else:
            print("\nFalha ao atualizar os dados.")
    elif opcao == 4:
        print("\n--- ATUALIZAR ENDEREÇO ---\n")
        numero_enderecos = len(session["enderecos"])
        if numero_enderecos > 0:
            print(f"Endereço:" if numero_enderecos == 1 else "Endereços:")
            for i, endereco in enumerate(session["enderecos"]):
                numero_enderecos -= 1
                print(f"\nID: {i+1}")
                print(
                    f"\n    {endereco['logradouro']}, {endereco['numero']}{' - ' + endereco['complemento'] if endereco['complemento'] else ''}",
                    f"\n    {endereco['bairro']}",
                    f"\n    {endereco['cidade']} - {endereco['estado']}"
                )
                if numero_enderecos != 0:
                    print(f"    --------------------------------")
        while True:
            id = input("\nDigite o ID do endereço que deseja atualizar(digite '0' para cancelar): ").strip()
            if id == '0':
                break
            if id.isdigit() and 0 < int(id) <= len(session['enderecos']):
                break
            print("ID inválido.")
        if id == '0':
            continue

        endereco = session['enderecos'][int(id) - 1]
        print("\nNovos dados (coloque '-' para manter o atual):")
        logradouro = input("Logradouro: ").strip()
        numero = input("Número: ").strip()
        complemento = input("Complemento: ").strip()
        bairro = input("Bairro: ").strip()
        cidade = input("Cidade: ").strip()
        estado = input("Estado: ").strip()

        dados = {
            "_id": endereco['_id'],
            "logradouro": logradouro if logradouro != '-' else endereco['logradouro'],
            "numero": numero if numero != '-' else endereco['numero'],
            "complemento": complemento if complemento != '-' else endereco['complemento'],
            "bairro": bairro if bairro != '-' else endereco['bairro'],
            "cidade": cidade if cidade != '-' else endereco['cidade'],
            "estado": estado if estado != '-' else endereco['estado']
        }

        session['enderecos'][int(id) - 1] = dados
        sucesso = r.setex(f"session:{session['_id']}", 3600, json.dumps(session, default=str))
        if sucesso:
            print("\nEndereço atualizado com sucesso.")
        else:
            print("\nFalha ao atualizar o endereço.")
    elif opcao == 5:
        print("\n--- DELETAR ENDEREÇO ---\n")
        numero_enderecos = len(session["enderecos"])
        if numero_enderecos > 0:
            print(f"Endereço:" if numero_enderecos == 1 else "Endereços:")
            for i, endereco in enumerate(session["enderecos"]):
                numero_enderecos -= 1
                print(f"\nID: {i+1}")
                print(
                    f"\n    {endereco['logradouro']}, {endereco['numero']}{' - ' + endereco['complemento'] if endereco['complemento'] else ''}",
                    f"\n    {endereco['bairro']}",
                    f"\n    {endereco['cidade']} - {endereco['estado']}"
                )
                if numero_enderecos != 0:
                    print(f"    --------------------------------")
        while True:
            ids = input("\nDigite os IDs dos endereços que deseja deletar (digite '0' para cancelar): ").strip().split()
            if '0' in ids:
                break
            if all(id.isdigit() and 0 < int(id) <= len(session['enderecos']) for id in ids):
                break
            print("ID inválido. Digite apenas números separados por espaço.")
        if '0' in ids:
            continue
        enderecos = [session['enderecos'][int(id) - 1] for id in ids]
        for endereco in enderecos:
            session['enderecos'].remove(endereco)
        sucesso = r.setex(f"session:{session['_id']}", 3600, json.dumps(session, default=str))
        if sucesso:
            print("\nEndereço(s) deletado(s) com sucesso.")
        else:
            print("\nFalha ao deletar o(s) endereço(s).")
    elif opcao == 0:
        r.delete(f"session:{session['_id']}")
        for endereco in session['enderecos']:
            endereco['_id'] = ObjectId(endereco['_id'])
        mydb.cliente.update_one(
            {"_id": ObjectId(session['_id'])},
            {"$set": {
                "nome": session['nome'],
                "cpf": session['cpf'],
                "email": session['email'],
                "telefone": session['telefone'],
                "enderecos": session['enderecos']
            }},
        )
        print("Saindo do sistema...")
        break
    else:
        limpar()