# Codigo gerado automaticamente pelo compilador Latim-Python
print((lambda x: round(x, 2) if isinstance(x, float) else x)("digite o primeiro numero: "), end='', flush=True)
try:
    x = int(input())
except ValueError:
    print(f'\n[Erro de Execucao] O valor digitado para "x" nao é um inteiro valido.')
    exit(1)
print((lambda x: round(x, 2) if isinstance(x, float) else x)("digite o segundo numero: "), end='', flush=True)
try:
    y = int(input())
except ValueError:
    print(f'\n[Erro de Execucao] O valor digitado para "y" nao é um inteiro valido.')
    exit(1)
soma = (x + y)
print((lambda x: round(x, 2) if isinstance(x, float) else x)("a soma é: "))
print((lambda x: round(x, 2) if isinstance(x, float) else x)(soma))
