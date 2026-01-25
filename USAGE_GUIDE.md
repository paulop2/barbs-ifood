# iFood Scraper - Usage Guide

## Overview

The unified iFood scraper provides an interactive workflow for scraping restaurant and merchant data from iFood's marketplace. The script guides you through three simple steps:

1. **Select Coordinates** - Choose locations on an interactive map
2. **Capture Headers** - Automatically capture fresh session headers from iFood
3. **Scrape Data** - Fetch and export merchant data to CSV

## Installation

### Prerequisites

Make sure you have Python 3.7+ installed.

### Install Dependencies

```bash
# Install required packages
pip install pandas requests openpyxl playwright

# Install Playwright browsers (required for header capture)
playwright install chromium
```

## Quick Start

### Basic Usage

Run the scraper with default settings (restaurants):

```bash
python run_scraper.py
```

### Specify Category

Choose which category to scrape:

```bash
# Restaurants (food delivery)
python run_scraper.py --category HOME_FOOD_DELIVERY

# Beverage markets
python run_scraper.py --category MERCADO_BEBIDAS

# General markets
python run_scraper.py --category HOME_MERCADO_BR

# Pharmacies
python run_scraper.py --category MERCADO_FARMACIA

# Pet shops
python run_scraper.py --category MERCADO_PETSHOP

# Official shopping
python run_scraper.py --category SHOPPING_OFICIAL
```

## Workflow Steps

### Step 1: Select Coordinates

1. The script will automatically open your web browser with an interactive map
2. Click on the map to select locations where you want to scrape data
3. You'll see markers appear for each selected location
4. Options:
   - **Click existing marker** to remove it
   - **Clear All** button to start over
   - **Load Default Grid** button to load 10 pre-configured São Paulo locations
   - **Submit** button when you're done selecting

The selected coordinates will be saved to `coordinates.json`.

### Step 2: Capture Headers

The script will automatically:
1. Open a Chromium browser window
2. Navigate to iFood.com.br
3. Capture fresh session headers from API requests
4. Save headers to `captured_headers.json`
5. Close the browser

This process takes 10-20 seconds. The browser may stay open if manual interaction is needed.

### Step 3: Scrape Data

The script will:
1. Fetch merchant IDs from all selected coordinates
2. Remove duplicates
3. Fetch detailed information for each merchant (parallel processing)
4. Export data to CSV file: `RESULTADO {CATEGORY} IFOOD.csv`

## Advanced Options

### Skip Coordinate Selection

Reuse previously saved coordinates:

```bash
python run_scraper.py --skip-map
```

This will load `coordinates.json` from the previous run.

### Skip Header Capture

Reuse previously captured headers:

```bash
python run_scraper.py --skip-headers
```

This will load `captured_headers.json` from the previous run.

**Note:** Headers may expire after a while, so you may need to recapture them if scraping fails.

### Combine Options

```bash
python run_scraper.py --category MERCADO_BEBIDAS --skip-map --skip-headers
```

This is useful for running multiple categories with the same coordinates and headers.

## Output Files

### Generated Files

- **`coordinates.json`** - Your selected coordinates
- **`captured_headers.json`** - Captured session headers
- **`RESULTADO {CATEGORY} IFOOD.csv`** - Merchant data (final output)

### CSV Columns

The output CSV contains the following columns:

- **NOME** - Merchant name
- **RUA** - Street name
- **NUMERO** - Street number
- **BAIRRO** - District/Neighborhood
- **CIDADE** - City
- **CEP** - Postal code
- **LATITUDE** - Merchant latitude
- **LONGITUDE** - Merchant longitude
- **CNPJ** - Tax ID (Brazilian company registration)
- **PRECO MEDIO** - Price range ($, $$, $$$, $$$$, $$$$$)
- **VALOR MINIMO** - Minimum order value
- **CATEGORIA** - Main category
- **AVALIACAO** - User rating
- **TEMPO ENTREGA** - Delivery time
- **VALOR ORIGINAL** - Original delivery fee
- **SUPER RESTAURANTE** - Super Restaurant flag (SIM/NAO)

## Configuration

### Retry Attempts

The scraper uses retry attempts from `TENTATIVAS.txt` files:

- `restaurantes/TENTATIVAS.txt` - For HOME_FOOD_DELIVERY (default: 5)
- `outras categorias/TENTATIVAS.txt` - For other categories (default: 17000)

You can edit these files to change retry behavior.

## Troubleshooting

### Browser Doesn't Open

**Problem:** Coordinate picker or header capture doesn't open browser

**Solutions:**
- Make sure Playwright is installed: `playwright install chromium`
- Try running manually: `python coordinate_picker_server.py`
- Check your default browser settings

### Header Capture Fails

**Problem:** Headers not captured automatically

**Solutions:**
- The browser window will stay open - manually browse iFood
- Enter your delivery location
- Browse some restaurants
- Headers should be captured and saved

### No Merchants Found

**Problem:** Scraper finds 0 merchants

**Solutions:**
- Try different coordinates (some locations may have no merchants)
- Recapture headers: `python run_scraper.py --skip-map`
- Check your internet connection
- Verify the category is correct

### Encoding Errors (Windows)

**Problem:** Unicode characters display incorrectly

**Solution:** The code uses ASCII-safe characters, but if you see issues:
- Use Windows Terminal instead of Command Prompt
- Or run in Git Bash / WSL

## Tips & Best Practices

1. **Use Default Grid First**: Click "Load Default Grid" to see how it works with 10 pre-configured São Paulo locations

2. **Headers Expire**: If you get errors after a while, recapture headers with:
   ```bash
   python run_scraper.py --skip-map
   ```

3. **Multiple Categories**: Scrape multiple categories by running the script multiple times:
   ```bash
   python run_scraper.py --category HOME_FOOD_DELIVERY --skip-map --skip-headers
   python run_scraper.py --category MERCADO_BEBIDAS --skip-map --skip-headers
   python run_scraper.py --category MERCADO_FARMACIA --skip-map --skip-headers
   ```

4. **More Coverage**: Select more coordinates on the map for better coverage, but be aware:
   - More coordinates = longer scraping time
   - Overlapping areas will find duplicate merchants (automatically removed)

5. **Coordinate Strategy**:
   - Spread coordinates across the city for maximum coverage
   - Each coordinate covers roughly a 3-5km radius
   - Use 10-20 coordinates for a full city

## Legacy Scripts

Your original scripts are still available as backups:

- `restaurantes/PROJETO_LEONARDO (2).py` - Original restaurant scraper
- `outras categorias/PROJETO_LEONARDO_outras_SP.py` - Original multi-category scraper

These scripts still work with hardcoded coordinates and headers if you need them.

## Support

If you encounter issues:

1. Check this guide first
2. Make sure all dependencies are installed
3. Try recapturing headers
4. Check that coordinates.json has valid data
5. Verify your internet connection

## Example Session

```
============================================================
|          iFood Data Scraper - Interactive Mode           |
============================================================

------------------------------------------------------------
Step 1/3: Select Coordinates
------------------------------------------------------------
 -> Opening coordinate picker in your browser...
 -> Click on the map to select scraping locations
 -> Press Submit when done

[Waiting for coordinate selection...]
[+] Received 8 coordinates

------------------------------------------------------------
Step 2/3: Capture Headers
------------------------------------------------------------
 -> Opening iFood in browser...
 -> Capturing session headers automatically...
 -> [This may take 10-20 seconds]

[+] Headers captured successfully
 ->   - Session ID: 8d1d8bd8-xxxx
 ->   - App Key: 41a266ee-xxxx

------------------------------------------------------------
Step 3/3: Scraping Data
------------------------------------------------------------
 -> Category: Restaurantes (delivery de comida)
 -> Coordinates: 8 locations

 -> Fetching merchant IDs from 8 locations...
   [8/8] Location (-23.4488, -46.3565)...

[+] Found 342 unique merchants

 -> Fetching detailed merchant information (parallel processing)...
   Processing 342 merchants with 3 workers...
   [########################################] 342/342 (100.0%)

[+] Retrieved details for 342 merchants

 -> Generating CSV file...
[+] CSV generated: C:\Users\PVS\projetos\barbs-ifood\RESULTADO HOME_FOOD_DELIVERY IFOOD.csv

============================================================
|                  Scraping Complete!                      |
============================================================
```

---

**Happy Scraping!**
