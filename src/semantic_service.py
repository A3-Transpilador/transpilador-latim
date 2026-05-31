from src.models import (
    Programa, Bloco, Declaracao, Atribuicao, Leitura, 
    Escrita, IfStmt, WhileStmt, ForStmt, BinOp, Literal, Variavel, DoWhileStmt
)

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.tabela_simbolos = {}

    def validar(self, node):
        """Método principal para iniciar a validação a partir da raiz."""
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(f"Método visit_{type(node).__name__} não implementado no Semântico.")

    def visit_Programa(self, node: Programa):
        self.validar(node.bloco)

    def visit_Bloco(self, node: Bloco):
        for comando in node.comandos:
            self.validar(comando)
   
    def visit_Declaracao(self, node: Declaracao):
        # Cadastra as variáveis na tabela de símbolos com o seu devido tipo
        for v_id in node.ids:
            if v_id in self.tabela_simbolos:
                raise SemanticError(f"Erro Semântico: Variável '{v_id}' já foi declarada anteriormente.")
            self.tabela_simbolos[v_id] = node.tipo

    def visit_Atribuicao(self, node: Atribuicao):
        # Regra 1: Verificar se a variável esquerda foi declarada
        if node.id not in self.tabela_simbolos:
            raise SemanticError(f"Erro Semântico: Variável '{node.id}' usada na atribuição não foi declarada.")

        tipo_esperado = self.tabela_simbolos[node.id]
        tipo_expressao = self.validar(node.expr)
        
        if tipo_esperado == "decimalis" and tipo_expressao == "numerus":
            return
        # Regra 2: Verificar compatibilidade de tipos na atribuição
        if tipo_esperado != tipo_expressao:
            raise SemanticError(
                f"Erro Semântico: Tipo inválido para '{node.id}'. "
                f"Declarada como '{tipo_esperado}', mas recebeu uma expressão do tipo '{tipo_expressao}'."
            )

    def visit_Leitura(self, node: Leitura):
        # Verificar se a variável onde o input vai salvar foi declarada
        if node.id not in self.tabela_simbolos:
            raise SemanticError(f"Erro Semântico: Variável '{node.id}' usada no comando lege() não foi declarada.")

    def visit_Escrita(self, node: Escrita):
        # O comando scribe() pode aceitar qualquer tipo válido, só precisamos validar a expressão interna
        self.validar(node.expr)

    def visit_IfStmt(self, node: IfStmt):
        # Valida a expressão lógica/relacional do si (...)
        tipo_condicao = self.validar(node.condicao)
        if tipo_condicao != "veritas":
            raise SemanticError(f"Erro Semântico: Condição do comando si() deve ser do tipo 'veritas', mas recebeu '{tipo_condicao}'.")
        # Valida os blocos internos
        self.validar(node.bloco_entao)
        if node.bloco_aliter:
            self.validar(node.bloco_aliter)

    def visit_WhileStmt(self, node: WhileStmt):
        # Valida a expressão lógica/relacional do dum (...)
        tipo_condicao = self.validar(node.condicao)
        if tipo_condicao != "veritas":
            raise SemanticError(f"Erro Semântico: Condição do comando dum() deve ser do tipo 'veritas', mas recebeu '{tipo_condicao}'.")
        self.validar(node.bloco)

    def visit_ForStmt(self, node: ForStmt):
        # O iterador do pro (contador) precisa ser uma variável declarada ou tratada
        if node.id not in self.tabela_simbolos:
            raise SemanticError(f"Erro Semântico: Variável iteradora '{node.id}' no comando pro() não foi declarada.")
        
        if self.tabela_simbolos[node.id] != "numerus":
            raise SemanticError(f"Erro Semântico: A variável iteradora '{node.id}' do pro() precisa ser do tipo 'numerus'.")
        
        # Garante que os limites de início e fim avaliem para números
        tipo_inicio = self.validar(node.inicio) if hasattr(node, 'inicio') else "numerus"
        tipo_fim = self.validar(node.fim) if hasattr(node, 'fim') else "numerus"

        if tipo_inicio != "numerus" or tipo_fim != "numerus":
            raise SemanticError("Erro Semântico: Os limites do intervalo do comando pro() devem ser do tipo 'numerus'.")

        self.validar(node.bloco)
  
    def visit_DoWhileStmt(self, node: DoWhileStmt):
        self.validar(node.bloco)
        
        tipo_condicao = self.validar(node.condicao)
        if tipo_condicao != "veritas":
            print(f"Aviso Semântico: Condição do do-while deveria ser veritas, recebeu {tipo_condicao}")
  
    def visit_BinOp(self, node: BinOp):
        # Valida recursivamente o lado esquerdo e o lado direito da operação matemática/relacional
        tipo_esq = self.validar(node.esquerda)
        tipo_dir = self.validar(node.direita)

        # Se for um operador relacional (==, !=, <, >, <=, >=)
        if node.operador in ["==", "!=", "<", ">", "<=", ">="]:
            # Permite comparar apenas tipos iguais (ex: número com número)
            if tipo_esq != tipo_dir:
                # Permitir comparar numerus com decimalis (coerção)
                if (tipo_esq in ["numerus", "decimalis"]) and (tipo_dir in ["numerus", "decimalis"]):
                    return "veritas"
                raise SemanticError(f"Erro: Nao se compara {tipo_esq} com {tipo_dir}.")
            return "veritas"
        # Se for operador matemático (+, -, *, /)
        # Se for operador matemático (+, -, *, /)
        else:
            # Bloqueio de tipos não numéricos
            tipos_numericos = ["numerus", "decimalis"]
            if tipo_esq not in tipos_numericos or tipo_dir not in tipos_numericos:
                raise SemanticError(f"Erro Semântico: Operação matemática inválida entre {tipo_esq} e {tipo_dir}.")

            # REGRA DE OURO: Se a operação envolver um decimal ou for uma DIVISÃO, 
            # o resultado da expressão inteira sobe para 'decimalis'
            if tipo_esq == "decimalis" or tipo_dir == "decimalis" or node.operador == "/":
                return "decimalis"
            
            return "numerus"

    def visit_Literal(self, node: Literal):
        # Mapeia o tipo do valor primitivo do Python de volta para os tipos da nossa gramática
        if node.valor is None:
            return "inanis"
        if isinstance(node.valor, list):
            return "collectio"
        if isinstance(node.valor, bool):
            return "veritas"
        if isinstance(node.valor, int):
            return "numerus"
        if isinstance(node.valor, float):
            return "decimalis"
        if isinstance(node.valor, str):
            return "textus"

    def visit_Variavel(self, node: Variavel):
        # Quando uma variável isolada aparece em uma expressão, checa se existe e retorna seu tipo
        print(f"DEBUG: Tentando validar a variável: {node.nome}")
        if node.nome not in self.tabela_simbolos:
            raise SemanticError(f"Erro Semântico: Variável '{node.nome}' não foi declarada.")
        return self.tabela_simbolos[node.nome]