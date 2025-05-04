import datetime

# Obtém a data atual
data_atual = datetime.datetime.now().date()
d_atu = data_atual.strftime("%d/%m/%Y")
# Imprime a data
print(d_atu)