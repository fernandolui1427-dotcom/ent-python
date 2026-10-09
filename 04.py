
# Sistema de Produtos com Vetores e Laços
# Versão equivalente à lógica de Portugol
# Os vetores têm tamanho fixo e são preenchidos por índices.

# 1. Cadastro usando vetores de tamanho fixo
quantidade = int(input("Quantos produtos deseja cadastrar? "))

nomes = [""] * quantidade
precos = [0.0] * quantidade
categorias = [""] * quantidade

for i in range(quantidade):
    print(f"\nCadastro do produto {i + 1}")

    nomes[i] = input("Nome: ")
    precos[i] = float(input("Preço: R$ "))
    categorias[i] = input("Categoria: ")

# 2. Filtragem por preço usando laços
valor_referencia = float(
    input("\nInforme o preço de referência: R$ ")
)

print("\n--- Produtos acima do preço ---")

for i in range(quantidade):
    if precos[i] > valor_referencia:
        print(
            f"{nomes[i]} - R$ {precos[i]:.2f} "
            f"- {categorias[i]}"
        )

print("\n--- Produtos abaixo do preço ---")

for i in range(quantidade):
    if precos[i] < valor_referencia:
        print(
            f"{nomes[i]} - R$ {precos[i]:.2f} "
            f"- {categorias[i]}"
        )

# 3. Ordenação por bolha (bubble sort)
# Ordena os preços em ordem crescente e troca também
# os nomes e as categorias para manter os dados juntos.

for i in range(quantidade - 1):
    for j in range(quantidade - 1 - i):
        if precos[j] > precos[j + 1]:
            precos[j], precos[j + 1] = (
                precos[j + 1], precos[j]
            )

            nomes[j], nomes[j + 1] = (
                nomes[j + 1], nomes[j]
            )

            categorias[j], categorias[j + 1] = (
                categorias[j + 1], categorias[j]
            )

print("\n--- Ordem crescente (bubble sort) ---")

for i in range(quantidade):
    print(f"{nomes[i]} - R$ {precos[i]:.2f}")

# 4. Ordem decrescente percorrendo o vetor ao contrário
print("\n--- Ordem decrescente ---")

for i in range(quantidade - 1, -1, -1):
    print(f"{nomes[i]} - R$ {precos[i]:.2f}")

# 5. Simulação manual de conjunto
# Compara cada categoria com as já armazenadas.
# Se for repetida, não é adicionada novamente.

categorias_unicas = [""] * quantidade
total_categorias = 0

for i in range(quantidade):
    repetida = False

    for j in range(total_categorias):
        if categorias[i] == categorias_unicas[j]:
            repetida = True
            break

    if not repetida:
        categorias_unicas[total_categorias] = categorias[i]
        total_categorias += 1

print("\n--- Categorias únicas ---")

for i in range(total_categorias):
    print(categorias_unicas[i])

# 6. Estatísticas calculadas com laços
if quantidade > 0:
    menor_preco = precos[0]
    maior_preco = precos[0]
    soma_precos = 0

    for i in range(quantidade):
        soma_precos += precos[i]

        if precos[i] < menor_preco:
            menor_preco = precos[i]

        if precos[i] > maior_preco:
            maior_preco = precos[i]

    media_precos = soma_precos / quantidade

    # Tupla imutável com as estatísticas
    estatisticas = (
        menor_preco,
        maior_preco,
        media_precos
    )

    # 7. Relatório final com f-strings
    print("\n========== RELATÓRIO FINAL ==========")
    print(f"Total de produtos: {quantidade}")
    print(f"Menor preço: R$ {estatisticas[0]:.2f}")
    print(f"Maior preço: R$ {estatisticas[1]:.2f}")
    print(f"Média dos preços: R$ {estatisticas[2]:.2f}")
    print(f"Total de categorias: {total_categorias}")
    print("=====================================")
else:
    print("Nenhum produto foi cadastrado.")