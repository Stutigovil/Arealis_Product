import streamlit as st
import pandas as pd
import numpy as np
import datetime
from io import BytesIO
from fuzzywuzzy import process
import sqlite3
import requests
import re
import plotly.express as px

st.set_page_config(page_title="Retail Data Cleaner", layout="wide")

# --- Sidebar ---
st.sidebar.image("Screenshot 2025-07-03 180755.png", width=80)
st.sidebar.title("ForesightFlow X Arealis – Problem-Driven Feature Validation & System Mapping for Fashion Retail AI Suite")
st.sidebar.markdown("🔍 Upload & Validate Broken Retail Data Files")
st.sidebar.markdown("---")
preserve_rows = st.sidebar.checkbox("Preserve rows with invalid data (fill with defaults)", value=False)

# --- Header ---
st.markdown("## 🧼 Data ingestion and Prompt window")
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






# --- CONFIG ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "your-openrouter-key")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}
model = "mistralai/mixtral-8x7b-instruct"

# --- PAGE ---
# st.title("🧠 NLP → SQL using Mixtral (with Visual Feature Comparison)")
st.caption("Upload retail data → Ask questions → Run SQL → See chart & matrix comparison")

# --- HARDCODED PROMPTS ---

nl_sql_pairs = {
    "What is the most sold product?":
        "SELECT product_name, SUM(quantity) AS total_sold FROM data GROUP BY product_name ORDER BY total_sold DESC LIMIT 1",

    "Which brand had the highest revenue?":
        "SELECT brand, SUM(final_price * quantity) AS revenue FROM data GROUP BY brand ORDER BY revenue DESC LIMIT 1",

    "Which category has the most returns?":
        "SELECT category, COUNT(*) AS return_count FROM data WHERE return_status = 1 GROUP BY category ORDER BY return_count DESC LIMIT 1",

    "What is the average delivery time?":
        "SELECT AVG(delivery_days) AS avg_delivery_time FROM data",

    "Which payment mode is most used?":
        "SELECT payment_mode, COUNT(*) AS count FROM data GROUP BY payment_mode ORDER BY count DESC LIMIT 1",

    "Which store location had the highest revenue?":
        "SELECT store_location, SUM(final_price * quantity) AS revenue FROM data GROUP BY store_location ORDER BY revenue DESC LIMIT 1",

    "What is the average discount given?":
        "SELECT AVG(discount_percent) AS avg_discount FROM data",

    "Which brand has the best average rating?":
        "SELECT brand, AVG(rating) AS avg_rating FROM data GROUP BY brand ORDER BY avg_rating DESC LIMIT 1",

    "What are the top 5 returned products?":
        "SELECT product_name, COUNT(*) AS return_count FROM data WHERE return_status = 1 GROUP BY product_name ORDER BY return_count DESC LIMIT 5",

    "Which sales channel performs best?":
        "SELECT sales_channel, SUM(final_price * quantity) AS total_sales FROM data GROUP BY sales_channel ORDER BY total_sales DESC LIMIT 1",

    "Which product has the highest average rating?":
        "SELECT product_name, AVG(rating) AS avg_rating FROM data GROUP BY product_name ORDER BY avg_rating DESC LIMIT 1",

    "c":
        "SELECT customer_age_group, SUM(quantity) AS total_quantity FROM data GROUP BY customer_age_group ORDER BY total_quantity DESC LIMIT 1",

    "Which gender contributes most to sales?":
        "SELECT customer_gender, SUM(final_price * quantity) AS total_sales FROM data GROUP BY customer_gender ORDER BY total_sales DESC LIMIT 1",

    "What is the total CO2 saved from returns?":
        "SELECT SUM(co2_saved) AS total_co2_saved FROM data WHERE return_status = 1",

    "What is the average price of products sold?":
        "SELECT AVG(price) AS avg_price FROM data",

    "Which color is most popular?":
        "SELECT color, SUM(quantity) AS count FROM data GROUP BY color ORDER BY count DESC LIMIT 1",

    "Which size is most sold?":
        "SELECT size, SUM(quantity) AS count FROM data GROUP BY size ORDER BY count DESC LIMIT 1",

    "What are the top 5 brands by sales?":
        "SELECT brand, SUM(final_price * quantity) AS revenue FROM data GROUP BY brand ORDER BY revenue DESC LIMIT 5",

    "Which city has the most returns?":
        "SELECT store_location, COUNT(*) AS return_count FROM data WHERE return_status = 1 GROUP BY store_location ORDER BY return_count DESC LIMIT 1",

    "What is the return rate overall?":
        "SELECT ROUND(100.0 * SUM(CASE WHEN return_status THEN 1 ELSE 0 END) / COUNT(*), 2) AS return_rate FROM data",

    "What is the best performing sub-category?":
        "SELECT sub_category, SUM(final_price * quantity) AS revenue FROM data GROUP BY sub_category ORDER BY revenue DESC LIMIT 1",

    "What are the top 3 payment modes used?":
        "SELECT payment_mode, COUNT(*) AS count FROM data GROUP BY payment_mode ORDER BY count DESC LIMIT 3",

    "Which brand has the highest average discount?":
        "SELECT brand, AVG(discount_percent) AS avg_discount FROM data GROUP BY brand ORDER BY avg_discount DESC LIMIT 1",

    "Which product is returned the most?":
        "SELECT product_name, COUNT(*) AS return_count FROM data WHERE return_status = 1 GROUP BY product_name ORDER BY return_count DESC LIMIT 1",

    "Which day had the highest sales?":
        "SELECT date_of_sale, SUM(final_price * quantity) AS revenue FROM data GROUP BY date_of_sale ORDER BY revenue DESC LIMIT 1",

    "Which gender returns products the most?":
        "SELECT customer_gender, COUNT(*) AS return_count FROM data WHERE return_status = 1 GROUP BY customer_gender ORDER BY return_count DESC LIMIT 1",

    "Which city has the lowest average delivery time?":
        "SELECT store_location, AVG(delivery_days) AS avg_days FROM data GROUP BY store_location ORDER BY avg_days ASC LIMIT 1",

    "What are the least sold products?":
        "SELECT product_name, SUM(quantity) AS total_sold FROM data GROUP BY product_name ORDER BY total_sold ASC LIMIT 5",

    "Which age group gives highest ratings?":
        "SELECT customer_age_group, AVG(rating) AS avg_rating FROM data GROUP BY customer_age_group ORDER BY avg_rating DESC LIMIT 1",

    "Which category has the highest average price?":
        "SELECT category, AVG(price) AS avg_price FROM data GROUP BY category ORDER BY avg_price DESC LIMIT 1",

    "How many items were sold overall?":
        "SELECT SUM(quantity) AS total_items_sold FROM data",

    "Which product has the lowest return rate?":
        "SELECT product_name, 100.0 * SUM(CASE WHEN return_status THEN 1 ELSE 0 END) / COUNT(*) AS return_rate FROM data GROUP BY product_name ORDER BY return_rate ASC LIMIT 1",

    "What is the average rating by category?":
        "SELECT category, AVG(rating) AS avg_rating FROM data GROUP BY category",

    "Which payment method has highest average sale amount?":
        "SELECT payment_mode, AVG(final_price * quantity) AS avg_sale FROM data GROUP BY payment_mode ORDER BY avg_sale DESC LIMIT 1",

    "Which store sold the most quantity?":
        "SELECT store_location, SUM(quantity) AS total_sold FROM data GROUP BY store_location ORDER BY total_sold DESC LIMIT 1",

    "What are the top 5 most discounted products?":
        "SELECT product_name, AVG(discount_percent) AS avg_discount FROM data GROUP BY product_name ORDER BY avg_discount DESC LIMIT 5",

    "Which gender gives highest average ratings?":
        "SELECT customer_gender, AVG(rating) AS avg_rating FROM data GROUP BY customer_gender ORDER BY avg_rating DESC LIMIT 1",

    "Which city generates the most revenue from returns?":
        "SELECT store_location, SUM(final_price * quantity) AS returned_revenue FROM data WHERE return_status = 1 GROUP BY store_location ORDER BY returned_revenue DESC LIMIT 1",

    "Which category has the most quantity sold?":
        "SELECT category, SUM(quantity) AS total_quantity FROM data GROUP BY category ORDER BY total_quantity DESC LIMIT 1",

    "How many products were sold online vs offline?":
        "SELECT sales_channel, SUM(quantity) AS total_sold FROM data GROUP BY sales_channel",

    "Which product category sells best in Delhi?":
        "SELECT category, SUM(quantity) AS total_sold FROM data WHERE store_location = 'Delhi' GROUP BY category ORDER BY total_sold DESC LIMIT 1",

    "What is the total sales revenue?":
        "SELECT SUM(final_price * quantity) AS total_revenue FROM data",

    "Which color is returned the most?":
        "SELECT color, COUNT(*) AS return_count FROM data WHERE return_status = 1 GROUP BY color ORDER BY return_count DESC LIMIT 1",

    "Which brand has highest return rate?":
        "SELECT brand, 100.0 * SUM(CASE WHEN return_status THEN 1 ELSE 0 END) / COUNT(*) AS return_rate FROM data GROUP BY brand ORDER BY return_rate DESC LIMIT 1",

    "What is the average final price per product?":
        "SELECT AVG(final_price) AS avg_final_price FROM data",

    "What are the most common return reasons?":
        "SELECT return_reason, COUNT(*) AS count FROM data WHERE return_status = 1 GROUP BY return_reason ORDER BY count DESC LIMIT 5",

    "Which category has the highest average rating?":
        "SELECT category, AVG(rating) AS avg_rating FROM data GROUP BY category ORDER BY avg_rating DESC LIMIT 1",

    "Which brand sells most via app?":
        "SELECT brand, SUM(quantity) AS total_sold FROM data WHERE sales_channel = 'App' GROUP BY brand ORDER BY total_sold DESC LIMIT 1"
}


# --- FILE UPLOAD ---
if 'new_df' in locals():
    df = new_df.copy()
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df = df.loc[:, ~df.columns.str.contains('^unnamed', case=False)]

    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")

    st.subheader("🧱 Table Schema")
    st.dataframe(pd.read_sql_query("PRAGMA table_info(data);", conn))
    st.subheader("🔍 Preview")
    st.dataframe(pd.read_sql_query("SELECT * FROM data LIMIT 5", conn))

    # --- QUESTION ---
    question = st.text_input("💬 Ask a question")
    result = None

    if question:
        query = nl_sql_pairs.get(question.strip())

        if query:
            st.subheader("🧾 SQL Query (Hardcoded)")
            st.code(query)
            try:
                result = pd.read_sql_query(query, conn)
                st.success("✅ Query Result")
                st.dataframe(result)
            except Exception as e:
                st.error(f"❌ SQL Execution Error: {e}")

        else:
            schema = ", ".join(df.columns)
            prompt = f"""
You are a professional data analyst. Convert the user question into a valid SQLite SQL query.

Table name: data  
Columns: {schema}

Only return SQL query. Do not explain or format.

Question: {question}
SQL:
""".strip()
            with st.spinner("🤖 Generating SQL via Mixtral..."):
                try:
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    res = requests.post(OPENROUTER_URL, headers=headers, json=payload)
                    raw = res.json()["choices"][0]["message"]["content"]

                    matches = re.findall(r"(SELECT\s.+?)(?:;|\n|$)", raw, re.IGNORECASE | re.DOTALL)
                    if matches:
                        sql_query = matches[0].strip()
                        st.subheader("🧾 Generated SQL")
                        sql_query = st.text_area("Edit SQL if needed", value=sql_query)
                        if st.button("▶️ Run SQL"):
                            try:
                                result = pd.read_sql_query(sql_query, conn)
                                st.success("✅ Query Result")
                                st.dataframe(result)
                            except Exception as e:
                                st.error(f"❌ SQL Execution Error: {e}")
                    else:
                        st.error("⚠️ No SQL found")
                        st.code(raw)
                except Exception as e:
                    st.error(f"❌ API Error: {e}")

    # --- FEATURE COMPARISON PLOT ---
    if result is not None:
        st.markdown("---")
        st.subheader("📊 Feature Comparison")

        data = {
            "Feature": [
                   "Multiple Data Ingestion Sources",
                                "Hyperlocal Sentiment Analysis",
                                "Quick Win Trend Analysis",
                                "Prompt-based Business Querying",
                                "Strategy Testing / Simulation",
                                "Consulting-style Auto Report Generation",
                                "Design Ideation (Visual AI)",
                                "SKU-Level Pricing Automation",
                                "Generative AI Narrative Insights",
                                "Product Matching (CV/NLP embeddings)"
            ],
            "ForesightFlow":     [1, 1, 1, 1, 1, 1, 0, 0, 1, 0],
            "Stylumia":          [1, 0, 1, 0, 1, 0, 1, 0, 1, 1],
            "Fractal":           [1, 1, 1, 1, 1, 1, 0, 1, 1, 0],
            "EDITED":            [1, 0, 0, 1, 0, 0, 0, 1, 1, 1],
            "Woven Insights":    [1, 1, 1, 1, 0, 0, 0, 0, 1, 0]
        }
        feat_df = pd.DataFrame(data).set_index("Feature")

        selected_feature = st.selectbox("🎛 Choose feature to compare", feat_df.index)
        row = feat_df.loc[selected_feature] * 100
        row_df = pd.DataFrame({"Company": row.index, "Support (%)": row.values})

        fig = px.bar(
            row_df.sort_values("Support (%)"),
            x="Support (%)", y="Company", orientation="h",
            color="Support (%)", color_continuous_scale="Blues",
            text="Support (%)", height=400
        )
        fig.update_layout(
            title=f"Support for: {selected_feature}",
            xaxis_title="Support %", yaxis_title="", plot_bgcolor="#FAFAFA",
            coloraxis_showscale=False
        )
        fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

        st.image("Comparative Matirx.jpg", caption="📌 Comparative Matrix Summary", use_column_width=True)
else:
    st.info("📤 Please upload a CSV file to begin.")
