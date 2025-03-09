import streamlit as st
import coloredlogs, logging
import pandas as pd
from plotly import express as px

coloredlogs.install(level='INFO')
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title='Shop Canada',
    page_icon='🇨🇦',
    layout='wide',
)

st.title('Shop Canada 🇨🇦')

st.caption('Explore the top Canadian brands on Shopify 🍁')

# with st.sidebar.expander('⚙️ Parameters', expanded=False):
#     eb_alpha = st.number_input(
#         'Empirical Bayes Smoothing Alpha',
#         min_value=0.0,
#         max_value=1000.0,
#         value=100.0,
#         step=1.0,
#         format='%.1f',
#         help='Smoothing factor for the ratings'
#     )

logger.info('Loading data... 📚')
df = pd.read_csv('./data/shop_canada_data.csv')
df = df[df['title'].isin(['Casper', 'Blundstone Canada']) == False]  # remove non-CAN companies
logger.info('Data loaded successfully ✅')

logger.info('Parameter setup... 🛠️')
category_options = df.groupby('section_title').size().sort_values(ascending=False).index.tolist()
col1, col2 = st.columns(2)
with col1:
    search = st.text_input('🔎 Search', '')
with col2:
    categories = st.multiselect(
        'Categories',
        category_options,
        default=category_options
    )

# logger.info('Emp Bayes Smoothing the ratings... 🧬')
# # learn more about empirical bayes here: https://drob.gumroad.com/l/empirical-bayes
# global_mean = df['rating'].mean()
# df['eb_rating'] = (
#     (df['rating'] * (df['volume_of_ratings'] / (df['volume_of_ratings'] + eb_alpha))) +
#     (global_mean * (eb_alpha / (df['volume_of_ratings'] + eb_alpha)))
# )
# logger.info('Ratings smoothed successfully ✅')

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
        # 'eb_rating': 'Rating (eb)'
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
    'Brand', 'Volume of Ratings', 'Rating', #'Rating (eb)', 
    'Category', 'Bio', 'Shopify Store URL', 'Shop App URL'
]].sort_values(by='Volume of Ratings', ascending=False)

viz_df.index = range(1, len(viz_df) + 1)



viz_df['Volume of Ratings'] = viz_df['Volume of Ratings'] / 1000
# viz_df['Volume of Ratings'] = viz_df['Volume of Ratings'].apply(lambda x: f"{x:,}")

st.dataframe(
    viz_df, 
    column_config={
        'Shopify Store URL': st.column_config.LinkColumn(
            "Shopify Store URL",
            display_text="https://(.*?)/"
        ),
        'Shop App URL': st.column_config.LinkColumn(
            "Shop App URL",
            display_text="https://(.*?)/"
        ),
        'Volume of Ratings': st.column_config.ProgressColumn(
            "Volume of Ratings",
            # format='%d',
            format="%.2fK",
            # format="{:,}",
            min_value=0,
            max_value=viz_df['Volume of Ratings'].max()
        ),
        'Rating': st.column_config.ProgressColumn(
            "Rating",
            format='%.1f',
            min_value=0,
            max_value=5
        ),
        # 'Rating (eb)': st.column_config.ProgressColumn(
        #     "Rating (eb)",
        #     min_value=0,
        #     max_value=5
        # ),
        'Bio': st.column_config.TextColumn(
            "Bio",
            max_chars=100
        )
    },
    height=800
)

# with st.expander('📊 Visualize Empirical Bayes Smoothing', expanded=False):
#     heat_map_df = df[['Rating', 'Rating (eb)', 'Volume of Ratings', 'Brand']]
#     heat_map_df = heat_map_df[heat_map_df['Rating'].isnull() == False]
#     counts_per_rating_and_eb = heat_map_df.groupby(['Rating', 'Rating (eb)']).size().reset_index(name='count')
#     counts_per_rating = heat_map_df.groupby(['Rating']).size().reset_index(name='count')

#     p = px.scatter(
#         df[df['Rating'].isnull() == False], 
#         x='Rating', 
#         y='Rating (eb)',
#         size='Volume of Ratings',
#         title='Empirical Bayes Smoothing',
#         hover_data=['Brand']
#     )
#     st.plotly_chart(p)


st.caption('📊 Data source: [Shop App Canada](https://shop.app/events/shop-canada)')
st.caption('🛠️ GitHub: [parker84/shop-canada](https://github.com/parker84/shop-canada)')