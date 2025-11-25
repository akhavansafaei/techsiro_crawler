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

    // Target the specific structure used by techsiro.com
    // Look for <p> elements with "font-bold" class that contain "تومان"
    // Skip elements with "line-through" class (old prices)
    let price = null;

    $('p').each((i, elem) => {
      const $elem = $(elem);
      const elemClass = $elem.attr('class') || '';
      const text = $elem.text().trim();

      // Skip if this is a line-through price (old price)
      if (elemClass.includes('line-through')) {
        return;
      }

      // Skip if text contains discount/savings indicators
      if (text.includes('سود') || text.includes('تخفیف') || text.includes('discount')) {
        return;
      }

      // Look for bold prices with "تومان"
      if (elemClass.includes('font-bold') && text.includes('تومان')) {
        const priceMatch = text.match(/([۰-۹0-9٬,]+)\s*تومان/);
        if (priceMatch) {
          const priceText = priceMatch[1];
          const priceNum = parseInt(toEnglishNumber(priceText));

          // Only consider valid prices
          if (priceNum > 1000) {
            price = priceText;
            return false; // Stop iteration, we found the main price
          }
        }
      }
    });

    if (!price) {
      return null;
    }

    // Remove commas from the price text before returning
    return price.replace(/[٬,]/g, '');

  } catch (error) {
    console.error(`Error scraping ${url}:`, error.message);
    return null;
  }
}

// Helper function to convert Persian/Arabic numerals to English (moved up for use in scrapePrice)
function toEnglishNumber(str) {
  const persianNumbers = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  const arabicNumbers = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];

  let result = str;
  persianNumbers.forEach((num, idx) => {
    result = result.replace(new RegExp(num, 'g'), idx.toString());
  });
  arabicNumbers.forEach((num, idx) => {
    result = result.replace(new RegExp(num, 'g'), idx.toString());
  });

  // Remove commas and other non-numeric characters
  result = result.replace(/[^0-9]/g, '');

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
