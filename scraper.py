"""
Advanced web scraper for Techsiro.com using Playwright with BeautifulSoup fallback
Handles JavaScript-rendered pages
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TechsiroScraper:
    def __init__(self):
        self.persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')

    def convert_persian_to_english(self, text):
        """Convert Persian/Arabic numerals to English numerals"""
        return text.translate(self.persian_to_english)

    def extract_price(self, price_text):
        """Extract numeric price from Persian text"""
        # Convert Persian numerals to English
        english_text = self.convert_persian_to_english(price_text)
        # Remove commas and extract numbers
        numbers = re.sub(r'[^\d]', '', english_text)
        try:
            return int(numbers) if numbers else None
        except ValueError:
            return None

    def scrape_with_requests(self, url):
        """
        Simple scraper using requests and BeautifulSoup
        This works if the price is in the initial HTML
        """
        result = {
            'price': None,
            'price_text': None,
            'status': 'error',
            'error': None
        }

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()

            html_content = response.text

            # Use regex to find price patterns
            persian_price_pattern = r'[\d۰-۹٬,]+\s*تومان'
            matches = re.findall(persian_price_pattern, html_content)

            if matches:
                # Find all prices and get the largest one
                prices = []
                for match in matches:
                    price_num = self.extract_price(match)
                    if price_num and price_num > 100000:  # Filter out small numbers
                        prices.append((price_num, match))

                if prices:
                    # Get the largest price (usually the main product price)
                    prices.sort(key=lambda x: x[0], reverse=True)
                    result['price'] = prices[0][0]
                    result['price_text'] = prices[0][1].strip()
                    result['status'] = 'success'
                else:
                    result['error'] = 'No valid price found in HTML'
                    result['status'] = 'not_found'
            else:
                result['error'] = 'No price pattern found in HTML'
                result['status'] = 'not_found'

        except requests.RequestException as e:
            result['error'] = f'HTTP request error: {str(e)}'
            result['status'] = 'error'
        except Exception as e:
            result['error'] = f'Error: {str(e)}'
            result['status'] = 'error'

        return result

    def scrape_product_price(self, url):
        """
        Scrape product price from Techsiro.com
        First tries simple requests, falls back to Playwright if needed
        Returns: dict with price and status
        """
        # Try simple requests first (faster and more reliable)
        print(f"  Trying simple HTTP request...")
        result = self.scrape_with_requests(url)

        if result['status'] == 'success':
            return result

        # If simple method failed, try Playwright
        print(f"  Simple request failed, trying Playwright...")
        result = {
            'price': None,
            'price_text': None,
            'status': 'error',
            'error': None
        }

        try:
            with sync_playwright() as p:
                # Launch browser in headless mode with additional args
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-software-rasterizer',
                        '--disable-extensions'
                    ]
                )
                context = browser.new_context(
                    locale='fa-IR',
                    timezone_id='Asia/Tehran',
                    ignore_https_errors=True  # Ignore SSL certificate errors
                )
                page = context.new_page()

                # Set timeout
                page.set_default_timeout(30000)

                # Navigate to product page
                page.goto(url, wait_until='domcontentloaded')

                # Wait a bit for JavaScript to execute
                page.wait_for_timeout(3000)

                # Wait for the price element to be visible
                # The price is typically in a button or div with "تومان" text
                try:
                    # Get page content and search for price
                    content = page.content()

                    # Use regex to find price pattern in Persian
                    import re
                    # Look for patterns like: ۶۳٬۶۰۰٬۰۰۰ تومان or with English numbers
                    persian_price_pattern = r'[\d۰-۹٬,]+\s*تومان'
                    matches = re.findall(persian_price_pattern, content)

                    if matches:
                        # Find the largest price (likely the product price, not shipping/warranty)
                        prices = []
                        for match in matches:
                            price_num = self.extract_price(match)
                            if price_num and price_num > 10000:  # Filter out small numbers
                                prices.append((price_num, match))

                        if prices:
                            # Get the largest price
                            prices.sort(key=lambda x: x[0], reverse=True)
                            result['price'] = prices[0][0]
                            result['price_text'] = prices[0][1].strip()
                            result['status'] = 'success'
                        else:
                            result['error'] = 'No valid price found'
                            result['status'] = 'not_found'
                    else:
                        # Try with button selector as fallback
                        try:
                            price_element = page.query_selector('button:has-text("تومان")')
                            if not price_element:
                                price_element = page.query_selector('div:has-text("تومان")')

                            if price_element:
                                price_text = price_element.text_content()
                                result['price_text'] = price_text.strip()
                                result['price'] = self.extract_price(price_text)
                                result['status'] = 'success'
                            else:
                                result['error'] = 'Price element not found'
                                result['status'] = 'not_found'
                        except:
                            result['error'] = 'Price element not found'
                            result['status'] = 'not_found'

                except PlaywrightTimeout:
                    result['error'] = 'Timeout waiting for price element'
                    result['status'] = 'timeout'

                except Exception as e:
                    result['error'] = f'Error finding price: {str(e)}'
                    result['status'] = 'error'

                finally:
                    browser.close()

        except Exception as e:
            result['error'] = f'Browser error: {str(e)}'
            result['status'] = 'error'

        return result

    def scrape_multiple_products(self, products):
        """
        Scrape prices for multiple products
        products: list of dicts with 'name' and 'url'
        Returns: list of products with added price information
        """
        results = []

        for product in products:
            print(f"Scraping: {product['name']}")
            price_data = self.scrape_product_price(product['url'])

            result = {
                'name': product['name'],
                'url': product['url'],
                'price': price_data['price'],
                'price_text': price_data['price_text'],
                'status': price_data['status'],
                'error': price_data['error'],
                'last_updated': time.time()
            }

            results.append(result)

            # Small delay between requests to be polite
            time.sleep(1)

        return results


if __name__ == '__main__':
    # Test the scraper
    scraper = TechsiroScraper()

    test_url = "https://techsiro.com/products/4804/microsoft-xbox-series-x-digital-1tb-robot-white"

    print(f"Testing scraper with URL: {test_url}")
    print(f"\n=== Testing requests method directly ===")
    requests_result = scraper.scrape_with_requests(test_url)
    print(f"Requests Result:")
    print(f"  Price: {requests_result['price']}")
    print(f"  Price Text: {requests_result['price_text']}")
    print(f"  Status: {requests_result['status']}")
    if requests_result['error']:
        print(f"  Error: {requests_result['error']}")

    print(f"\n=== Testing full scrape_product_price method ===")
    result = scraper.scrape_product_price(test_url)

    print(f"\nFinal Result:")
    print(f"  Price: {result['price']}")
    print(f"  Price Text: {result['price_text']}")
    print(f"  Status: {result['status']}")
    if result['error']:
        print(f"  Error: {result['error']}")
