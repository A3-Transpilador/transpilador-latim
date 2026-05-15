# Codigo gerado automaticamente pelo compilador Latim-Python
mensagem = "iniciando sistema de notas..."
print(mensagem)
print("digite seu nome: ")
nome = input()
limite = 3
executando = True
vazio = None
lista_notas = [Literal(valor=7), Literal(valor=8), Literal(valor=10)]
media = (5 + (2 * 3))
print("resultado da conta (esperado 11): ")
print(media)
if (media >= 10):
    print("media excelente!")
else:
    print("media dentro do esperado.")
print("contagem progressiva:")
for contador in range(1, limite):
    print(contador)
print("contagem regressiva:")
while (limite > 0):
    print(limite)
    limite = (limite - 1)
print("teste do-while:")
while True:
    print("executou pelo menos uma vez!")
    executando = False
    if not ((executando == True)):
        break
print("fim do programa, ")
print(nome)
