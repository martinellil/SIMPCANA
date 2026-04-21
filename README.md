# FIAP - Faculdade de Informática e Administração Paulista

<a href="https://www.fiap.com.br/">
  <img src="https://raw.githubusercontent.com/agodoi/templateFiapVfinal/main/assets/logo-fiap.png" alt="FIAP" width="200"/>
</a>

&nbsp;

# SIMPCANA — Sistema de Monitoramento de Perdas na Colheita de Cana-de-Açúcar

## Gestão do Agronegócio em Python

## Integrantes:
- Leonardo Martinelli Dietrich — RM571605

---

## Descrição

O SIMPCANA é um sistema em Python para monitorar as perdas na colheita de cana-de-açúcar. A ideia veio de um dado real: a colheita mecânica gera perdas de até 15% da produção, enquanto a manual fica em torno de 5%. Essa diferença representa um prejuízo enorme para o produtor — só no estado de São Paulo, a SOCICANA estima R$ 20 milhões por ano.

Com o sistema, o produtor consegue cadastrar seus talhões, registrar cada colheita, ver automaticamente quanto perdeu e qual a receita estimada, além de classificar se a perda está em nível aceitável, alerta ou crítico. Os dados ficam salvos em JSON e também podem ser enviados para um banco Oracle. O projeto usa os conteúdos dos capítulos 3 ao 6: funções com passagem de parâmetros, listas, tuplas, dicionários, tabela de memória, arquivos JSON e texto, e conexão com Oracle.

---

## Estrutura de pastas

```
SIMPCANA/
├── main.py          → menu, funções, estruturas de dados e manipulação de arquivos
├── database.py      → conexão e operações com o banco Oracle
├── requirements.txt → dependências do projeto
├── dados/           → criado automaticamente ao salvar
│   ├── dados.json
│   └── relatorio.txt
└── README.md
```

---

## Como executar o código

**Requisitos:**
- Python 3.10+
- `oracledb` (só necessário se for usar o Oracle)

**Passos:**

1. Clone o repositório:
```bash
git clone https://github.com/martinelli1/SIMPCANA.git
cd SIMPCANA
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute:
```bash
python main.py
```

O sistema já carrega os dados salvos automaticamente na inicialização. Para usar o Oracle, edite o `DB_CONFIG` no `database.py` com suas credenciais e acesse a opção 10 do menu.

---

## O que foi usado de cada capítulo

**Cap. 3 – Funções e procedimentos com passagem de parâmetros**
Todas as funções estão no `main.py`: `calcular_producao_liquida()`, `calcular_receita()`, `calcular_produtividade()`, `classificar_perda()`, `gerar_codigo_talhao()`, entre outras. Todas recebem parâmetros e retornam valores.

**Cap. 4 – Estruturas de dados**
- Dicionário: `talhoes` guarda os talhões com o código como chave
- Lista: `colheitas` guarda os registros de cada colheita
- Tuplas: `VARIEDADES` e `TIPOS` são dados fixos de referência
- Tabela de memória: a função `montar_tabela()` retorna uma lista de listas com cabeçalho, consolidando os dados por talhão

**Cap. 5 – Manipulação de arquivos**
- `salvar_json()` e `carregar_json()` salvam e restauram todos os dados em arquivo `.json`
- `exportar_txt()` gera um relatório formatado em arquivo `.txt`

**Cap. 6 – Banco de dados Oracle**
- `database.py` faz a conexão via `oracledb`, cria as tabelas automaticamente se não existirem, e tem funções de INSERT e SELECT para talhões e colheitas

---

## Histórico de lançamentos

* 1.0.0 - 2024
  * Versão inicial com todas as funcionalidades

---

## Licença

[![CC BY 4.0](https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1)](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1)
[![BY](https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1)](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1)

[MODELO GIT FIAP](https://github.com/agodoi/template) por [Fiap](https://fiap.com.br) está licenciado sobre [Attribution 4.0 International](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1).
