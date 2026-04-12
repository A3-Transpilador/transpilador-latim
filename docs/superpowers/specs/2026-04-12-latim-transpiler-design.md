# Design Spec: Transpilador Latim-Python (Lexer & Parser)

**Data:** 12 de Abril de 2026
**Autor:** Opencode (em colaboração com o usuário)
**Status:** Em Revisão

## 1. Objetivo
Desenvolver a camada frontal (frontend) de um transpilador da linguagem "Latim" para Python. O escopo abrange a análise léxica (Lexer), análise sintática (Parser) e a geração de uma Árvore de Sintaxe Abstrata (AST) estruturada em objetos Python (Dataclasses).

## 2. Requisitos de Linguagem (Gramática)
A linguagem deve seguir a estrutura:
- **Case-insensitivity:** `SI` == `si`.
- **Delimitadores:** Comandos simples terminam com ponto (`.`). Blocos de controle usam chaves `{ }`.
- **Palavras Reservadas:** `principium`, `finis`, `numerus`, `decimalis`, `textus`, `veritas`, `lege`, `scribe`, `si`, `aliter`, `dum`, `pro`, `usque`.
- **Tipos de Dados:** `numerus` (int), `decimalis` (float), `textus` (string), `veritas` (bool).
- **Booleanos:** `verum`, `falsum`.

## 3. Arquitetura Técnica
Utilizaremos a biblioteca **Lark** para análise sintática devido à sua flexibilidade e suporte a gramáticas EBNF.

### 3.1. Componentes
1.  **Gramática (EBNF):** Definição formal dos tokens e das regras de produção.
2.  **Modelos AST (Dataclasses):** Classes que representam os nós da árvore (ex: `BinOp`, `IfStmt`, `AssignStmt`).
3.  **Transformer (Lark):** Classe que converte a Parse Tree do Lark em instâncias das Dataclasses.

### 3.2. Precedência Matemática
A gramática será estruturada em camadas para garantir a ordem correta das operações:
1.  `expr` (Soma/Subtração)
2.  `termo` (Multiplicação/Divisão)
3.  `fator` (Átomos, parênteses)

## 4. Estrutura da AST (Exemplos de Classes)
- `Programa(comandos: List[BaseAST])`
- `Declaracao(tipo: str, ids: List[str])`
- `Atribuicao(id: str, expr: BaseAST)`
- `ComandoSi(condicao: BaseAST, bloco_entao: List[BaseAST], bloco_aliter: Optional[List[BaseAST]])`
- `ComandoPro(id: str, inicio: BaseAST, fim: BaseAST, bloco: List[BaseAST])`

## 5. Plano de Verificação
- **Testes Unitários do Lexer:** Verificar se tokens como `10.5`, `"texto"` e `si` são reconhecidos corretamente.
- **Testes de Precedência:** Validar se `5 + 2 * 3` resulta em uma árvore onde a multiplicação está abaixo da soma.
- **Testes de Gramática:** Submeter o exemplo de código "Input" fornecido pelo usuário e verificar se a AST é gerada sem erros.

## 6. Interface com o Grupo
O resultado final será uma função `parse_latim(codigo: str) -> Programa` que retorna o nó raiz da AST, permitindo que os outros membros do grupo implementem o `CodeGenerator` apenas iterando sobre os objetos da AST.
