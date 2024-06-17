# TestTask Grupo AG Capital

- O banco de dados é real e está hospeado no render.com, é possível verificar os dados de login e acesso ao banco no `settings.py`. 
- O SU do backend é `root` e a senha é `wasder`. 
- O backend utiliza Django com GraphQL. 
- Foram criados testes unitários para os apps `accounts`, `cleitons`, `activities` e `documents`.
- Cleiton é um trocadilho para Client.
- Os testes unitários realizam todas as funções CRUD.
- O backend permite que apenas o SU crie contas e adicione cleitons.
- O backend realiza verificações de autenticação para que apenas o dono do projeto, ou um SU ou staff, consiga realizar mudanças no seu respectivo projeto.

## Instruções para executar os testes e o servidor
1. Clonar este repositório. 
2. Entrar na pasta do repositório clonado. 
3. Criar um venv com o nome `venv` (para poder usar o activate_venv.bat). 
4. Ativar o venv. 
5. Usar `pip install -r requirements.txt`. 
6. Rodar os testes `pytest -vvv` na pasta raiz do projeto. 
7. Utilize `py manage.py runserver` para executar o servidor localmente. 

## Diagrama de classes
![diagrama_de_classes](https://github.com/DevArqSangoi/das-agcapital/assets/125471877/0942ff3c-7422-4491-ab5e-9fe93437b5da)
