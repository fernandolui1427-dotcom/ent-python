"""Modelos do sistema bancário: exceções, Cliente, Transacao, Conta (abstrata),
ContaCorrente, ContaPoupanca e Banco."""

import re
from abc import ABC, abstractmethod
from datetime import datetime

PADRAO_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
PADRAO_CPF = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")


# ------------------------------------------------------------- Exceções
class BancoError(Exception):
    """Classe base das exceções do sistema bancário."""

    def __init__(self, mensagem="Erro no sistema bancário"):
        super().__init__(mensagem)
        self.mensagem = mensagem

    def __str__(self):
        return f"[{type(self).__name__}] {self.mensagem}"


class ValorInvalidoError(BancoError):
    """Valor monetário ou atributo fora das regras de negócio."""


class SaldoInsuficienteError(BancoError):
    """Operação deixaria a conta abaixo do limite permitido."""


class ContaNaoEncontradaError(BancoError):
    """Número de conta inexistente no banco."""


# -------------------------------------------------------------- Cliente
class Cliente:
    """Pessoa titular de uma ou mais contas (composição: Cliente TEM contas)."""

    def __init__(self, nome, email, cpf):
        self.nome = nome
        self.email = email
        self.cpf = cpf
        self._contas = []

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ValorInvalidoError("Nome deve ter ao menos 2 caracteres.")
        self._nome = valor.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        if not isinstance(valor, str) or not PADRAO_EMAIL.match(valor):
            raise ValorInvalidoError(f"E-mail inválido: {valor!r}")
        self._email = valor

    @property
    def cpf(self):
        return self._cpf

    @cpf.setter
    def cpf(self, valor):
        if not isinstance(valor, str) or not PADRAO_CPF.match(valor):
            raise ValorInvalidoError(f"CPF inválido (use 000.000.000-00): {valor!r}")
        self._cpf = valor

    @property
    def contas(self):
        """Cópia imutável das contas (protege a lista interna)."""
        return tuple(self._contas)

    @property
    def saldo_total(self):
        return sum(conta.saldo for conta in self._contas)

    def adicionar_conta(self, conta):
        self._contas.append(conta)

    def __str__(self):
        return f"{self.nome} <{self.email}> | CPF {self.cpf} | {len(self._contas)} conta(s)"

    def __repr__(self):
        return f"Cliente(nome={self.nome!r}, email={self.email!r}, cpf={self.cpf!r})"

    def __eq__(self, outro):
        return isinstance(outro, Cliente) and self.cpf == outro.cpf

    def __hash__(self):
        return hash(self.cpf)

    def __lt__(self, outro):
        return self.nome < outro.nome


# ------------------------------------------------------------ Transacao
class Transacao:
    """Registro imutável de uma movimentação na conta."""

    def __init__(self, tipo, valor, saldo_apos):
        if not isinstance(tipo, str) or not tipo:
            raise ValorInvalidoError("Tipo de transação inválido.")
        self._tipo = tipo
        self._valor = float(valor)
        self._saldo_apos = float(saldo_apos)
        self._data = datetime.now()

    @property
    def tipo(self):
        return self._tipo

    @property
    def valor(self):
        return self._valor

    @property
    def saldo_apos(self):
        return self._saldo_apos

    @property
    def data(self):
        return self._data

    def __str__(self):
        return (f"{self._data:%d/%m/%Y %H:%M} | {self._tipo:<14} | "
                f"R$ {self._valor:>10,.2f} | saldo R$ {self._saldo_apos:>10,.2f}")

    def __repr__(self):
        return f"Transacao({self._tipo!r}, {self._valor}, {self._saldo_apos})"


# ---------------------------------------------------------------- Conta
class Conta(ABC):
    """Classe abstrata: define o contrato comum de qualquer conta."""

    def __init__(self, numero, titular, saldo_inicial=0.0):
        if not isinstance(numero, int) or numero <= 0:
            raise ValorInvalidoError("Número da conta deve ser inteiro positivo.")
        if not isinstance(titular, Cliente):
            raise ValorInvalidoError("Titular deve ser um Cliente.")
        if saldo_inicial < 0:
            raise ValorInvalidoError("Saldo inicial não pode ser negativo.")
        self._numero = numero
        self._titular = titular
        self._saldo = float(saldo_inicial)
        self._historico = []

    # --- propriedades
    @property
    def numero(self):
        return self._numero

    @property
    def titular(self):
        return self._titular

    @property
    def limite(self):
        """Quanto a conta pode ficar negativa. Base: 0 (nunca negativa)."""
        return 0.0

    @property
    def saldo(self):
        return self._saldo

    @saldo.setter
    def saldo(self, valor):
        if valor < -self.limite:
            raise SaldoInsuficienteError(
                f"Conta {self._numero}: saldo R$ {valor:,.2f} ultrapassa o limite "
                f"permitido (-R$ {self.limite:,.2f})."
            )
        self._saldo = float(valor)

    @property
    def historico(self):
        return tuple(self._historico)

    # --- operações
    @staticmethod
    def _validar_valor(valor):
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValorInvalidoError(f"Valor deve ser positivo: {valor!r}")

    def _registrar(self, tipo, valor):
        self._historico.append(Transacao(tipo, valor, self._saldo))

    def depositar(self, valor):
        self._validar_valor(valor)
        self.saldo = self._saldo + valor
        self._registrar("DEPÓSITO", valor)

    def sacar(self, valor):
        self._validar_valor(valor)
        self.saldo = self._saldo - valor  # o setter bloqueia se passar do limite
        self._registrar("SAQUE", valor)

    @abstractmethod
    def aplicar_rotina_mensal(self):
        """Cada tipo de conta tem sua rotina (tarifa ou rendimento).
        Retorna o valor aplicado (negativo = cobrança, positivo = ganho)."""

    # --- dunder
    def __str__(self):
        return (f"{type(self).__name__} nº {self._numero} | {self._titular.nome} | "
                f"saldo R$ {self._saldo:,.2f}")

    def __repr__(self):
        return (f"{type(self).__name__}(numero={self._numero}, "
                f"titular={self._titular.nome!r}, saldo={self._saldo})")

    def __eq__(self, outro):
        return isinstance(outro, Conta) and self._numero == outro._numero

    def __hash__(self):
        return hash(self._numero)

    def __lt__(self, outro):
        return self._saldo < outro._saldo


class ContaCorrente(Conta):
    """Conta com cheque especial e tarifa mensal."""

    def __init__(self, numero, titular, saldo_inicial=0.0, limite=500.0, tarifa=15.0):
        self.limite = limite      # definido antes do super (o setter do saldo usa)
        self.tarifa = tarifa
        super().__init__(numero, titular, saldo_inicial)

    @property
    def limite(self):
        return self._limite

    @limite.setter
    def limite(self, valor):
        if valor < 0:
            raise ValorInvalidoError("Limite não pode ser negativo.")
        self._limite = float(valor)

    @property
    def tarifa(self):
        return self._tarifa

    @tarifa.setter
    def tarifa(self, valor):
        if valor < 0:
            raise ValorInvalidoError("Tarifa não pode ser negativa.")
        self._tarifa = float(valor)

    def aplicar_rotina_mensal(self):
        self.saldo = self._saldo - self._tarifa
        self._registrar("TARIFA", self._tarifa)
        return -self._tarifa

    def __str__(self):
        return f"{super().__str__()} | limite R$ {self._limite:,.2f}"


class ContaPoupanca(Conta):
    """Conta que não fica negativa e rende juros mensais."""

    def __init__(self, numero, titular, saldo_inicial=0.0, taxa_rendimento=0.005):
        super().__init__(numero, titular, saldo_inicial)
        self.taxa_rendimento = taxa_rendimento

    @property
    def taxa_rendimento(self):
        return self._taxa_rendimento

    @taxa_rendimento.setter
    def taxa_rendimento(self, valor):
        if not 0 <= valor <= 0.10:
            raise ValorInvalidoError("Taxa deve estar entre 0 e 0,10 (10%).")
        self._taxa_rendimento = float(valor)

    def aplicar_rotina_mensal(self):
        rendimento = self._saldo * self._taxa_rendimento
        self.saldo = self._saldo + rendimento
        if rendimento > 0:
            self._registrar("RENDIMENTO", rendimento)
        return rendimento

    def __str__(self):
        return f"{super().__str__()} | rende {self._taxa_rendimento:.2%}/mês"


# ---------------------------------------------------------------- Banco
class Banco:
    """Agrega clientes e contas (composição: Banco TEM clientes e contas)."""

    def __init__(self, nome):
        if not nome or not nome.strip():
            raise ValorInvalidoError("Nome do banco é obrigatório.")
        self._nome = nome.strip()
        self._clientes = {}
        self._contas = {}

    @property
    def nome(self):
        return self._nome

    @property
    def contas(self):
        return tuple(self._contas.values())

    @property
    def clientes(self):
        return tuple(self._clientes.values())

    def cadastrar_cliente(self, cliente):
        if cliente.cpf in self._clientes:
            raise ValorInvalidoError(f"CPF já cadastrado: {cliente.cpf}")
        self._clientes[cliente.cpf] = cliente
        return cliente

    def abrir_conta(self, conta):
        if conta.numero in self._contas:
            raise ValorInvalidoError(f"Número de conta já existe: {conta.numero}")
        self._contas[conta.numero] = conta
        conta.titular.adicionar_conta(conta)
        return conta

    def buscar_conta(self, numero):
        try:
            return self._contas[numero]
        except KeyError:
            raise ContaNaoEncontradaError(f"Conta {numero} não existe.") from None

    def transferir(self, origem, destino, valor):
        conta_origem = self.buscar_conta(origem)
        conta_destino = self.buscar_conta(destino)
        conta_origem.sacar(valor)
        conta_destino.depositar(valor)

    def executar_rotina_mensal(self):
        """Polimorfismo: a mesma chamada, comportamento diferente por tipo."""
        resultados = []
        for conta in self._contas.values():
            try:
                resultados.append((conta, conta.aplicar_rotina_mensal()))
            except SaldoInsuficienteError as erro:
                resultados.append((conta, erro))
        return resultados

    @property
    def total_depositado(self):
        return sum(conta.saldo for conta in self._contas.values())

    def __len__(self):
        return len(self._contas)

    def __str__(self):
        return (f"Banco {self._nome} | {len(self._clientes)} cliente(s) | "
                f"{len(self._contas)} conta(s) | R$ {self.total_depositado:,.2f}")

    def __repr__(self):
        return f"Banco(nome={self._nome!r})"
