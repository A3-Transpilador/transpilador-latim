import sys
from src.parser_service import get_parser
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
    
    print("Realizando análise sintática...")
    ast = parser.parse(source_code.lower())

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