# exchange-rate-bot

## References

- [Nexa Banco](https://www.nexabanco.com/)

- [Pinggy](https://pinggy.io/)

```bash
ssh -p 443 -R0:127.0.0.1:8000 qr@free.pinggy.io
```

## aiohttp

[aiohttp client quickstart](https://docs.aiohttp.org/en/stable/client_quickstart.html)

Note
Don’t create a session per request. Most likely you need a session per application which performs all requests together.

More complex cases may require a session per site, e.g. one for Github and other one for Facebook APIs. Anyway making a session for every request is a very bad idea.

A session contains a connection pool inside. Connection reusage and keep-alive (both are on by default) may speed up total performance.

## Banrural API Discovery

### Summary

This document explains the step-by-step process of how Banrural's internal API was discovered and implemented to obtain USD exchange rates.

### Initial Problem

When attempting traditional web scraping of the Banrural website (https://www.banrural.com.gt/site/personas), the scraper could not find exchange rates in the initial HTML. The elements existed but were empty:

```html
<p id="efectivo-compra">Q</p>
<p id="documento-compra">Q</p>
<p id="banca-viarual-compra-mobile">Q</p>
```

### Discovery Process

#### 1. Initial HTML Analysis

First, the main page HTML was analyzed using `curl`:

```bash
curl -s "https://www.banrural.com.gt/site/personas" | grep -i "7\.59\|cambio\|dolar\|usd" -A 3 -B 3
```

**Result:** HTML elements with exchange rate-related IDs were found, but without values.

#### 2. Dynamic Loading Identification

The HTML showed that data is loaded dynamically via JavaScript:

```html
<script src="https://www.banrural.com.gt/hubfs/.../template_tipo_de_cambio.min.js"></script>
```

#### 3. JavaScript Analysis

The JavaScript file was downloaded and analyzed:

```bash
curl -s "https://www.banrural.com.gt/hubfs/hub_generated/template_assets/1/188510768808/1753208208135/template_tipo_de_cambio.js"
```

**Key finding:** The JavaScript contained code that populated HTML elements:

```javascript
$('#efectivo-compra').text('Q' + datosCompletos.compra_dolares);
$('#documento-compra').text('Q' + datosCompletos.compra_dolares_docto);
$('#banca-viarual-compra-mobile').text('Q' + datosCompletos.compra_dolares_docto_bv);
```

#### 4. API Discovery

Continuing the JavaScript analysis, the AJAX call was found:

```javascript
$.ajax({
  url: '/_hcms/api/site/banrural/tasadecambio',
  type: 'GET',
  contentType: 'application/json',
  data: JSON.stringify(),
```

**Eureka!** The internal API was: `/_hcms/api/site/banrural/tasadecambio`

#### 5. Initial API Test

First direct test:

```bash
curl -s "https://www.banrural.com.gt/_hcms/api/site/banrural/tasadecambio"
```

**Result:** `{"error":"Acceso no autorizado"}`

#### 6. Required Headers Analysis

To simulate a legitimate browser request, specific headers were added:

```bash
curl -s "https://www.banrural.com.gt/_hcms/api/site/banrural/tasadecambio" \
  -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36" \
  -H "Referer: https://www.banrural.com.gt/site/personas" \
  -H "X-Requested-With: XMLHttpRequest"
```

**Success!** The API responded with complete JSON data:

```json
{
  "compra_dolares": "7.53",
  "venta_dolares": "7.80",
  "compra_euros": "8.36",
  "venta_euros": "9.75",
  "compra_dolares_docto": "7.56",
  "venta_dolares_docto": "7.80",
  "compra_dolares_docto_bv": "7.59",
  "venta_dolares_docto_bv": "7.77",
  "compra_euros_docto": "8.47",
  "venta_euros_docto": "9.75"
}
```

### Value Mapping

| API Field | Description | Value |
|-----------|-------------|-------|
| `compra_dolares` | Cash USD (Buy) | 7.53 |
| `compra_dolares_docto` | Document USD (Buy) | 7.56 |
| `compra_dolares_docto_bv` | **Virtual Banking APP (Buy)** | **7.59** |
| `venta_dolares` | Cash USD (Sell) | 7.80 |
| `venta_dolares_docto` | Document USD (Sell) | 7.80 |
| `venta_dolares_docto_bv` | Virtual Banking APP (Sell) | 7.77 |

### Final Implementation

#### Critical Headers

```python
api_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.banrural.com.gt/site/personas",
    "X-Requested-With": "XMLHttpRequest"
}
```

#### Specific Value Extraction

```python
if "compra_dolares_docto_bv" in data:
    rate = float(data["compra_dolares_docto_bv"])  # 7.59
    return rate
```

#### Authentication Headers
- `Referer`: Indicates where the request comes from
- `X-Requested-With: XMLHttpRequest`: Identifies AJAX requests
- `User-Agent`: Simulates a real browser

#### Hybrid Strategy
- API first (more reliable and faster)
- Fallback to web scraping if API fails

#### Tools Used

1. **curl** - For making HTTP requests and analyzing responses
2. **grep** - For searching patterns in HTML and JavaScript
3. **Manual analysis** - To understand JavaScript logic
4. **aiohttp** - To implement the asynchronous Python client

#### Final Result

The scraper now obtains the exchange rate for **Virtual Banking APP (Buy)** directly from Banrural's internal API, being much more efficient and reliable than traditional web scraping.
