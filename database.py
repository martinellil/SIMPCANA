"""
database.py - Conexao e operacoes com Oracle (Cap. 6)
"""

try:
    import oracledb
    DISPONIVEL = True
except ImportError:
    DISPONIVEL = False

# Edite conforme seu ambiente Oracle
DB_CONFIG = {
    "user":     "SIMPCANA",
    "password": "simpcana123",
    "dsn":      "localhost/XEPDB1"
}


def conectar():
    if not DISPONIVEL:
        raise RuntimeError("Instale oracledb: pip install oracledb")
    return oracledb.connect(**DB_CONFIG)


def criar_tabelas(con):
    """Cria as tabelas e sequence caso nao existam."""
    cur = con.cursor()

    cur.execute("""
        BEGIN
            EXECUTE IMMEDIATE '
                CREATE TABLE SIMPCANA_TALHOES (
                    CODIGO        VARCHAR2(10) PRIMARY KEY,
                    NOME          VARCHAR2(100) NOT NULL,
                    AREA          NUMBER(10,2) NOT NULL,
                    VARIEDADE     VARCHAR2(50),
                    TIPO_COLHEITA VARCHAR2(20) NOT NULL
                )';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -955 THEN RAISE; END IF;
        END;
    """)

    cur.execute("""
        BEGIN
            EXECUTE IMMEDIATE '
                CREATE TABLE SIMPCANA_COLHEITAS (
                    ID                  NUMBER PRIMARY KEY,
                    CODIGO_TALHAO       VARCHAR2(10) REFERENCES SIMPCANA_TALHOES(CODIGO),
                    DATA_COLHEITA       DATE NOT NULL,
                    PRODUCAO_BRUTA      NUMBER(12,2) NOT NULL,
                    PERDA_PERCENTUAL    NUMBER(5,2) NOT NULL,
                    PRODUCAO_LIQUIDA    NUMBER(12,2) NOT NULL,
                    CLASSIFICACAO_PERDA VARCHAR2(20)
                )';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -955 THEN RAISE; END IF;
        END;
    """)

    cur.execute("""
        BEGIN
            EXECUTE IMMEDIATE 'CREATE SEQUENCE SIMPCANA_SEQ START WITH 1 INCREMENT BY 1';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -955 THEN RAISE; END IF;
        END;
    """)

    con.commit()
    cur.close()


def inserir_talhao(con, codigo, t):
    cur = con.cursor()
    cur.execute(
        "INSERT INTO SIMPCANA_TALHOES (CODIGO,NOME,AREA,VARIEDADE,TIPO_COLHEITA) "
        "VALUES (:1,:2,:3,:4,:5)",
        (codigo, t["nome"], t["area"], t["variedade"], t["tipo_colheita"])
    )
    con.commit()
    cur.close()


def inserir_colheita(con, c):
    from datetime import datetime
    cur = con.cursor()
    data = datetime.strptime(c["data"], "%d/%m/%Y")
    cur.execute(
        "INSERT INTO SIMPCANA_COLHEITAS "
        "(ID,CODIGO_TALHAO,DATA_COLHEITA,PRODUCAO_BRUTA,PERDA_PERCENTUAL,PRODUCAO_LIQUIDA,CLASSIFICACAO_PERDA) "
        "VALUES (SIMPCANA_SEQ.NEXTVAL,:1,:2,:3,:4,:5,:6)",
        (c["id_talhao"], data, c["producao_bruta"],
         c["perda_percentual"], c["producao_liquida"], c["classificacao_perda"])
    )
    con.commit()
    cur.close()


def buscar_talhoes(con):
    cur = con.cursor()
    cur.execute("SELECT CODIGO,NOME,AREA,VARIEDADE,TIPO_COLHEITA FROM SIMPCANA_TALHOES")
    resultado = {r[0]: {"nome": r[1], "area": float(r[2]), "variedade": r[3], "tipo_colheita": r[4]}
                 for r in cur.fetchall()}
    cur.close()
    return resultado


def buscar_colheitas(con):
    cur = con.cursor()
    cur.execute(
        "SELECT ID,CODIGO_TALHAO,TO_CHAR(DATA_COLHEITA,'DD/MM/YYYY'),"
        "PRODUCAO_BRUTA,PERDA_PERCENTUAL,PRODUCAO_LIQUIDA,CLASSIFICACAO_PERDA "
        "FROM SIMPCANA_COLHEITAS ORDER BY DATA_COLHEITA"
    )
    resultado = [
        {"id": int(r[0]), "id_talhao": r[1], "data": r[2],
         "producao_bruta": float(r[3]), "perda_percentual": float(r[4]),
         "producao_liquida": float(r[5]), "classificacao_perda": r[6] or ""}
        for r in cur.fetchall()
    ]
    cur.close()
    return resultado


def menu_oracle(talhoes, colheitas, preco_tonelada):
    """Menu de operacoes Oracle chamado a partir do main."""
    print("\n  [1] Conectar e criar estrutura")
    print("  [2] Enviar dados para Oracle")
    print("  [3] Importar dados do Oracle")
    print("  [0] Voltar")
    op = input("  >> ").strip()

    if op not in ("1", "2", "3"):
        return

    try:
        con = conectar()
    except Exception as e:
        print(f"  Erro de conexao: {e}")
        return

    if op == "1":
        criar_tabelas(con)
        print("  Tabelas criadas/verificadas com sucesso!")

    elif op == "2":
        criar_tabelas(con)
        talhoes_bd = buscar_talhoes(con)
        colheitas_bd_ids = {c["id"] for c in buscar_colheitas(con)}
        t_ins = c_ins = 0
        for cod, t in talhoes.items():
            if cod not in talhoes_bd:
                inserir_talhao(con, cod, t)
                t_ins += 1
        for c in colheitas:
            if c["id"] not in colheitas_bd_ids:
                inserir_colheita(con, c)
                c_ins += 1
        print(f"  Enviados: {t_ins} talhao(es) e {c_ins} colheita(s).")

    elif op == "3":
        t_bd = buscar_talhoes(con)
        c_bd = buscar_colheitas(con)
        talhoes.clear()
        talhoes.update(t_bd)
        colheitas.clear()
        colheitas.extend(c_bd)
        print(f"  Importados: {len(talhoes)} talhao(es), {len(colheitas)} colheita(s).")

    con.close()
