import pytest
from src.parser_service import get_parser
from src.models import *

def test_exemplo_completo_pdf():
    parser = get_parser()
    code = """
    principium
      numerus a, b.
      textus nome.
      scribe("Digite seu nome: ").
      lege(nome).
      a = 10.
      b = 5 + 2 * 3. 
      
      si (b > a) {
        scribe(nome).
        scribe(" Venceu!").
      } aliter {
        dum (a > 0) {
          a = a - 1.
        }
      }
      pro (contador = 0 usque 5) {
        scribe(contador).
      }
    finis
    """
    ast = parser.parse(code.lower())
    
    assert isinstance(ast, Programa)
    cmds = ast.bloco.comandos
    
    assert isinstance(cmds[0], Declaracao)
    assert cmds[0].tipo == "numerus"
    assert "a" in cmds[0].ids
    
    atribuicao_b = cmds[5]
    assert atribuicao_b.id == "b"
    assert atribuicao_b.expr.operador == "+"
    assert atribuicao_b.expr.direita.operador == "*"
    
    assert isinstance(cmds[6], IfStmt)
    assert cmds[6].bloco_aliter is not None
    
    assert isinstance(cmds[7], ForStmt)
    assert cmds[7].id == "contador"
    assert cmds[7].inicio.valor == 0
    assert cmds[7].fim.valor == 5

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
