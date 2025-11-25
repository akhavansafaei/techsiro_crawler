"""
Flask backend for Techsiro Price Monitor
Provides API endpoints for product management and price monitoring
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import os
from threading import Thread, Lock
import time
from scraper import TechsiroScraper

app = Flask(__name__, static_folder='static')
CORS(app)

# File paths
PRODUCTS_FILE = 'products.json'
SETTINGS_FILE = 'settings.json'
ALARM_SOUND_PATH = 'alarm sound/mixkit-classic-alarm-995.wav'

# Thread-safe data storage
data_lock = Lock()
cached_prices = {}
scraper = TechsiroScraper()


def load_json_file(filepath, default=None):
    """Load JSON file with error handling"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
    return default if default is not None else []


def save_json_file(filepath, data):
    """Save data to JSON file with error handling"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filepath}: {e}")
        return False


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with their current prices"""
    products = load_json_file(PRODUCTS_FILE, [])

    # Add cached price information
    with data_lock:
        for product in products:
            url = product['url']
            if url in cached_prices:
                product.update(cached_prices[url])

    return jsonify({
        'success': True,
        'products': products
    })


@app.route('/api/products', methods=['POST'])
def add_product():
    """Add a new product to monitor"""
    data = request.json

    if not data or 'name' not in data or 'url' not in data:
        return jsonify({
            'success': False,
            'error': 'Name and URL are required'
        }), 400

    name = data['name'].strip()
    url = data['url'].strip()

    if not name or not url:
        return jsonify({
            'success': False,
            'error': 'Name and URL cannot be empty'
        }), 400

    # Validate URL is from techsiro.com
    if 'techsiro.com' not in url:
        return jsonify({
            'success': False,
            'error': 'URL must be from techsiro.com'
        }), 400

    products = load_json_file(PRODUCTS_FILE, [])

    # Check if URL already exists
    if any(p['url'] == url for p in products):
        return jsonify({
            'success': False,
            'error': 'Product URL already exists'
        }), 400

    # Add new product
    new_product = {
        'name': name,
        'url': url
    }

    products.append(new_product)

    if save_json_file(PRODUCTS_FILE, products):
        # Immediately scrape the new product
        try:
            price_data = scraper.scrape_product_price(url)
            with data_lock:
                cached_prices[url] = {
                    'price': price_data['price'],
                    'price_text': price_data['price_text'],
                    'status': price_data['status'],
                    'error': price_data['error'],
                    'last_updated': time.time()
                }
            new_product.update(cached_prices[url])
        except Exception as e:
            print(f"Error scraping new product: {e}")

        return jsonify({
            'success': True,
            'product': new_product
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to save product'
        }), 500


@app.route('/api/products/<int:index>', methods=['DELETE'])
def delete_product(index):
    """Delete a product by index"""
    products = load_json_file(PRODUCTS_FILE, [])

    if index < 0 or index >= len(products):
        return jsonify({
            'success': False,
            'error': 'Invalid product index'
        }), 400

    deleted_product = products.pop(index)

    if save_json_file(PRODUCTS_FILE, products):
        # Remove from cache
        with data_lock:
            if deleted_product['url'] in cached_prices:
                del cached_prices[deleted_product['url']]

        return jsonify({
            'success': True,
            'deleted': deleted_product
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to delete product'
        }), 500


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    settings = load_json_file(SETTINGS_FILE, {
        'refresh_interval': 30,
        'target_price': 1000000,
        'alarm_enabled': True
    })

    return jsonify({
        'success': True,
        'settings': settings
    })


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update settings"""
    data = request.json

    if not data:
        return jsonify({
            'success': False,
            'error': 'No data provided'
        }), 400

    settings = load_json_file(SETTINGS_FILE, {})

    # Update only provided fields
    if 'refresh_interval' in data:
        try:
            interval = int(data['refresh_interval'])
            if interval < 5:
                return jsonify({
                    'success': False,
                    'error': 'Refresh interval must be at least 5 seconds'
                }), 400
            settings['refresh_interval'] = interval
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid refresh interval'
            }), 400

    if 'target_price' in data:
        try:
            settings['target_price'] = int(data['target_price'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid target price'
            }), 400

    if 'alarm_enabled' in data:
        settings['alarm_enabled'] = bool(data['alarm_enabled'])

    if save_json_file(SETTINGS_FILE, settings):
        return jsonify({
            'success': True,
            'settings': settings
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to save settings'
        }), 500


@app.route('/api/scrape', methods=['POST'])
def manual_scrape():
    """Manually trigger a scrape of all products"""
    products = load_json_file(PRODUCTS_FILE, [])

    if not products:
        return jsonify({
            'success': False,
            'error': 'No products to scrape'
        }), 400

    # Scrape in background thread
    def scrape_task():
        results = scraper.scrape_multiple_products(products)
        with data_lock:
            for result in results:
                cached_prices[result['url']] = {
                    'price': result['price'],
                    'price_text': result['price_text'],
                    'status': result['status'],
                    'error': result['error'],
                    'last_updated': result['last_updated']
                }

    thread = Thread(target=scrape_task)
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'message': 'Scraping started'
    })


@app.route('/alarm-sound')
def get_alarm_sound():
    """Serve the alarm sound file"""
    return send_from_directory('alarm sound', 'mixkit-classic-alarm-995.wav')


def background_scraper():
    """Background thread to periodically scrape prices"""
    while True:
        try:
            settings = load_json_file(SETTINGS_FILE, {'refresh_interval': 30})
            interval = settings.get('refresh_interval', 30)

            products = load_json_file(PRODUCTS_FILE, [])

            if products:
                print(f"Background scraper: Checking {len(products)} products...")
                results = scraper.scrape_multiple_products(products)

                with data_lock:
                    for result in results:
                        cached_prices[result['url']] = {
                            'price': result['price'],
                            'price_text': result['price_text'],
                            'status': result['status'],
                            'error': result['error'],
                            'last_updated': result['last_updated']
                        }

                        # Log if price matches target
                        if result['price']:
                            target_price = settings.get('target_price', 1000000)
                            if result['price'] == target_price:
                                print(f"🚨 ALERT: {result['name']} reached target price: {result['price_text']}")

            time.sleep(interval)

        except Exception as e:
            print(f"Background scraper error: {e}")
            time.sleep(30)  # Wait before retrying


if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)

    # Start background scraper thread
    scraper_thread = Thread(target=background_scraper, daemon=True)
    scraper_thread.start()

    # Run Flask app
    print("Starting Techsiro Price Monitor...")
    print("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
