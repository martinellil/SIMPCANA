# SIMPCANA
### Sistema de Monitoramento de Perdas na Colheita de Cana-de-Açúcar

> Projeto da disciplina **Gestão do Agronegócio em Python** — Capítulos 3 ao 6  

---

## O problema

O Brasil é o maior produtor mundial de cana-de-açúcar. Mesmo assim, enfrenta perdas significativas durante a **colheita mecânica**, que chegam a **15% da produção bruta**, segundo avaliação da SOCICANA. A colheita manual, em comparação, apresenta perdas de apenas **5%**.

Considerando a área plantada em São Paulo (~3 milhões de hectares), esse percentual representa um prejuízo anual estimado em **R$ 20 milhões** para o setor — apenas nesse estado.

O **SIMPCANA** oferece ao produtor rural uma ferramenta para registrar, monitorar e analisar as perdas de cada talhão, com classificação automática de risco, estimativa de receita e persistência dos dados.

---

## Funcionalidades

| Opção | Funcionalidade |
|-------|----------------|
| 1 | Cadastrar talhão (código automático, variedade, tipo de colheita) |
| 2 | Listar talhões cadastrados |
| 3 | Registrar colheita com cálculo automático de perdas e receita |
| 4 | Listar colheitas com classificação de risco |
| 5 | Tabela consolidada por talhão (tabela de memória) |
| 6 | Exportar relatório em arquivo `.txt` |
| 7 | Salvar dados em arquivo `.json` |
| 8 | Carregar dados do arquivo `.json` |
| 9 | Configurar preço por tonelada |
| 10 | Conectar ao Oracle e sincronizar dados |

---

## Estrutura do projeto

```
simpcana/
├── main.py          # Código principal: funções, estruturas, arquivos e menu
├── database.py      # Conexão e operações com banco de dados Oracle
├── requirements.txt # Dependências Python
├── dados/           # Criado automaticamente ao salvar
│   ├── dados.json       # Persistência dos dados em JSON
│   └── relatorio.txt    # Relatório exportado em texto
└── README.md
```

---

## Conteúdo técnico — Capítulos 3 ao 6

### Capítulo 3 — Subalgoritmos com passagem de parâmetros (`main.py`)

| Função | Descrição |
|--------|-----------|
| `calcular_producao_liquida(producao_bruta, perda_percentual)` | Desconta a perda percentual da produção bruta |
| `calcular_receita(producao_liquida, preco)` | Estima a receita com base na produção líquida |
| `calcular_produtividade(producao_liquida, area_hectares)` | Calcula toneladas por hectare (t/ha) |
| `classificar_perda(tipo_colheita, perda_percentual)` | Classifica a perda como ACEITAVEL, ALERTA ou CRITICO |
| `gerar_codigo_talhao()` | Gera o próximo código sequencial (T001, T002…) |
| `gerar_id_colheita()` | Gera o próximo ID inteiro para colheita |
| `ler_float(prompt, minimo)` | Valida entrada numérica com reentrada em caso de erro |
| `ler_opcao(prompt, opcoes)` | Valida se a entrada pertence a uma tupla de opções |
| `ler_data(prompt)` | Valida data no formato DD/MM/AAAA |
| `montar_tabela()` | Monta tabela de memória consolidada por talhão |

---

### Capítulo 4 — Estruturas de dados (`main.py`)

**Dicionário** — cadastro de talhões, onde a chave é o código e o valor é um dicionário de atributos:
```python
talhoes = {
    "T001": {"nome": "Talhão Norte", "area": 50.5, "variedade": "RB867515", "tipo_colheita": "mecanica"}
}
```

**Lista** — registro de colheitas, cada elemento é um dicionário:
```python
colheitas = [
    {"id": 1, "id_talhao": "T001", "data": "10/06/2024", "producao_bruta": 5000.0, ...}
]
```

**Tuplas** — dados de referência imutáveis:
```python
VARIEDADES = ("RB867515", "RB92579", "RB966928", "CTC9001", "Outra")
TIPOS      = ("manual", "mecanica")
```

**Tabela de memória** — lista de listas retornada por `montar_tabela()`, onde a primeira linha é o cabeçalho:
```python
[
  ["Codigo", "Talhao", "Area(ha)", "Colheitas", "Prod.Bruta(t)", "Perda(%)", "Prod.Liq.(t)", "Receita(R$)"],
  ["T001", "Talhão Norte", 50.5, 3, 15000.0, 12.3, 13155.0, 1973250.0],
  ["T002", "Talhão Sul",   30.0, 1,  3000.0,  4.1,  2877.0,   431550.0],
]
```

---

### Capítulo 5 — Manipulação de arquivos (`main.py`)

**JSON** — `salvar_json()` usa `json.dump()` para persistir o estado completo; `carregar_json()` usa `json.load()` para restaurar:
```json
{
  "preco": 150.0,
  "talhoes": { "T001": { ... } },
  "colheitas": [ { ... } ]
}
```

**Texto** — `exportar_txt()` grava um relatório formatado com cabeçalho, totalizadores, tabela consolidada e detalhamento por talhão em `dados/relatorio.txt`.

---

### Capítulo 6 — Conexão com banco de dados Oracle (`database.py`)

- Conexão via `oracledb.connect()` com configuração em `DB_CONFIG`
- Criação automática das tabelas `SIMPCANA_TALHOES` e `SIMPCANA_COLHEITAS` e da sequence `SIMPCANA_SEQ`
- CRUD: `inserir_talhao()`, `inserir_colheita()`, `buscar_talhoes()`, `buscar_colheitas()`
- Sincronização: envio dos dados locais para o Oracle e importação do Oracle para a memória

```sql
CREATE TABLE SIMPCANA_TALHOES (
    CODIGO        VARCHAR2(10) PRIMARY KEY,
    NOME          VARCHAR2(100) NOT NULL,
    AREA          NUMBER(10,2)  NOT NULL,
    VARIEDADE     VARCHAR2(50),
    TIPO_COLHEITA VARCHAR2(20)  NOT NULL
);

CREATE TABLE SIMPCANA_COLHEITAS (
    ID                  NUMBER PRIMARY KEY,
    CODIGO_TALHAO       VARCHAR2(10) REFERENCES SIMPCANA_TALHOES(CODIGO),
    DATA_COLHEITA       DATE         NOT NULL,
    PRODUCAO_BRUTA      NUMBER(12,2) NOT NULL,
    PERDA_PERCENTUAL    NUMBER(5,2)  NOT NULL,
    PRODUCAO_LIQUIDA    NUMBER(12,2) NOT NULL,
    CLASSIFICACAO_PERDA VARCHAR2(20)
);
```

---

## Como executar

**1. Clone o repositório**
```bash
git clone https://github.com/SEU_USUARIO/simpcana.git
cd simpcana
```

**2. Instale as dependências**
```bash
pip install -r requirements.txt
```
> `oracledb` só é necessário para as funções Oracle. O restante funciona sem ele.

**3. Configure o Oracle** (opcional — edite `database.py`):
```python
DB_CONFIG = {
    "user":     "SIMPCANA",
    "password": "simpcana123",
    "dsn":      "localhost/XEPDB1"
}
```

Crie o usuário no Oracle XE:
```sql
CREATE USER simpcana IDENTIFIED BY simpcana123;
GRANT CONNECT, RESOURCE, UNLIMITED TABLESPACE TO simpcana;
```

**4. Execute**
```bash
python main.py
```
O sistema carrega os dados salvos automaticamente ao iniciar e oferece salvar ao sair.

---

## Classificação de perdas (referência SOCICANA)

| Tipo de colheita | ACEITAVEL | ALERTA | CRITICO |
|------------------|-----------|--------|---------|
| Manual           | até 2,5%  | até 5% | > 5%   |
| Mecânica         | até 7,5%  | até 15%| > 15%  |

---

## Referências

- SOCICANA — Associação dos Fornecedores de Cana de Guariba
- EMBRAPA — Agricultura Digital: pesquisa, desenvolvimento e inovação nas cadeias produtivas (2020)
- Blog CHB Agro — Perdas na colheita de cana: como reduzi-las
- TOTVS — O que é agronegócio?
- AEVO Blog — O que é Agrotech?
