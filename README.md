# Exchange Rate Bot 🏦

A Telegram bot that provides real-time exchange rates and currency conversion functionality. Get current exchange rates for popular currencies and convert between different currencies with simple commands.

## Features

- 💱 **Real-time Exchange Rates**: Get up-to-date exchange rates for major currencies
- 🔄 **Currency Conversion**: Convert amounts between different currencies
- 🌍 **Multiple Currencies**: Supports USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY, and many more
- 🚀 **Easy to Use**: Simple commands with clear formatting
- 📱 **Telegram Integration**: Works seamlessly in Telegram chats

## Bot Commands

- `/start` - Welcome message and basic information
- `/rates [currency]` - Get exchange rates (default: USD base)
- `/convert <amount> <from> <to>` - Convert between currencies
- `/help` - Show help and usage examples

## Usage Examples

```
/rates                    # Shows popular currencies vs USD
/rates EUR               # Shows all currencies vs EUR
/convert 100 USD EUR     # Converts 100 USD to EUR
/convert 50 GBP JPY      # Converts 50 GBP to Japanese Yen
```

## Setup

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rodrigodeleonv/exchange-rate-bot.git
   cd exchange-rate-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

4. **Configure your bot token:**
   Edit the `.env` file and add your Telegram Bot Token:
   ```
   TELEGRAM_BOT_TOKEN=your_actual_bot_token_here
   ```

### Getting a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Start a chat with BotFather and send `/newbot`
3. Follow the instructions to create your bot
4. Copy the bot token and add it to your `.env` file

### Running the Bot

```bash
python bot.py
```

The bot will start and show a message indicating it's running. Press `Ctrl+C` to stop.

## Docker Support (Optional)

You can also run the bot using Docker:

1. **Build the image:**
   ```bash
   docker build -t exchange-rate-bot .
   ```

2. **Run the container:**
   ```bash
   docker run -d --env-file .env exchange-rate-bot
   ```

## API Information

This bot uses the free [ExchangeRate-API](https://exchangerate-api.com/) service for fetching real-time exchange rates. The free tier provides:

- ✅ 1,500 requests per month
- ✅ Real-time exchange rates
- ✅ No authentication required
- ✅ 160+ supported currencies

## Supported Currencies

The bot supports all major world currencies including:

**Popular currencies:** USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY

**All supported currencies:** AED, AFN, ALL, AMD, ANG, AOA, ARS, AUD, AWG, AZN, BAM, BBD, BDT, BGN, BHD, BIF, BMD, BND, BOB, BRL, BSD, BTN, BWP, BYN, BZD, CAD, CDF, CHF, CLP, CNY, COP, CRC, CUC, CUP, CVE, CZK, DJF, DKK, DOP, DZD, EGP, ERN, ETB, EUR, FJD, FKP, GBP, GEL, GGP, GHS, GIP, GMD, GNF, GTQ, GYD, HKD, HNL, HRK, HTG, HUF, IDR, ILS, IMP, INR, IQD, IRR, ISK, JEP, JMD, JOD, JPY, KES, KGS, KHR, KMF, KPW, KRW, KWD, KYD, KZT, LAK, LBP, LKR, LRD, LSL, LYD, MAD, MDL, MGA, MKD, MMK, MNT, MOP, MRU, MUR, MVR, MWK, MXN, MYR, MZN, NAD, NGN, NIO, NOK, NPR, NZD, OMR, PAB, PEN, PGK, PHP, PKR, PLN, PYG, QAR, RON, RSD, RUB, RWF, SAR, SBD, SCR, SDG, SEK, SGD, SHP, SLE, SLL, SOS, SRD, STN, SVC, SYP, SZL, THB, TJS, TMT, TND, TOP, TRY, TTD, TUT, TVD, TWD, TZS, UAH, UGX, USD, UYU, UZS, VED, VES, VND, VUV, WST, XAF, XAG, XAU, XCD, XDR, XOF, XPD, XPF, XPT, YER, ZAR, ZMW, ZWL

## Error Handling

The bot includes comprehensive error handling for:

- Invalid currency codes
- Network connectivity issues
- Invalid conversion amounts
- API rate limiting
- Malformed commands

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions:

1. Check the existing [Issues](https://github.com/rodrigodeleonv/exchange-rate-bot/issues)
2. Create a new issue if your problem isn't already reported
3. Include error messages and steps to reproduce the issue