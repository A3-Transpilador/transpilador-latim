from dataclasses import dataclass
from typing import List, Union, Optional

@dataclass
class BaseAST:
    pass

@dataclass
class Expressao(BaseAST):
    pass

@dataclass
class Literal(Expressao):
    valor: Union[int, float, str, bool]

@dataclass
class Variavel(Expressao):
    nome: str

@dataclass
class BinOp(Expressao):
    esquerda: Expressao
    operador: str
    direita: Expressao

@dataclass
class Comando(BaseAST):
    pass

@dataclass
class Bloco(BaseAST):
    comandos: List[Comando]

@dataclass
class Declaracao(Comando):
    tipo: str
    ids: List[str]

@dataclass
class Atribuicao(Comando):
    id: str
    expr: Expressao

@dataclass
class Leitura(Comando):
    id: str

@dataclass
class Escrita(Comando):
    expr: Expressao

@dataclass
class IfStmt(Comando):
    condicao: Expressao
    bloco_entao: Bloco
    bloco_aliter: Optional[Bloco] = None

@dataclass
class WhileStmt(Comando):
    condicao: Expressao
    bloco: Bloco

@dataclass
class ForStmt(Comando):
    id: str
    inicio: Expressao
    fim: Expressao
    bloco: Bloco

@dataclass
class DoWhileStmt(Comando):
    bloco: Bloco
    condicao: Expressao
@dataclass
class Programa(BaseAST):
    bloco: Bloco
