"""
SIMPCANA - Sistema de Monitoramento de Perdas na Colheita de Cana-de-Acucar
Gestao do Agronegocio em Python - Capitulos 3 ao 6
"""

import json
import os
from datetime import datetime

# ===========================================================================
# CAP. 4 - ESTRUTURAS DE DADOS
# ===========================================================================

# Tuplas: dados de referencia imutaveis
VARIEDADES = ("RB867515", "RB92579", "RB966928", "CTC9001", "Outra")
TIPOS      = ("manual", "mecanica")
LIMITES    = {"manual": 5.0, "mecanica": 15.0}

# Dicionario: cadastro de talhoes  {codigo: {nome, area, variedade, tipo_colheita}}
talhoes = {}

# Lista: registro de colheitas
colheitas = []

# Float configuravel pelo usuario
preco_tonelada = 150.0


# ===========================================================================
# CAP. 3 - FUNCOES E PROCEDIMENTOS COM PASSAGEM DE PARAMETROS
# ===========================================================================

def calcular_producao_liquida(producao_bruta, perda_percentual):
    """Retorna a producao descontando o percentual de perda."""
    return round(producao_bruta * (1 - perda_percentual / 100), 2)


def calcular_receita(producao_liquida, preco):
    """Estima a receita com base na producao liquida e preco por tonelada."""
    return round(producao_liquida * preco, 2)


def calcular_produtividade(producao_liquida, area_hectares):
    """Calcula toneladas por hectare (t/ha)."""
    if area_hectares <= 0:
        return 0.0
    return round(producao_liquida / area_hectares, 2)


def classificar_perda(tipo_colheita, perda_percentual):
    """Classifica o nivel de perda como ACEITAVEL, ALERTA ou CRITICO (ref. SOCICANA)."""
    limite = LIMITES[tipo_colheita]
    if perda_percentual <= limite * 0.5:
        return "ACEITAVEL"
    elif perda_percentual <= limite:
        return "ALERTA"
    return "CRITICO"


def gerar_codigo_talhao():
    """Gera proximo codigo sequencial: T001, T002..."""
    nums = [int(k[1:]) for k in talhoes if k.startswith("T") and k[1:].isdigit()]
    return f"T{(max(nums) + 1 if nums else 1):03d}"


def gerar_id_colheita():
    """Gera proximo ID inteiro para colheita."""
    return max((c["id"] for c in colheitas), default=0) + 1


# --- Procedimentos de entrada validada ----------------------------------------

def ler_float(prompt, minimo=0.0):
    """Solicita float ao usuario, com reentrada em caso de erro."""
    while True:
        try:
            valor = float(input(prompt).strip().replace(",", "."))
            if valor >= minimo:
                return valor
            print(f"  Valor deve ser >= {minimo}.")
        except ValueError:
            print("  Digite um numero valido.")


def ler_inteiro(prompt, minimo=0, maximo=99):
    """Solicita inteiro ao usuario, com reentrada em caso de erro."""
    while True:
        try:
            valor = int(input(prompt).strip())
            if minimo <= valor <= maximo:
                return valor
            print(f"  Digite um numero entre {minimo} e {maximo}.")
        except ValueError:
            print("  Digite um numero inteiro valido.")


def ler_opcao(prompt, opcoes):
    """Valida se entrada esta entre as opcoes validas (tupla). Retorna opcao original."""
    mapa = {o.lower(): o for o in opcoes}
    while True:
        entrada = input(prompt).strip().lower()
        if entrada in mapa:
            return mapa[entrada]
        print(f"  Opcoes validas: {', '.join(opcoes)}")


def ler_data(prompt):
    """Valida e retorna data no formato DD/MM/AAAA."""
    while True:
        try:
            return datetime.strptime(input(prompt).strip(), "%d/%m/%Y").strftime("%d/%m/%Y")
        except ValueError:
            print("  Use o formato DD/MM/AAAA.")


# ===========================================================================
# CAP. 4 - TABELA DE MEMORIA (lista de listas)
# ===========================================================================

def montar_tabela():
    """
    Retorna tabela de memoria (lista de listas) consolidada por talhao.
    Primeira linha = cabecalho.
    """
    cabecalho = ["Codigo", "Talhao", "Area(ha)", "Colheitas",
                 "Prod.Bruta(t)", "Perda(%)", "Prod.Liq.(t)", "Receita(R$)"]
    tabela = [cabecalho]

    for cod, t in talhoes.items():
        cols = [c for c in colheitas if c["id_talhao"] == cod]
        if not cols:
            tabela.append([cod, t["nome"], t["area"], 0, 0.0, 0.0, 0.0, 0.0])
            continue
        pb  = sum(c["producao_bruta"]  for c in cols)
        pl  = sum(c["producao_liquida"] for c in cols)
        pm  = sum(c["perda_percentual"] for c in cols) / len(cols)
        rec = calcular_receita(pl, preco_tonelada)
        tabela.append([cod, t["nome"], t["area"], len(cols),
                       round(pb, 2), round(pm, 2), round(pl, 2), rec])
    return tabela


def imprimir_tabela():
    """Imprime a tabela de memoria no terminal de forma legivel."""
    tabela = montar_tabela()
    sep    = "-" * 90
    print("\n" + sep)
    for i, linha in enumerate(tabela):
        print("  ".join(str(v).ljust(13) for v in linha))
        if i == 0:
            print(sep)
    print(sep)


# ===========================================================================
# CAP. 5 - MANIPULACAO DE ARQUIVOS
# ===========================================================================

def salvar_json():
    """Persiste talhoes, colheitas e preco em arquivo JSON."""
    os.makedirs("dados", exist_ok=True)
    with open("dados/dados.json", "w", encoding="utf-8") as f:
        json.dump(
            {"preco": preco_tonelada, "talhoes": talhoes, "colheitas": colheitas},
            f, ensure_ascii=False, indent=2
        )
    print("  Dados salvos em dados/dados.json")


def carregar_json():
    """Carrega dados do arquivo JSON para as estruturas em memoria."""
    global talhoes, colheitas, preco_tonelada
    if not os.path.exists("dados/dados.json"):
        print("  Nenhum arquivo encontrado.")
        return
    with open("dados/dados.json", "r", encoding="utf-8") as f:
        d = json.load(f)
    talhoes        = d.get("talhoes", {})
    colheitas      = d.get("colheitas", [])
    preco_tonelada = float(d.get("preco", 150.0))
    for c in colheitas:
        c["id"] = int(c["id"])
    print(f"  Carregados: {len(talhoes)} talhao(es), {len(colheitas)} colheita(s).")


def exportar_txt():
    """Exporta relatorio formatado em arquivo de texto."""
    os.makedirs("dados", exist_ok=True)
    tabela = montar_tabela()
    total_bruta = sum(c["producao_bruta"]  for c in colheitas)
    total_liq   = sum(c["producao_liquida"] for c in colheitas)
    perda_geral = ((total_bruta - total_liq) / total_bruta * 100) if total_bruta else 0

    with open("dados/relatorio.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  SIMPCANA - Relatorio de Colheita de Cana-de-Acucar\n")
        f.write(f"  Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"  Talhoes: {len(talhoes)} | Colheitas: {len(colheitas)}\n")
        f.write(f"  Producao bruta total : {total_bruta:,.2f} t\n")
        f.write(f"  Producao liquida total: {total_liq:,.2f} t\n")
        f.write(f"  Perda media geral    : {perda_geral:.2f}%\n")
        f.write(f"  Receita estimada total: R$ {calcular_receita(total_liq, preco_tonelada):,.2f}\n\n")
        f.write("-" * 80 + "\n")
        for i, linha in enumerate(tabela):
            f.write("  ".join(str(v).ljust(13) for v in linha) + "\n")
            if i == 0:
                f.write("-" * 80 + "\n")
        f.write("\n")

        # Detalhamento por talhao
        f.write("=" * 80 + "\n  DETALHAMENTO POR TALHAO\n" + "=" * 80 + "\n")
        for cod, t in talhoes.items():
            cols = sorted([c for c in colheitas if c["id_talhao"] == cod], key=lambda x: x["data"])
            f.write(f"\n[{cod}] {t['nome']} | {t['area']} ha | {t['variedade']} | {t['tipo_colheita']}\n")
            for c in cols:
                f.write(
                    f"  {c['data']}  Bruta: {c['producao_bruta']:.1f}t  "
                    f"Perda: {c['perda_percentual']}%  "
                    f"Liquida: {c['producao_liquida']:.1f}t  "
                    f"Status: {c['classificacao_perda']}\n"
                )

    print("  Relatorio exportado em dados/relatorio.txt")


# ===========================================================================
# MENU E FLUXO PRINCIPAL
# ===========================================================================

def cadastrar_talhao():
    codigo = gerar_codigo_talhao()
    print(f"\n  Codigo gerado: {codigo}")
    nome = input("  Nome do talhao: ").strip()
    if not nome:
        print("  Nome invalido.")
        return
    area = ler_float("  Area (ha): ", 0.01)
    print(f"  Variedades: {', '.join(VARIEDADES)}")
    variedade = ler_opcao("  Variedade: ", VARIEDADES)
    print(f"  Tipos: {', '.join(TIPOS)}")
    tipo = ler_opcao("  Tipo de colheita: ", TIPOS)

    talhoes[codigo] = {"nome": nome, "area": area, "variedade": variedade, "tipo_colheita": tipo}
    print(f"  Talhao {codigo} cadastrado com sucesso!")


def registrar_colheita():
    if not talhoes:
        print("  Nenhum talhao cadastrado.")
        return

    print("\n  Talhoes disponíveis:")
    for cod, t in talhoes.items():
        print(f"  {cod} - {t['nome']} [{t['tipo_colheita']}]")

    codigo = input("  Codigo do talhao: ").strip().upper()
    if codigo not in talhoes:
        print("  Talhao nao encontrado.")
        return

    t     = talhoes[codigo]
    data  = ler_data("  Data (DD/MM/AAAA): ")
    bruta = ler_float("  Producao bruta (t): ", 0.01)
    perda = ler_float(f"  Perda % [limite {LIMITES[t['tipo_colheita']]}%]: ", 0)
    if perda > 100:
        print("  Perda nao pode ser > 100%.")
        return

    liq      = calcular_producao_liquida(bruta, perda)
    classif  = classificar_perda(t["tipo_colheita"], perda)
    produt   = calcular_produtividade(liq, t["area"])
    rec      = calcular_receita(liq, preco_tonelada)

    colheitas.append({
        "id": gerar_id_colheita(), "id_talhao": codigo, "data": data,
        "producao_bruta": bruta, "perda_percentual": perda,
        "producao_liquida": liq, "classificacao_perda": classif
    })

    print(f"\n  Producao liquida : {liq} t")
    print(f"  Produtividade    : {produt} t/ha")
    print(f"  Receita estimada : R$ {rec:,.2f}")
    print(f"  Classificacao    : {classif}")
    print("  Colheita registrada com sucesso!")


def listar_talhoes():
    if not talhoes:
        print("  Nenhum talhao cadastrado.")
        return
    print(f"\n  {'Cod':<8} {'Nome':<22} {'Area':>8} {'Variedade':<12} {'Tipo':<10} {'Colheitas':>9}")
    print("  " + "-" * 72)
    for cod, t in talhoes.items():
        n = sum(1 for c in colheitas if c["id_talhao"] == cod)
        print(f"  {cod:<8} {t['nome']:<22} {t['area']:>8.2f} {t['variedade']:<12} {t['tipo_colheita']:<10} {n:>9}")


def listar_colheitas():
    if not colheitas:
        print("  Nenhuma colheita registrada.")
        return
    print(f"\n  {'ID':>4} {'Talhao':<8} {'Data':<12} {'Bruta':>10} {'Perda%':>7} {'Liquida':>10} {'Status'}")
    print("  " + "-" * 65)
    for c in sorted(colheitas, key=lambda x: x["data"]):
        print(f"  {c['id']:>4} {c['id_talhao']:<8} {c['data']:<12} "
              f"{c['producao_bruta']:>9.1f}t {c['perda_percentual']:>6.1f}% "
              f"{c['producao_liquida']:>9.1f}t  {c['classificacao_perda']}")


def main():
    global preco_tonelada

    # Tenta carregar dados salvos automaticamente
    try:
        carregar_json()
    except Exception:
        pass

    while True:
        print("\n" + "=" * 40)
        print("  SIMPCANA - Cana-de-Acucar")
        print(f"  Talhoes: {len(talhoes)} | Colheitas: {len(colheitas)} | R$/t: {preco_tonelada:.2f}")
        print("=" * 40)
        print("  [1] Cadastrar talhao")
        print("  [2] Listar talhoes")
        print("  [3] Registrar colheita")
        print("  [4] Listar colheitas")
        print("  [5] Tabela consolidada")
        print("  [6] Exportar relatorio (.txt)")
        print("  [7] Salvar dados (.json)")
        print("  [8] Carregar dados (.json)")
        print("  [9] Configurar preco/tonelada")
        print("  [10] Conectar / Sincronizar Oracle")
        print("  [0] Sair")
        op = input("  >> ").strip()

        if op == "1":
            cadastrar_talhao()
        elif op == "2":
            listar_talhoes()
        elif op == "3":
            registrar_colheita()
        elif op == "4":
            listar_colheitas()
        elif op == "5":
            imprimir_tabela()
        elif op == "6":
            exportar_txt()
        elif op == "7":
            salvar_json()
        elif op == "8":
            carregar_json()
        elif op == "9":
            preco_tonelada = ler_float("  Novo preco por tonelada (R$): ", 0.01)
            print(f"  Preco atualizado para R$ {preco_tonelada:.2f}/t")
        elif op == "10":
            import database as db
            db.menu_oracle(talhoes, colheitas, preco_tonelada)
        elif op == "0":
            salvar = input("  Salvar antes de sair? (s/n): ").strip().lower()
            if salvar == "s":
                salvar_json()
            print("  Ate logo!")
            break
        else:
            print("  Opcao invalida.")

        input("\n  Pressione ENTER para continuar...")


if __name__ == "__main__":
    main()
