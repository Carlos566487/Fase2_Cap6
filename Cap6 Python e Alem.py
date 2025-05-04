# Monitoramento de Colheita em Tempo Real
#
# Este aplicativo tem como objetivo reduzir perdas significativas durante o processo de
# colheita, especialmente na cultura da cana-de-açúcar, por meio do uso de tecnologias
# modernas de monitoramento.
#
# A solução integra sensores e dispositivos GPS instalados nas colhedoras para:
# - Acompanhar em tempo real a área colhida;
# - Estimar as perdas por hectare durante a operação;
# - Emitir alertas ao operador em casos de falhas mecânicas ou perdas acima dos níveis aceitáveis;
# - Gerar relatórios analíticos por fazenda, máquina e operador, facilitando a tomada de decisão.
#
# Tecnologias utilizadas: IoT (Internet das Coisas), GPS embarcado, dashboards analíticos
# e integração com banco de dados Oracle.

import json
import cx_Oracle
import datetime

data_atual = datetime.datetime.now().date()
d_atu = data_atual.strftime("%d/%m/%Y")

# Inicializa o cliente Oracle
cx_Oracle.init_oracle_client(lib_dir="C:\\instantclient_23_7")

# Função para calcular perdas
def calcular_perda(area_colhida_ha: float, total_produzido_t: float, estimativa_t_ha: float) -> float:
    producao_esperada = estimativa_t_ha * area_colhida_ha
    perda = producao_esperada - total_produzido_t
    return round(perda, 2)

# Procedimento para salvar em arquivo de texto
def salvar_txt(dados: dict, nome_arquivo: str):
    with open(nome_arquivo, 'a') as f:
        for k, v in dados.items():
            f.write(f"{k}: {v}\n")
        f.write("-" * 30 + "\n")

# Procedimento para salvar em arquivo JSON
def salvar_json(dados: dict, nome_arquivo: str):
    try:
        with open(nome_arquivo, 'r') as f:
            registros = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        registros = []

    registros.append(dados)

    with open(nome_arquivo, 'w') as f:
        json.dump(registros, f, indent=4)

# Entrada de dados com estrutura de dados (lista, tupla, dicionário)
def entrada_dados():
    maquinas = [
        ("Maq001", "Colhedora-Auto1"),
        ("Maq002", "Colhedora-Auto2")
    ]

    registros = []  # Lista de dicionários (tabela em memória)

    for id_maquina, nome in maquinas:
        print(f"\nRegistrando para máquina: {nome}")

        area = float(input("Área colhida (ha): "))
        produzido = float(input("Total produzido (toneladas): "))
        estimativa = float(input("Estimativa (t/ha): "))

        perda = calcular_perda(area, produzido, estimativa)

        registro = {
            "id_maquina": id_maquina,
            "nome_maquina": nome,
            "area_colhida_ha": area,
            "total_produzido_t": produzido,
            "estimativa_t_ha": estimativa,
            "perda_estimativa_t": perda,
            "data_colheita": d_atu
        }

        registros.append(registro)

        salvar_txt(registro, "colheita_log.txt")
        salvar_json(registro, "colheita_registros.json")

    return registros

# Conexão com banco Oracle (insere os dados)
def inserir_banco_oracle(registros):
    dsn = cx_Oracle.makedsn("localhost", 1521, service_name="XEPDB1")
    conn = cx_Oracle.connect(user="EDUBD", password="edu1", dsn=dsn)

    cursor = conn.cursor()

    for r in registros:
        cursor.execute(
            """
            INSERT INTO COLHEITA (
                ID_MAQUINA,
                NOME_MAQUINA,
                AREA_HA,
                PRODUZIDO_T,
                ESTIMATIVA_T_HA,
                PERDA_T,
                DATA_COLHEITA
            ) VALUES (
                :1, :2, :3, :4, :5, :6, :7
            )
            """,
            (
                r["id_maquina"],
                r["nome_maquina"],
                r["area_colhida_ha"],
                r["total_produzido_t"],
                r["estimativa_t_ha"],
                r["perda_estimativa_t"],
                r["data_colheita"]
            )
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Dados inseridos no banco Oracle com sucesso!")

# Programa principal
def main():
    print("=== Monitoramento de Colheita ===")
    registros = entrada_dados()
    inserir_banco_oracle(registros)

if __name__ == "__main__":
    main()
