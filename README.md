# Transpilador Latim-Python

Este projeto é um transpilador completo que converte programas escritos em uma linguagem de programação personalizada baseada em **Latim** para **Python**. O sistema realiza todas as etapas clássicas de compilação: análise léxica, sintática, semântica e geração de código.

## Requisitos Mínimos Atendidos

Conforme o enunciado, este projeto implementa:
- **4+ Tipos de dados:** Inteiro (`numerus`), Decimal (`decimalis`), String (`textus`), Booleano (`veritas`), Nulo (`inanis`) e Lista (`collectio`).
- **Estrutura de Controle:** `si ... aliter` (equivalente ao `if ... else`).
- **Estruturas de Repetição:** `while` (`dum`), `for` (`pro ... usque`) e `do ... while` (`fac ... dum`).
- **Precedência Matemática:** Gramática estruturada para respeitar a ordem das operações (+, -, *, /).
- **Atribuições e Escopo:** Validação de tipos e verificação de variáveis declaradas.
- **Entrada e Saída:** Comandos `lege` (input) e `scribe` (print).
- **Números Decimais:** Suporte completo a tipos de ponto flutuante.

---

## Arquitetura do Sistema

O transpilador foi desenvolvido em Python utilizando a biblioteca **Lark** para o processamento da gramática.

1.  **Análise Léxica e Sintática (`src/grammar.lark`):** Define os tokens e a estrutura da gramática (LALR).
2.  **Modelagem (`src/models.py`):** Define os nós da Árvore de Sintaxe Abstrata (AST).
3.  **Transformação (`src/parser_service.py`):** Converte o parse tree do Lark para a nossa AST customizada.
4.  **Análise Semântica (`src/semantic_service.py`):**
    - Verifica se variáveis foram declaradas antes do uso.
    - Valida compatibilidade de tipos em operações e atribuições.
    - Garante que condições de loops e `if` sejam booleanas.
5.  **Geração de Código (`src/generator_service.py`):**
    - Traduz a AST para código Python 3.
    - Implementa **Casting Automático** no `input()` baseado no tipo da variável.
    - Garante a **Inclusividade** no loop `pro` (até o limite final).
    - Formata a saída de decimais para evitar ruído matemático.
    - Otimiza a interface de prompt (texto do `scribe` na mesma linha do `lege`).

---

## Especificação da Linguagem (Latim)

### Palavras Reservadas e Tipos
| Latim | Python | Descrição |
| :--- | :--- | :--- |
| `numerus` | `int` | Inteiro |
| `decimalis` | `float` | Decimal |
| `textus` | `str` | String |
| `veritas` | `bool` | Booleano (`verum` / `falsum`) |
| `inanis` | `NoneType` | Nulo (`nihil`) |
| `collectio` | `list` | Lista |

### Comandos e Estruturas
| Latim | Exemplo |
| :--- | :--- |
| **Início/Fim** | `principium` ... `finis` |
| **Saída** | `scribe("Olá").` |
| **Entrada** | `lege(nome).` |
| **Condicional** | `si (x > 0) { ... } aliter { ... }` |
| **Loop For** | `pro (i = 1 usque 10) { ... }` |
| **Loop While** | `dum (condicao) { ... }` |
| **Loop Do-While** | `fac { ... } dum (condicao).` |

---

## Instalação e Uso

### 1. Preparar o Ambiente
Recomendamos o uso de um ambiente virtual:
```bash
# Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

> **Nota para Linux (Ubuntu/Debian ou WSL)**: A interface gráfica (IDE) utiliza a biblioteca `Tkinter`. Se você receber um erro de módulo não encontrado, instale-a via gerenciador de pacotes:
> ```bash
> sudo apt-get update && sudo apt-get install -y python3-tk
> ```

### 2. Forma 1: Executar via Interface Gráfica (IDE Desktop)
A forma mais fácil e interativa de digitar, compilar e rodar programas em Latim é usando a nossa IDE nativa:
```bash
python3 gui.py
```
Isso abrirá uma janela com editor de código (modo escuro, números de linha, realce de sintaxe básico), console integrado e visualizador do código Python gerado em tempo real. Entradas (`lege`) são solicitadas através de caixas de diálogo interativas modernas.

### 3. Forma 2: Executar via Linha de Comando (CLI)
Você também pode compilar e executar o código diretamente pelo terminal clássico de comandos:

#### Passo A: Compilar o arquivo `.latim`
```bash
python3 main.py programa.latim
```
Isso gerará o arquivo traduzido `saida.py`.

#### Passo B: Executar o programa gerado
```bash
python3 saida.py
```

---

## Bateria de Testes

O projeto inclui diversos testes para validar os requisitos:
- `programa.latim`: Demonstração geral das funcionalidades.
- `teste_math.latim`: Valida precedência de operadores.
- `teste_loops.latim`: Valida todas as estruturas de repetição.
- `teste_io.latim`: Valida entrada/saída com casting de tipos.

Para rodar os testes automatizados do Parser:
```bash
pytest tests/test_parser.py
```

---

## 👥 Desenvolvedores
*   Gabriel Almeida
*   Rafael Rangel
*   Vitor Pio

---
*Projeto desenvolvido para a disciplina de Compiladores.*
