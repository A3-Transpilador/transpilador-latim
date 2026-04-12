import pytest
from src.parser_service import get_parser
from src.models import *

def test_full_program():
    parser = get_parser()
    code = """
    principium
      numerus a, b.
      a = 10.
      b = 5 + 2 * 3.
      si (b > a) {
        scribe("venceu").
      }
    finis
    """
    ast = parser.parse(code.lower())
    assert isinstance(ast, Programa)
    assert len(ast.bloco.comandos) == 4
    b_assign = ast.bloco.comandos[2]
    assert b_assign.id == "b"
    assert b_assign.expr.operador == "+"
    assert b_assign.expr.direita.operador == "*"

def test_loops():
    parser = get_parser()
    code = """
    principium
      pro (i = 0 usque 5) {
        scribe(i).
      }
      dum (verum) {
        scribe("loop").
      }
    finis
    """
    ast = parser.parse(code.lower())
    assert isinstance(ast.bloco.comandos[0], ForStmt)
    assert isinstance(ast.bloco.comandos[1], WhileStmt)
