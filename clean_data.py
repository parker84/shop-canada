import json
import pandas as pd
import json
import logging
import coloredlogs

# Set up colored logs
coloredlogs.install(level='INFO')

# Create a logger
logger = logging.getLogger(__name__)

logger.info('Reading raw JSON data... 📚')
raw_json = json.load(open('shop_canada_data.json'))
logger.info('Raw JSON data read successfully ✅')

logger.info('Flattening JSON data... 📏')
# Flatten the JSON data
flattened_data = []
for section in raw_json.values():
    for brand in section['details_per_brand']:
        flattened_data.append({
            'section_title': section['section_title'],
            'title': brand['title'],
            'rating_and_volume': brand['rating'],
            'rating': brand['rating'].split('(')[0],
            'volume_of_ratings': brand['volume_of_ratings'],
            'bio': brand['bio'],
            'url': brand['url'],
            'shop_app_url': brand['shop_app_url']
        })
logger.info('JSON data flattened successfully ✅')

logger.info('Converting flattened data to a DataFrame... 📊')
# Convert the flattened data to a DataFrame
df = pd.DataFrame(flattened_data)
logger.info('Data converted to a DataFrame successfully ✅')

logger.info('Saving to a CSV file... 📂')
# Save the DataFrame to a CSV file
df.to_csv('shop_canada_data.csv', index=False)
logger.info('Data saved to shop_canada_data.csv ✅')

logger.info('Data cleaning complete! 🎉')