# iFood Data Scraper

Scripts Python para extrair dados de estabelecimentos/restaurantes da API do iFood para a região de São Paulo.

## Visão Geral

Dois scripts que coletam informações detalhadas sobre estabelecimentos e restaurantes do marketplace iFood:
- `restaurantes/PROJETO_LEONARDO (2).py` - Restaurantes de delivery de comida
- `outras categorias/PROJETO_LEONARDO_outras_SP.py` - Outras categorias (mercados, farmácias, pet shops, etc.)

## Recursos

- Extração multi-localização em 10 coordenadas de São Paulo
- Processamento paralelo para coleta mais rápida de dados
- Consultas GraphQL API para informações detalhadas de estabelecimentos
- Tratamento automático de paginação
- Exportação Excel com dados estruturados

## Dados Coletados

Cada entrada de estabelecimento inclui:
- **Localização**: Rua, número, bairro, cidade, CEP, coordenadas
- **Negócio**: Nome, CNPJ, categoria
- **Preços**: Faixa de preço ($-$$$$$), valor mínimo do pedido, taxa de entrega
- **Métricas**: Avaliação de usuários, tempo de entrega
- **Status**: Flag Super Restaurante

## Categorias

| Script | Categorias |
|--------|-----------|
| Restaurantes | HOME_FOOD_DELIVERY |
| Outras Categorias | MERCADO_BEBIDAS, HOME_MERCADO_BR, MERCADO_FARMACIA, MERCADO_PETSHOP, SHOPPING_OFICIAL |

## Requisitos

```bash
pip install pandas requests openpyxl
```

## Configuração

1. Crie um arquivo `TENTATIVAS.txt` no diretório de cada script contendo o número de tentativas de repetição (ex: `5`)

## Uso

```bash
# Para restaurantes
cd restaurantes
python "PROJETO_LEONARDO (2).py"

# Para outras categorias
cd "outras categorias"
python "PROJETO_LEONARDO_outras_SP.py"
```

## Saída

Cada script gera arquivos Excel nomeados `RESULTADO {CATEGORIA} IFOOD.xlsx` contendo todos os dados de estabelecimentos coletados.
