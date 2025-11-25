# Techsiro Price Monitor 🔍

A powerful web application to monitor product prices from Techsiro.com with automatic alerts and real-time updates.

## Features ✨

- **Real-time Price Monitoring**: Automatically scrapes and updates product prices every X seconds
- **Adjustable Refresh Interval**: Configure how often prices are checked (minimum 5 seconds)
- **Manual Product Addition**: Add new products directly from the UI
- **Price Alerts**: Set a target price and get loud audio alarms when reached
- **Customizable Target Price**: Adjust the alert price threshold anytime
- **Persian Language Support**: Full RTL interface with Persian numerals
- **Advanced Scraping**: Uses Playwright for JavaScript-rendered pages
- **Auto-refresh UI**: Products update automatically without page reload
- **Delete Products**: Remove products from monitoring

## Requirements 📋

- Python 3.8+
- Modern web browser (Chrome, Firefox, Edge)

## Installation 🚀

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

This downloads the Chromium browser needed for web scraping.

## Usage 🎯

### 1. Start the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 2. Open in Browser

Navigate to `http://localhost:5000` in your web browser.

### 3. Configure Settings

- **Refresh Interval**: Set how often (in seconds) prices are checked
- **Target Price**: Set the price threshold for alarms (in Toman)
- Click "ذخیره تنظیمات" (Save Settings) to apply

### 4. Add Products

1. Enter the product name in Persian
2. Enter the full URL from techsiro.com
3. Click "افزودن" (Add)

Example:
- Name: `کنسول بازی ایکس باکس سری ایکس ( Xbox Series X Digital ) سفید - ظرفیت 1TB`
- URL: `https://techsiro.com/products/4804/microsoft-xbox-series-x-digital-1tb-robot-white`

### 5. Monitor Prices

- Products are automatically scraped at the configured interval
- Prices update in real-time on the UI
- When a price reaches exactly the target price (default: ۱٬۰۰۰٬۰۰۰ تومان), an alarm sounds
- Click "خاموش کردن هشدار" (Turn Off Alarm) to stop the alarm

### 6. Manual Refresh

Click "بروزرسانی دستی" (Manual Update) to immediately scrape all products.

## Project Structure 📁

```
techsiro_crawler/
├── app.py                      # Flask backend server
├── scraper.py                  # Playwright-based web scraper
├── requirements.txt            # Python dependencies
├── products.json              # Product database (auto-managed)
├── settings.json              # Application settings (auto-managed)
├── static/
│   └── index.html             # Frontend UI
├── alarm sound/
│   └── mixkit-classic-alarm-995.wav  # Alarm sound file
└── sample to helo u build price monitor/
    └── ...                    # Sample HTML for development
```

## API Endpoints 🔌

The Flask backend provides these REST API endpoints:

- `GET /` - Serve frontend HTML
- `GET /api/products` - Get all products with current prices
- `POST /api/products` - Add a new product
- `DELETE /api/products/<index>` - Delete a product
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings
- `POST /api/scrape` - Manually trigger price scraping
- `GET /alarm-sound` - Serve alarm audio file

## Configuration Files 📝

### products.json
Stores the list of products to monitor:

```json
[
  {
    "name": "Product Name",
    "url": "https://techsiro.com/products/..."
  }
]
```

### settings.json
Stores application settings:

```json
{
  "refresh_interval": 30,
  "target_price": 1000000,
  "alarm_enabled": true
}
```

## How It Works 🔧

1. **Backend** (Flask + Playwright):
   - Background thread periodically scrapes product prices
   - Uses Playwright to handle JavaScript-rendered pages
   - Caches prices in memory for fast API responses
   - Converts Persian numerals to English for processing

2. **Frontend** (HTML + JavaScript):
   - Auto-refreshes product list at configured interval
   - Displays prices in Persian format with thousand separators
   - Plays alarm sound when target price is reached
   - Provides intuitive UI for managing products and settings

3. **Scraping Strategy**:
   - Launches headless Chromium browser
   - Waits for page to fully load (networkidle)
   - Searches for price elements containing "تومان"
   - Extracts and parses Persian numerals
   - Handles timeouts and errors gracefully

## Troubleshooting 🔧

### Playwright Installation Issues

If you get errors about missing browsers:

```bash
playwright install chromium
```

### Port Already in Use

If port 5000 is busy, edit `app.py` and change:

```python
app.run(host='0.0.0.0', port=5000, ...)
```

to a different port number.

### Scraping Failures

- Check your internet connection
- Verify the product URL is correct and from techsiro.com
- The site might be blocking automated requests (rare)
- Try increasing the timeout in `scraper.py`

### Alarm Not Playing

- Check browser permissions for audio
- Some browsers require user interaction before playing audio
- Ensure the alarm sound file exists in `alarm sound/` directory

## Advanced Usage 💡

### Changing Alarm Sound

Replace `alarm sound/mixkit-classic-alarm-995.wav` with your own WAV file (keep the same filename).

### Custom Scraping Logic

Edit `scraper.py` to customize how prices are extracted. The current implementation looks for elements containing "تومان" text.

### Background Scraping

The app runs a background thread that continuously monitors prices. You can adjust the logic in `app.py`'s `background_scraper()` function.

## Security Notes 🔒

- This app is designed for **local use only**
- Don't expose it to the internet without proper authentication
- Be respectful with scraping frequency to avoid overloading the target website
- Default minimum interval is 5 seconds

## License 📄

This is a personal project for educational and monitoring purposes.

## Support 💬

For issues or questions, please check:
- The troubleshooting section above
- Playwright documentation: https://playwright.dev/
- Flask documentation: https://flask.palletsprojects.com/

---

Made with ❤️ for monitoring Techsiro.com prices
