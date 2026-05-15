# Transpilador Latim-Python
Módulo de Lexer e Parser.

## Arquitetura do Sistema
O transpilador segue as fases clássicas de um compilador:
1.  **Análise Léxica (Lexer):** Implementada via biblioteca **Lark**, responsável por transformar o texto em tokens.
2.  **Análise Sintática (Parser):** Define as regras gramaticais e gera a Árvore de Sintaxe Abstrata (AST).
3.  **Análise Semântica:** Valida a tabela de símbolos e a compatibilidade de tipos de dados.
4.  **Geração de Código:** Traduz a AST para código Python respeitando a indentação por blocos.

| Instrução Latim | Equivalente Python | Descrição / Função |
| :--- | :--- | :--- |
| `principium` | (Início do Arquivo) | Delimitador de início do programa. |
| `finis` | (Fim do Arquivo) | Delimitador de encerramento do programa. |
| `numerus` | `int` | Tipo de dado para números inteiros. |
| `decimalis` | `float` | Tipo de dado para números reais (ponto flutuante). |
| `textus` | `str` | Tipo de dado para cadeias de caracteres (strings). |
| `veritas` | `bool` | Tipo de dado para valores lógicos (verdadeiro/falso). |
| `scribe(expr).` | `print(expr)` | Comando de saída de dados no terminal. |
| `lege(id).` | `id = input()` | Comando de entrada de dados via teclado. |
| `si (cond) { ... }` | `if cond:` | Estrutura de controle condicional. |
| `aliter { ... }` | `else:` | Bloco alternativo para o comando `si`. |
| `dum (cond) { ... }` | `while cond:` | Estrutura de repetição condicional. |
| `pro (i=0 usque 5)` | `for i in range(0, 5):` | Estrutura de repetição com intervalo definido. |
| `a = 10.` | `a = 10` | Atribuição de valores com encerramento por ponto. |