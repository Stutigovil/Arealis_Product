import streamlit as st
import pandas as pd
import numpy as np
import datetime
from io import BytesIO
from fuzzywuzzy import process

st.set_page_config(page_title="Retail Data Cleaner", layout="wide")

# --- Sidebar ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Shopping_cart_icon.svg/768px-Shopping_cart_icon.svg.png", width=80)
st.sidebar.title("Retail Data Ingestion")
st.sidebar.markdown("🔍 Upload & Validate Broken Retail Data Files")
st.sidebar.markdown("---")
preserve_rows = st.sidebar.checkbox("Preserve rows with invalid data (fill with defaults)", value=False)

# --- Header ---
st.markdown("## 🧼 Retail Data Auto-Cleaner")
st.markdown("Upload broken Excel/CSV files from store managers and watch the system clean, validate, and structure them in real-time.")

# --- File Upload ---
uploaded_file = st.file_uploader("📤 Upload a CSV or Excel File", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Read file with encoding handling
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        else:
            df = pd.read_excel(uploaded_file)

        st.markdown("### Received Data (Before Cleaning)")

        # Show the first 5 rows before cleaning
        st.dataframe(df.head())

        # Column Mapping Dictionary with Expanded Names
        column_mapping = {
            'transaction_id': ['transaction_id', 'transactionid', 'txn_id', 'transaction', 'txn', 'trans_id'],
            'date_of_sale': ['date_of_sale', 'sale_date', 'transaction_date', 'purchase_date', 'sale_datetime', 'date'],
            'brand': ['brand', 'product_brand', 'company', 'manufacturer', 'product_label', 'product_make'],
            'product_name': ['product_name', 'item_name', 'product', 'item', 'product_label', 'item_description'],
            'category': ['category', 'product_category', 'product_type', 'item_category', 'category_name'],
            'sub_category': ['sub_category', 'subcategory', 'category_type', 'item_subcategory'],
            'size': ['size', 'product_size', 'item_size', 'garment_size', 'shoe_size'],
            'color': ['color', 'product_color', 'item_color', 'colour'],
            'price': ['price', 'cost', 'product_price', 'item_price', 'cost_price', 'unit_price'],
            'discount_percent': ['discount_percent', 'discount', 'discount_rate', 'discount_value'],
            'final_price': ['final_price', 'price_after_discount', 'sale_price', 'final_cost', 'net_price'],
            'quantity': ['quantity', 'qty', 'units', 'item_count', 'quantity_sold'],
            'payment_mode': ['payment_mode', 'payment_method', 'transaction_mode', 'payment_type', 'payment_method_type'],
            'store_location': ['store_location', 'outlet', 'store', 'store_name', 'location', 'store_address'],
            'sales_channel': ['sales_channel', 'channel', 'selling_channel', 'sale_channel', 'channel_type'],
            'customer_id': ['customer_id', 'user_id', 'client_id', 'customer_number', 'account_id'],
            'customer_gender': ['customer_gender', 'gender', 'user_gender', 'customer_sex'],
            'return_status': ['return_status', 'is_returned', 'return', 'return_flag', 'return_ind'],
            'return_reason': ['return_reason', 'reason_for_return', 'return_cause', 'return_description', 'reason'],
            'review_text': ['review_text', 'customer_review', 'feedback', 'product_review', 'review'],
            'co2_saved': ['co2_saved', 'carbon_saved', 'carbon_emission_saved', 'co2_reduction'],
            'rating': ['rating', 'product_rating', 'customer_rating', 'user_rating', 'product_review_score'],
            'delivery_days': ['delivery_days', 'days_to_deliver', 'delivery_time', 'shipping_days', 'shipping_time']
        }

        found_columns = {}

        # Convert column names to lowercase and strip spaces for easier matching
        df_columns = [col.lower().strip() for col in df.columns]

        # Check if columns from the mapping exist in the DataFrame
        for key, value in column_mapping.items():
            for v in value:
                # Check if the cleaned column name is in the DataFrame
                if v.lower().strip() in df_columns:
                    original_name = df.columns[df_columns.index(v.lower().strip())]
                    found_columns[original_name] = key

        # Renaming columns
        new_df = df.copy()
        for orig_name, new_name in found_columns.items():
            new_df.rename(columns={orig_name: new_name}, inplace=True)

        # --- Log Output: Show which columns were renamed ---
        log_messages = []
        for orig_name, new_name in found_columns.items():
            log_messages.append(f"**Renamed column** '{orig_name}' **to** '{new_name}'")

        # --- Cleaning Process ---
        log_messages.append("\n**### Cleaning Process:**")

        # 1. Handle missing values
        log_messages.append("- **Filling missing values** with default entries for optional columns.")
        new_df.fillna({
            'return_reason': 'No return reason',
            'review_text': 'No review provided',
            'rating': 0,
            'co2_saved': 0,
        }, inplace=True)

        # 2. Correct the date format
        new_df['date_of_sale'] = pd.to_datetime(new_df['date_of_sale'], errors='coerce')
        log_messages.append("- **Converted 'date_of_sale' to datetime format.**")

        # 3. Ensure the 'price' and 'final_price' are numeric
        new_df['price'] = pd.to_numeric(new_df['price'], errors='coerce')
        new_df['final_price'] = pd.to_numeric(new_df['final_price'], errors='coerce')
        log_messages.append("- **Converted 'price' and 'final_price' to numeric.**")

        # 4. Convert categorical columns to uppercase or title-case
        new_df['brand'] = new_df['brand'].str.upper().str.strip()
        new_df['category'] = new_df['category'].str.title().str.strip()
        new_df['sub_category'] = new_df['sub_category'].str.title().str.strip()
        new_df['payment_mode'] = new_df['payment_mode'].str.upper().str.strip()
        new_df['store_location'] = new_df['store_location'].str.title().str.strip()
        new_df['sales_channel'] = new_df['sales_channel'].str.title().str.strip()
        log_messages.append("- **Standardized case for categorical columns: 'brand', 'category', 'sub_category', etc.**")

        # 5. Handle quantity as integers
        new_df['quantity'] = pd.to_numeric(new_df['quantity'], errors='coerce', downcast='integer')
        log_messages.append("- **Converted 'quantity' to integers.**")

        # 6. Handle rating as float
        new_df['rating'] = pd.to_numeric(new_df['rating'], errors='coerce')
        log_messages.append("- **Converted 'rating' to float.**")

        # 7. Handle discount as percentage (ensure it's numeric and between 0-100)
        new_df['discount_percent'] = pd.to_numeric(new_df['discount_percent'], errors='coerce')
        new_df['discount_percent'] = new_df['discount_percent'].clip(0, 100)
        log_messages.append("- **Validated 'discount_percent' to fall between 0 and 100.**")

        # 8. Handle any remaining NaN or invalid values
        new_df.fillna({
            'price': new_df['price'].median(),  # Use median for price in case of NaN
            'final_price': new_df['final_price'].median(),  # Use median for final_price in case of NaN
        }, inplace=True)

        # --- Log Output: Stats Before and After ---
        log_messages.append("\n**### Data Statistics Before Cleaning:**")
        before_cleaning_stats = df.describe(include='all').transpose()

        log_messages.append("\n**### Data Statistics After Cleaning:**")
        after_cleaning_stats = new_df.describe(include='all').transpose()

        # Display the cleaned rows
        st.markdown("### Cleaned Data Preview:")
        st.dataframe(new_df.head())

        # Display logs of what was done in a scrollable window
        st.markdown("### Logs of Cleaning Process:")
        st.text_area("Cleaning Logs", "\n".join(log_messages), height=300)

        st.markdown(f"**Shape (Before):** {df.shape}")
        st.markdown(f"**Shape (After):** {new_df.shape}")
        st.markdown(f"**Columns (Before):** {df.columns}")
        st.markdown(f"**Columns (After):** {new_df.columns}")

        # Display stats in a more organized manner
        st.markdown("### Data Statistics Before Cleaning:")
        st.dataframe(before_cleaning_stats)

        st.markdown("### Data Statistics After Cleaning:")
        st.dataframe(after_cleaning_stats)

    except Exception as e:
        st.markdown(f"Error: {e}")

else:
    st.markdown("Upload to begin")