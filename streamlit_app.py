import streamlit as st
import coloredlogs, logging
import pandas as pd

coloredlogs.install(level='INFO')
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title='Shop Canada',
    page_icon='🇨🇦',
    layout='wide',
)

st.title('Shop Canada 🇨🇦')

st.caption('Explore the top Canadian brands on Shopify 🍁')


logger.info('Loading data... 📚')
df = pd.read_csv('./data/shop_canada_data.csv')
df = df[df['title'].isin(['Casper', 'Blundstone Canada']) == False]  # remove non-CAN companies
logger.info('Data loaded successfully ✅')

logger.info('Parameter setup... 🛠️')
category_options = df.groupby('section_title').size().sort_values(ascending=False).index.tolist()
col1, col2 = st.columns(2)
with col1:
    search = st.text_input(
        '🔎 Search', 
        '',
        help='Search by brand, category, bio, or URL'
    )
with col2:
    categories = st.multiselect(
        'Categories',
        category_options,
        default=category_options,
        help='Filter by category (Home, Beauty, Women, Men, Baby & Toddler)'
    )


df.rename(
    columns={
        'section_title': 'Category',
        'title': 'Brand',
        'rating_and_volume': 'Rating (Volume)',
        'rating': 'Rating',
        'volume_of_ratings': 'Volume of Ratings',
        'bio': 'Bio',
        'url': 'Shopify Store URL',
        'shop_app_url': 'Shop App URL',
    },
    inplace=True
)


logger.info('Filtering data... 🔍')
filtered_df = df[df['Category'].isin(categories)]
if search != '':
    filtered_df = filtered_df[
        filtered_df['Brand'].str.contains(search, case=False) |
        filtered_df['Category'].str.contains(search, case=False) |
        filtered_df['Bio'].str.contains(search, case=False) |
        filtered_df['Shopify Store URL'].str.contains(search, case=False) |
        filtered_df['Shop App URL'].str.contains(search, case=False)
    ]
logger.info('Data filtered successfully ✅')

logger.info('Handle duplicates... 🧰')
dups = df.groupby('Shopify Store URL').size()
dups = dups[dups > 1]
df_w_dups = df[df['Shopify Store URL'].isin(dups.index)]
combined_sections = df_w_dups.groupby('Shopify Store URL')['Category'].agg(lambda x: ', '.join(x)).reset_index()
filtered_df = filtered_df.drop_duplicates(subset='Shopify Store URL', keep='first')
filtered_df = filtered_df.merge(combined_sections, on='Shopify Store URL', how='left', suffixes=('_singles', '_combined')) # keep new combined categories
filtered_df['Category'] = filtered_df['Category_combined'].fillna(filtered_df['Category_singles'])

viz_df = filtered_df[[
    'Brand', 'Volume of Ratings', 'Rating',
    'Category', 'Bio', 'Shopify Store URL', 'Shop App URL'
]].sort_values(by='Volume of Ratings', ascending=False)

viz_df.index = range(1, len(viz_df) + 1)



viz_df['Volume of Ratings'] = viz_df['Volume of Ratings'] / 1000

st.dataframe(
    viz_df, 
    column_config={
        'Shopify Store URL': st.column_config.LinkColumn(
            "Shopify Store URL",
            display_text="https://(.*?)/",
            help='URL of the Shopify store'
        ),
        'Shop App URL': st.column_config.LinkColumn(
            "Shop App URL",
            display_text="https://(.*?)/",
            help='URL of the Shop App page'
        ),
        'Volume of Ratings': st.column_config.ProgressColumn(
            "📊 Volume of Ratings",
            # format='%d',
            format="%.2fK",
            # format="{:,}",
            min_value=0,
            max_value=viz_df['Volume of Ratings'].max(),
            help='Volume of ratings in thousands (K) based on Shop App ratings.'
        ),
        'Rating': st.column_config.ProgressColumn(
            "⭐️ Rating",
            format='%.1f',
            min_value=0,
            max_value=5,
            help='Average rating based on Shop App ratings.'
        ),
        'Bio': st.column_config.TextColumn(
            "Bio",
            max_chars=500,
            help='Bio of the brand as listed on their Shop App page.'
        ),
        'Category': st.column_config.TextColumn(
            "Category",
            help='Category of the brand as its listed here: [Shop App Canada](https://shop.app/events/shop-canada)'
        ),
        'Brand': st.column_config.TextColumn(
            "Brand",
            help='Brand name as listed on their Shop App page.'
        ),
    },
    height=800
)


st.caption('📊 Data source: [Shop App Canada](https://shop.app/events/shop-canada)')
st.caption('🛠️ GitHub: [parker84/shop-canada](https://github.com/parker84/shop-canada)')