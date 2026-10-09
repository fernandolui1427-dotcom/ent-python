"""Demonstração: 10+ objetos, polimorfismo e tratamento de exceções."""

from modelos import (Banco, BancoError, Cliente, ContaCorrente, ContaPoupanca,
                     Conta, ContaNaoEncontradaError, SaldoInsuficienteError,
                     ValorInvalidoError)


def titulo(texto):
    print(f"\n{'=' * 70}\n{texto}\n{'=' * 70}")


def main():
    banco = Banco("Sprint6")

    titulo("1) Criando clientes e contas (10+ objetos)")
    clientes = [
        Cliente("Ana Souza", "ana@email.com", "529.982.247-25"),
        Cliente("Bruno Lima", "bruno@email.com", "111.444.777-35"),
        Cliente("Carla Dias", "carla@empresa.com.br", "390.533.447-05"),
        Cliente("Diego Alves", "diego@email.com", "123.456.789-09"),
    ]
    for cliente in clientes:
        banco.cadastrar_cliente(cliente)
    ana, bruno, carla, diego = clientes

    contas = [
        ContaCorrente(1001, ana, 1500.00, limite=1000),
        ContaPoupanca(1002, ana, 5000.00),
        ContaCorrente(1003, bruno, 300.00, limite=500, tarifa=20),
        ContaPoupanca(1004, bruno, 800.00, taxa_rendimento=0.007),
        ContaCorrente(1005, carla, 2500.00),
        ContaPoupanca(1006, carla, 12000.00, taxa_rendimento=0.006),
        ContaCorrente(1007, diego, 50.00, limite=100, tarifa=15),
    ]
    for conta in contas:
        banco.abrir_conta(conta)
    print(f"{len(clientes)} clientes + {len(contas)} contas + banco = "
          f"{len(clientes) + len(contas) + 1} objetos")
    print(banco)
    for cliente in clientes:
        print(" -", cliente)

    titulo("2) Operações e histórico")
    contas[0].depositar(500)
    contas[0].sacar(2300)             # usa cheque especial
    banco.transferir(1006, 1004, 1000)
    print(contas[0])
    for transacao in contas[0].historico:
        print("  ", transacao)

    titulo("3) Polimorfismo: mesma chamada, comportamentos diferentes")
    for conta, resultado in banco.executar_rotina_mensal():
        if isinstance(resultado, Exception):
            print(f"{conta.numero} {type(conta).__name__:<15} -> FALHA: {resultado}")
        else:
            print(f"{conta.numero} {type(conta).__name__:<15} -> "
                  f"{'+' if resultado >= 0 else '-'}R$ {abs(resultado):>8,.2f}")

    titulo("4) Ordenação com __lt__ e igualdade com __eq__")
    for conta in sorted(banco.contas, reverse=True):
        print(" ", conta)
    print("Conta 1001 == Conta 1001?", banco.buscar_conta(1001) == contas[0])
    print("Conta 1001 == Conta 1002?", contas[0] == contas[1])
    print("repr:", repr(contas[0]))

    titulo("5) Tratamento de exceções (entradas inválidas)")
    testes = [
        ("E-mail inválido", lambda: Cliente("Eva", "eva@@mail", "529.982.247-25")),
        ("CPF inválido", lambda: Cliente("Eva", "eva@mail.com", "12345")),
        ("Saldo inicial negativo", lambda: ContaPoupanca(2000, ana, -10)),
        ("Taxa inválida", lambda: ContaPoupanca(2001, ana, 100, taxa_rendimento=0.5)),
        ("Depósito negativo", lambda: contas[1].depositar(-50)),
        ("Saque acima do limite", lambda: contas[6].sacar(5000)),
        ("Conta inexistente", lambda: banco.buscar_conta(9999)),
        ("CPF duplicado", lambda: banco.cadastrar_cliente(ana)),
        ("Classe abstrata", lambda: Conta(1, ana)),
    ]
    for descricao, acao in testes:
        try:
            acao()
        except (BancoError, TypeError) as erro:
            print(f"{descricao:<24} -> {erro}")
        else:
            print(f"{descricao:<24} -> NÃO LEVANTOU ERRO")

    titulo("6) Resumo final")
    print(banco)
    for cliente in sorted(clientes):
        print(f" {cliente.nome:<12} saldo total: R$ {cliente.saldo_total:>10,.2f}")


if __name__ == "__main__":
    main()
