const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Path to products JSON file
const PRODUCTS_FILE = path.join(__dirname, 'products.json');

// Function to scrape price from techsiro.com product page
async function scrapePrice(url) {
  try {
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000
    });

    const $ = cheerio.load(response.data);

    // Try multiple selectors to find the price
    let price = null;

    // Look for price in common patterns
    // Method 1: Look for price with "تومان" text
    $('*').each((i, elem) => {
      const text = $(elem).text().trim();
      // Match Persian numbers with commas followed by تومان
      const priceMatch = text.match(/([۰-۹0-9٬,]+)\s*تومان/);
      if (priceMatch && !price) {
        // Get the largest number (main price, not additional fees)
        const priceText = priceMatch[1];
        // Only consider it if it's a standalone price element (not in a paragraph with lots of text)
        if (text.length < 100 && priceText.length > 5) {
          price = priceText;
        }
      }
    });

    // Method 2: Look for specific price classes or IDs (if Method 1 fails)
    if (!price) {
      const priceSelectors = [
        '.product-price',
        '.price',
        '#product-price',
        '[class*="price"]',
        '[id*="price"]'
      ];

      for (const selector of priceSelectors) {
        const elem = $(selector).first();
        if (elem.length) {
          const text = elem.text().trim();
          const priceMatch = text.match(/([۰-۹0-9٬,]+)\s*تومان/);
          if (priceMatch) {
            price = priceMatch[1];
            break;
          }
        }
      }
    }

    return price;
  } catch (error) {
    console.error(`Error scraping ${url}:`, error.message);
    return null;
  }
}

// Helper function to convert Persian/Arabic numerals to English
function convertToEnglishNumbers(str) {
  const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const arabicNumbers = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];

  let result = str;
  persianNumbers.forEach((num, idx) => {
    result = result.replace(new RegExp(num, 'g'), idx.toString());
  });
  arabicNumbers.forEach((num, idx) => {
    result = result.replace(new RegExp(num, 'g'), idx.toString());
  });

  return result;
}

// Helper function to convert number to Persian format with commas
function toPersianNumber(num) {
  const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const numStr = num.toString();

  // Add commas
  const withCommas = numStr.replace(/\B(?=(\d{3})+(?!\d))/g, '٬');

  // Convert to Persian digits
  return withCommas.split('').map(char => {
    if (char >= '0' && char <= '9') {
      return persianDigits[parseInt(char)];
    }
    return char;
  }).join('');
}

// API endpoint to get all products with current prices
app.get('/api/products', async (req, res) => {
  try {
    const data = await fs.readFile(PRODUCTS_FILE, 'utf8');
    const products = JSON.parse(data);
    res.json(products);
  } catch (error) {
    console.error('Error reading products:', error);
    res.status(500).json({ error: 'Failed to read products' });
  }
});

// API endpoint to get price for a specific product
app.get('/api/price/:index', async (req, res) => {
  try {
    const index = parseInt(req.params.index);
    const data = await fs.readFile(PRODUCTS_FILE, 'utf8');
    const products = JSON.parse(data);

    if (index < 0 || index >= products.length) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const product = products[index];
    const price = await scrapePrice(product.url);

    res.json({
      name: product.name,
      url: product.url,
      price: price,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error fetching price:', error);
    res.status(500).json({ error: 'Failed to fetch price' });
  }
});

// API endpoint to get all prices at once
app.get('/api/prices', async (req, res) => {
  try {
    const data = await fs.readFile(PRODUCTS_FILE, 'utf8');
    const products = JSON.parse(data);

    const pricesPromises = products.map(async (product, index) => {
      const price = await scrapePrice(product.url);
      return {
        index,
        name: product.name,
        url: product.url,
        price: price,
        timestamp: new Date().toISOString()
      };
    });

    const prices = await Promise.all(pricesPromises);
    res.json(prices);
  } catch (error) {
    console.error('Error fetching prices:', error);
    res.status(500).json({ error: 'Failed to fetch prices' });
  }
});

// API endpoint to add a new product
app.post('/api/products', async (req, res) => {
  try {
    const { name, url } = req.body;

    if (!name || !url) {
      return res.status(400).json({ error: 'Name and URL are required' });
    }

    // Validate URL is from techsiro.com
    if (!url.includes('techsiro.com')) {
      return res.status(400).json({ error: 'URL must be from techsiro.com' });
    }

    const data = await fs.readFile(PRODUCTS_FILE, 'utf8');
    const products = JSON.parse(data);

    products.push({ name, url });

    await fs.writeFile(PRODUCTS_FILE, JSON.stringify(products, null, 2));

    res.json({ success: true, product: { name, url } });
  } catch (error) {
    console.error('Error adding product:', error);
    res.status(500).json({ error: 'Failed to add product' });
  }
});

// API endpoint to delete a product
app.delete('/api/products/:index', async (req, res) => {
  try {
    const index = parseInt(req.params.index);
    const data = await fs.readFile(PRODUCTS_FILE, 'utf8');
    const products = JSON.parse(data);

    if (index < 0 || index >= products.length) {
      return res.status(404).json({ error: 'Product not found' });
    }

    const deleted = products.splice(index, 1);

    await fs.writeFile(PRODUCTS_FILE, JSON.stringify(products, null, 2));

    res.json({ success: true, deleted: deleted[0] });
  } catch (error) {
    console.error('Error deleting product:', error);
    res.status(500).json({ error: 'Failed to delete product' });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 Techsiro Price Monitor Server running at http://localhost:${PORT}`);
  console.log(`📊 API available at http://localhost:${PORT}/api/products`);
});
