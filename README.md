# 🛒 Techsiro Price Monitor

A real-time price monitoring application for techsiro.com products with alarm notifications.

## Features

✅ **Real-time Price Monitoring**: Automatically fetches and displays current prices from techsiro.com
✅ **Adjustable Refresh Interval**: Set custom update intervals (in seconds)
✅ **Price Alerts**: Loud alarm when products reach your target price
✅ **Manual Product Addition**: Add new products directly from the UI
✅ **Customizable Target Price**: Set and adjust your desired price threshold
✅ **Persian Language Support**: Full RTL support with Persian numbers
✅ **Beautiful UI**: Modern, responsive design with real-time updates

## Installation

1. Install dependencies:
```bash
npm install
```

## Usage

1. Start the server:
```bash
npm start
```

2. Open your browser and navigate to:
```
http://localhost:3000
```

3. The app will automatically start monitoring the products listed in `products.json`

## How to Use

### Monitoring Products
- Products are automatically fetched and displayed
- Prices update every X seconds (default: 10 seconds)
- Current prices are shown in large, easy-to-read format

### Adjusting Settings
1. **Refresh Interval**: Change the "بازه زمانی بروزرسانی" value (in seconds)
2. **Target Price**: Set your desired price in the "قیمت هدف" field (e.g., ۱٬۰۰۰٬۰۰۰)
3. Click "اعمال تنظیمات" to apply changes

### Adding New Products
1. Enter the product name in "نام محصول"
2. Enter the techsiro.com product URL in "آدرس محصول"
3. Click "افزودن محصول"

Example:
- **Name**: کنسول بازی ایکس باکس سری ایکس
- **URL**: https://techsiro.com/products/4804/microsoft-xbox-series-x-digital-1tb-robot-white

### Price Alarm
- When any product reaches your target price, a loud alarm will sound
- A visual indicator will appear at the top of the page
- Click "خاموش کردن آلارم" to stop the alarm
- The alarm will repeat continuously until manually stopped

## File Structure

```
techsiro_crawler/
├── server.js              # Backend Express server
├── package.json           # Node.js dependencies
├── products.json          # Product list (name & URL)
├── public/
│   ├── index.html        # Frontend UI
│   └── alarm.wav         # Alarm sound file
└── README.md             # This file
```

## API Endpoints

- `GET /api/products` - Get all products
- `GET /api/prices` - Get current prices for all products
- `GET /api/price/:index` - Get price for a specific product
- `POST /api/products` - Add a new product
- `DELETE /api/products/:index` - Delete a product

## Configuration

### Adding Products Manually to JSON
Edit `products.json`:
```json
[
  {
    "name": "محصول اول",
    "url": "https://techsiro.com/products/..."
  },
  {
    "name": "محصول دوم",
    "url": "https://techsiro.com/products/..."
  }
]
```

### Default Settings
- **Refresh Interval**: 10 seconds
- **Target Price**: ۱٬۰۰۰٬۰۰۰ تومان (1,000,000 Toman)
- **Port**: 3000

## Troubleshooting

### Prices Not Showing
- Check your internet connection
- Verify the product URLs are correct and accessible
- techsiro.com may have changed their page structure

### Alarm Not Playing
- Ensure your browser allows audio playback
- Check that `alarm.wav` exists in the `public` folder
- Some browsers require user interaction before playing audio

## Development

Run with auto-reload:
```bash
npm run dev
```

## Notes

- All products must be from techsiro.com
- Prices are scraped in real-time from the actual product pages
- The app uses Persian number formatting for display
- Supports both Persian (۰-۹) and Arabic (٠-٩) numerals in input

## License

MIT
