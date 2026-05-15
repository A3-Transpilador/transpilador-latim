import sys
from src.parser_service import get_parser
from src.semantic_service import SemanticAnalyzer, SemanticError # IMPORTANTE
from src.generator_service import PythonGenerator

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_fonte.latim>")
        return

    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        return
    
    parser = get_parser()
    # 1. Análise Sintática (Lark)
    print("Realizando análise sintática...")
    parser = get_parser()
    ast = parser.parse(source_code.lower())
     
    # 2. Análise Semântica
    print("Validando regras semânticas...")
    try:
        analyzer = SemanticAnalyzer()
        analyzer.validar(ast)
        print("Análise semântica concluída com sucesso! Sem erros detectados.")
    except SemanticError as err:
        print(f"\n[ERRO DE COMPILAÇÃO] {err}")
        sys.exit(1)
        
    # 3. Geração de Código
    print("Traduzindo para Python...")
    generator = PythonGenerator()
    python_code = generator.generate(ast)

    output_file = "saida.py"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Codigo gerado automaticamente pelo compilador Latim-Python\n")
        f.write(python_code)
        f.write("\n")

    print(f"Sucesso! Código Python compilado em: '{output_file}'")

if __name__ == "__main__":
    main()