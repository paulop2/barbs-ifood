# iFood Data Scraper

Python scripts to scrape merchant/restaurant data from iFood's API for São Paulo region.

## Overview

Two scripts that collect detailed information about merchants and restaurants from iFood marketplace:
- `restaurantes/PROJETO_LEONARDO (2).py` - Food delivery restaurants
- `outras categorias/PROJETO_LEONARDO_outras_SP.py` - Other categories (markets, pharmacies, pet shops, etc.)

## Features

- Multi-location scraping across 10 São Paulo coordinates
- Parallel processing for faster data collection
- GraphQL API queries for detailed merchant information
- Automatic pagination handling
- Excel export with structured data

## Collected Data

Each merchant entry includes:
- **Location**: Street, number, neighborhood, city, CEP, coordinates
- **Business**: Name, CNPJ, category
- **Pricing**: Price range ($-$$$$$), minimum order value, delivery fee
- **Metrics**: User rating, delivery time
- **Status**: Super Restaurant flag

## Categories

| Script | Categories |
|--------|-----------|
| Restaurantes | HOME_FOOD_DELIVERY |
| Outras Categorias | MERCADO_BEBIDAS, HOME_MERCADO_BR, MERCADO_FARMACIA, MERCADO_PETSHOP, SHOPPING_OFICIAL |

## Requirements

```bash
pip install pandas requests openpyxl
```

## Setup

1. Create a `TENTATIVAS.txt` file in each script's directory containing the number of retry attempts (e.g., `5`)

## Usage

```bash
# For restaurants
cd restaurantes
python "PROJETO_LEONARDO (2).py"

# For other categories
cd "outras categorias"
python "PROJETO_LEONARDO_outras_SP.py"
```

## Output

Each script generates Excel files named `RESULTADO {CATEGORY} IFOOD.xlsx` containing all collected merchant data.
