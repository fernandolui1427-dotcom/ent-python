"""Sistema de Análise de Dados: leitura de CSV, validação com regex,
tratamento de exceções e relatório formatado."""

import csv
import re
import sys
from datetime import date, datetime

COLUNAS_OBRIGATORIAS = ["nome", "email", "cpf", "telefone", "data_nascimento"]
IDADE_MINIMA = 0
IDADE_MAXIMA = 120

# ---------------------------------------------------------------- Regex
PADRAO_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
PADRAO_CPF = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
PADRAO_TELEFONE = re.compile(r"^\(?\d{2}\)?\s?9?\d{4}-?\d{4}$")
PADRAO_DATA = re.compile(r"^(0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/\d{4}$")


# ------------------------------------------------- Exceções personalizadas
class FormatoInvalidoError(Exception):
    """Campo não respeita o formato esperado."""

    def __init__(self, campo, valor):
        self.campo = campo
        self.valor = valor
        super().__init__(f"{campo} inválido: '{valor}'")


class IdadeInvalidaError(Exception):
    """Idade fora do intervalo permitido pela regra de negócio."""

    def __init__(self, idade):
        self.idade = idade
        super().__init__(
            f"idade {idade} fora do intervalo {IDADE_MINIMA}-{IDADE_MAXIMA}"
        )


# ------------------------------------------------------------ Validações
def validar_email(email):
    if not PADRAO_EMAIL.match(email):
        raise FormatoInvalidoError("e-mail", email)


def validar_cpf(cpf):
    if not PADRAO_CPF.match(cpf):
        raise FormatoInvalidoError("CPF", cpf)
    numeros = [int(d) for d in re.findall(r"\d", cpf)]
    if len(set(numeros)) == 1:
        raise FormatoInvalidoError("CPF (dígitos repetidos)", cpf)
    for pos in (9, 10):  # dígitos verificadores
        soma = sum(n * p for n, p in zip(numeros[:pos], range(pos + 1, 1, -1)))
        digito = (soma * 10 % 11) % 10
        if digito != numeros[pos]:
            raise FormatoInvalidoError("CPF (dígito verificador)", cpf)


def validar_telefone(telefone):
    if not PADRAO_TELEFONE.match(telefone):
        raise FormatoInvalidoError("telefone", telefone)


def validar_data(texto):
    """Valida formato DD/MM/AAAA, data real e idade. Retorna a idade."""
    if not PADRAO_DATA.match(texto):
        raise FormatoInvalidoError("data", texto)
    try:
        nascimento = datetime.strptime(texto, "%d/%m/%Y").date()
    except ValueError:  # ex.: 31/02/1999 passa no regex mas não existe
        raise FormatoInvalidoError("data (inexistente)", texto)
    hoje = date.today()
    idade = hoje.year - nascimento.year - (
        (hoje.month, hoje.day) < (nascimento.month, nascimento.day)
    )
    if not IDADE_MINIMA <= idade <= IDADE_MAXIMA:
        raise IdadeInvalidaError(idade)
    return idade


def validar_registro(linha):
    """Valida todos os campos; levanta exceção no primeiro erro."""
    validar_email(linha["email"].strip())
    validar_cpf(linha["cpf"].strip())
    validar_telefone(linha["telefone"].strip())
    return validar_data(linha["data_nascimento"].strip())


# --------------------------------------------------------------- Leitura
def ler_csv(caminho):
    """Lê o CSV e devolve lista de dicionários."""
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in (leitor.fieldnames or [])]
        if faltando:
            raise KeyError(", ".join(faltando))
        return list(leitor)


def analisar(registros):
    validos, invalidos, idades = [], [], []
    for numero, linha in enumerate(registros, start=2):  # linha 1 = cabeçalho
        try:
            idade = validar_registro(linha)
        except (FormatoInvalidoError, IdadeInvalidaError) as erro:
            invalidos.append((numero, linha["nome"], str(erro)))
        except (KeyError, AttributeError):
            invalidos.append((numero, linha.get("nome", "?"), "linha incompleta"))
        else:
            validos.append((numero, linha["nome"], idade))
            idades.append(idade)
    return validos, invalidos, idades


# ------------------------------------------------------------- Relatório
def gerar_relatorio(validos, invalidos, idades):
    total = len(validos) + len(invalidos)
    pct = (len(validos) / total * 100) if total else 0
    media = (sum(idades) / len(idades)) if idades else 0
    linhas = [
        "=" * 60,
        f"{'RELATÓRIO DE ANÁLISE DE DADOS':^60}",
        f"{'Gerado em ' + datetime.now().strftime('%d/%m/%Y %H:%M'):^60}",
        "=" * 60,
        "",
        f"REGISTROS VÁLIDOS ({len(validos)})",
        "-" * 60,
    ]
    linhas += [f"Linha {n:<3} | {nome:<20} | {idade:>3} anos" for n, nome, idade in validos]
    linhas += ["", f"REGISTROS INVÁLIDOS ({len(invalidos)})", "-" * 60]
    linhas += [f"Linha {n:<3} | {nome:<12} | {motivo}" for n, nome, motivo in invalidos]
    linhas += [
        "",
        "ESTATÍSTICAS",
        "-" * 60,
        f"Total de registros : {total}",
        f"Válidos            : {len(validos)} ({pct:.1f}%)",
        f"Inválidos          : {len(invalidos)} ({100 - pct:.1f}%)" if total else "Inválidos          : 0",
        f"Idade média        : {media:.1f} anos",
        f"Idade mín/máx      : {min(idades, default=0)} / {max(idades, default=0)}",
        "=" * 60,
    ]
    return "\n".join(linhas)


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else "dados.csv"
    try:
        registros = ler_csv(caminho)
    except FileNotFoundError:
        print(f"Erro: o arquivo '{caminho}' não foi encontrado.")
    except KeyError as erro:
        print(f"Erro: coluna(s) ausente(s) no CSV: {erro}")
    except ValueError as erro:
        print(f"Erro de conversão de valor: {erro}")
    else:
        validos, invalidos, idades = analisar(registros)
        relatorio = gerar_relatorio(validos, invalidos, idades)
        print(relatorio)
        with open("relatorio.txt", "w", encoding="utf-8") as saida:
            saida.write(relatorio)
        print("\nRelatório salvo em 'relatorio.txt'.")
    finally:
        print("Execução finalizada.")


if __name__ == "__main__":
    main()
