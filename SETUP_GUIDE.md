# Setup Guide for Techsiro Price Monitor

## Quick Start 🚀

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Playwright Browsers

```bash
playwright install chromium
```

**Note:** If you're in a restricted environment (Docker, cloud sandbox), Playwright may have issues. See the "Troubleshooting" section below.

### Step 3: Run the Application

```bash
python app.py
```

The server will start at `http://localhost:5000`

### Step 4: Open in Browser

Navigate to `http://localhost:5000` and start monitoring prices!

## Environment-Specific Setup

### For Local Development (Recommended)

If you're running on your local machine (Windows, Mac, or Linux desktop):

1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Install Playwright: `playwright install chromium`
4. Run: `python app.py`

This is the **best environment** for the scraper to work properly.

### For Docker/Cloud Environments

Playwright requires certain system dependencies. If you're in a containerized environment:

**Option 1: Use the requests-based scraper (No browser needed)**

The app automatically tries the simpler HTTP request method first, which works if:
- The website doesn't block bot traffic
- The price is in the initial HTML (not loaded by JavaScript)

**Option 2: Install system dependencies for Playwright**

```bash
# For Debian/Ubuntu-based systems
playwright install-deps chromium

# Then install browsers
playwright install chromium
```

**Option 3: Use Demo/Mock Mode**

If scraping doesn't work in your environment, you can:

1. Manually update `products.json` with price data
2. Or modify the scraper to return mock data for testing the UI

## Verifying the Installation

### Test the Scraper

Run this command to test if scraping works:

```bash
python scraper.py
```

You should see:
- If successful: Price extracted and displayed
- If 403 error: Website is blocking requests (see below)
- If browser crash: Playwright needs system dependencies

### Expected Output (Success)

```
Testing scraper with URL: https://techsiro.com/products/...
=== Testing requests method directly ===
Requests Result:
  Price: 63600000
  Price Text: ۶۳٬۶۰۰٬۰۰۰ تومان
  Status: success
```

## Troubleshooting Common Issues

### Issue 1: 403 Forbidden Error

**Problem:** Website blocks automated requests

**Solutions:**

1. **Add cookies/session** - The website may require a session. You can:
   - Visit the site in a browser first
   - Copy cookies using browser dev tools
   - Add them to the scraper

2. **Use a proxy** - Route requests through a proxy service

3. **Increase delays** - Add more time between requests

4. **Contact website** - For commercial use, contact techsiro.com for API access

### Issue 2: Playwright Browser Crashes

**Problem:** Browser fails to launch or crashes immediately

**Solutions:**

1. **Install system dependencies:**
   ```bash
   playwright install-deps chromium
   ```

2. **Run on a local machine** instead of a container

3. **Use the requests fallback** - The app will try this automatically

4. **Disable Playwright** - Modify `scraper.py` to only use requests method

### Issue 3: Price Not Found

**Problem:** Scraper runs but doesn't extract price

**Solutions:**

1. **Check the HTML structure** - Website may have changed

2. **Update selectors** - Modify the regex pattern in `scraper.py`:
   ```python
   persian_price_pattern = r'[\d۰-۹٬,]+\s*تومان'
   ```

3. **Manual testing** - Use `test_local_scraper.py` with saved HTML to debug

### Issue 4: SSL Certificate Errors

**Problem:** SSL verification fails

**Solution:** The app already disables SSL verification (`verify=False`). If you still see errors:

```python
# In scraper.py, this is already done:
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

## Production Deployment Tips

### Security

1. **Don't expose to internet** - This is for local use only
2. **Add authentication** - If you must expose it, add login
3. **Use environment variables** - Don't hardcode sensitive data
4. **Respect robots.txt** - Check site's scraping policy

### Performance

1. **Adjust refresh interval** - Don't set too low (min 5 seconds recommended)
2. **Use caching** - The app already caches prices in memory
3. **Database** - For production, replace JSON files with a database
4. **Queue system** - For many products, use a task queue (Celery, RQ)

### Reliability

1. **Error handling** - The app already handles most errors gracefully
2. **Retry logic** - Consider adding retries for failed requests
3. **Monitoring** - Set up alerts if scraping stops working
4. **Logging** - Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced Configuration

### Changing Scraping Behavior

Edit `scraper.py`:

```python
# Change timeout
page.set_default_timeout(30000)  # 30 seconds

# Change wait strategy
page.goto(url, wait_until='domcontentloaded')  # Faster
# or
page.goto(url, wait_until='networkidle')  # More reliable

# Change price filter threshold
if price_num and price_num > 100000:  # Only prices above 100,000
```

### Adding More Products

**Via UI:**
- Click "افزودن محصول جدید" (Add New Product)
- Enter name and URL
- Click "افزودن" (Add)

**Via JSON file:**
Edit `products.json`:
```json
[
  {
    "name": "Product Name",
    "url": "https://techsiro.com/products/..."
  }
]
```

### Customizing Alarm

1. **Change alarm sound:** Replace `alarm sound/mixkit-classic-alarm-995.wav`

2. **Change alarm trigger:** Edit `settings.json`:
   ```json
   {
     "target_price": 1000000,
     "alarm_enabled": true
   }
   ```

3. **Multiple price alerts:** Modify the frontend `checkPriceAlerts()` function

## Testing Without Real Scraping

For testing the UI without actual web scraping:

1. Edit `scraper.py` and modify `scrape_with_requests()`:

```python
def scrape_with_requests(self, url):
    # Mock data for testing
    import random
    return {
        'price': random.randint(50000000, 70000000),
        'price_text': 'مبلغ تستی',
        'status': 'success',
        'error': None
    }
```

2. Or manually edit `products.json` with mock prices

## Getting Help

If you're still having issues:

1. Check the full error message
2. Enable debug mode in Flask: `app.run(debug=True)`
3. Test each component separately:
   - Scraper: `python scraper.py`
   - Local HTML extraction: `python test_local_scraper.py`
   - Flask server: `python app.py`

## Next Steps

Once everything is working:

1. ✅ Configure your refresh interval (Settings panel)
2. ✅ Set your target price for alerts
3. ✅ Add products to monitor
4. ✅ Test the alarm system (set target to current price)
5. ✅ Leave it running in the background

Happy price monitoring! 🎯
