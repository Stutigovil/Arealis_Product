# import streamlit as st
# import pandas as pd
# import sqlite3
# import requests
# import re

# # --- CONFIG ---
# OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "your-openrouter-key")
# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# headers = {
#     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#     "Content-Type": "application/json"
# }

# model = "mistralai/mixtral-8x7b-instruct"

# st.title("🧠 NLP → SQL using Mixtral")
# st.caption("Upload your retail CSV, ask questions, get SQL, run queries.")

# # --- FILE UPLOAD ---
# uploaded_file = st.file_uploader("📁 Upload Retail CSV", type=["csv"])
# if uploaded_file:
#     df = pd.read_csv(uploaded_file, header=0)
#     df = df.loc[:, ~df.columns.str.contains('^unnamed', case=False)]
#     df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

#     st.subheader("✅ Sanitized Columns")
#     st.write(df.columns.tolist())

#     conn = sqlite3.connect(":memory:")
#     df.to_sql("data", conn, index=False, if_exists="replace")

#     # Show SQLite schema
#     schema_df = pd.read_sql_query("PRAGMA table_info(data);", conn)
#     st.subheader("🧱 SQLite Table Schema")
#     st.dataframe(schema_df)

#     # Preview data
#     try:
#         preview_df = pd.read_sql_query("SELECT * FROM data LIMIT 5", conn)
#         st.subheader("🔍 Table Preview")
#         st.dataframe(preview_df)
#     except Exception as e:
#         st.error(f"❌ Preview Error: {e}")

#     # --- USER QUESTION ---
#     st.markdown("---")
#     question = st.text_input("💬 Ask a question (e.g. What is the most sold product?)")

#     if question:
#         schema = ", ".join(df.columns)
#         prompt = f"""
# You are a professional data analyst. Convert the user question below into a valid SQLite SQL query.

# Only use this table:
# - Table name: data
# - Columns: {schema}

# Only return a clean SQL query. Do not explain or format.

# Use GROUP BY, ORDER BY, and SUM if needed.

# Question: {question}
# SQL:
# """.strip()

#         with st.spinner("🤖 Generating SQL..."):
#             try:
#                 payload = {
#                     "model": model,
#                     "messages": [{"role": "user", "content": prompt}]
#                 }
#                 response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
#                 raw = response.json()["choices"][0]["message"]["content"]

#                 matches = re.findall(r"(SELECT\s.+?)(?:;|\n|$)", raw, re.IGNORECASE | re.DOTALL)
#                 if matches:
#                     sql_query = matches[0].strip()
#                 else:
#                     st.error("⚠️ No SQL found. See full model output below.")
#                     st.code(raw)
#                     st.stop()

#                 st.subheader("🧾 Generated SQL")
#                 sql_query = st.text_area("Edit SQL if needed", value=sql_query, height=120)

#                 if st.button("▶️ Run SQL"):
#                     try:
#                         result = pd.read_sql_query(sql_query, conn)
#                         st.success("✅ Query Result")
#                         st.dataframe(result)
#                     except Exception as e:
#                         st.error(f"❌ SQL Execution Error: {e}")

#             except Exception as e:
#                 st.error(f"❌ OpenRouter API Error: {e}")
# else:
#     st.info("📤 Upload a CSV file with retail data to begin.")
import streamlit as st
import pandas as pd
import sqlite3
import requests
import re

# --- CONFIG ---
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "your-openrouter-key")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

model = "mistralai/mixtral-8x7b-instruct"

st.title("🧠 NLP → SQL using Mixtral (with Hardcoded Fallback)")
st.caption("Upload your retail CSV, ask questions, get SQL, run queries.")

# --- HARDCODED PROMPT-SQL DICTIONARY ---
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

    "Which customer age group buys the most?":
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
uploaded_file = st.file_uploader("\U0001F4C1 Upload Retail CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file, header=0)
    df = df.loc[:, ~df.columns.str.contains('^unnamed', case=False)]
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    st.subheader("✅ Sanitized Columns")
    st.write(df.columns.tolist())

    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")

    schema_df = pd.read_sql_query("PRAGMA table_info(data);", conn)
    st.subheader("🧱 SQLite Table Schema")
    st.dataframe(schema_df)

    preview_df = pd.read_sql_query("SELECT * FROM data LIMIT 5", conn)
    st.subheader("🔍 Table Preview")
    st.dataframe(preview_df)

    st.markdown("---")
    question = st.text_input("💬 Ask a question (e.g. What is the most sold product?)")

    if question:
        query = nl_sql_pairs.get(question.strip())
        if query:
            st.subheader("🧾 SQL Query (From Hardcoded List)")
            st.code(query, language="sql")
            try:
                result = pd.read_sql_query(query, conn)
                st.success("✅ Query Result")
                st.dataframe(result)
            except Exception as e:
                st.error(f"❌ SQL Execution Error: {e}")
        else:
            schema = ", ".join(df.columns)
            prompt = f"""
You are a professional data analyst. Convert the user question below into a valid SQLite SQL query.

Only use this table:
- Table name: data
- Columns: {schema}

Only return a clean SQL query. Do not explain or format.

Use GROUP BY, ORDER BY, and SUM if needed.

Question: {question}
SQL:
""".strip()

            with st.spinner("🤖 Generating SQL via LLM..."):
                try:
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}]
                    }
                    response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
                    raw = response.json()["choices"][0]["message"]["content"]

                    matches = re.findall(r"(SELECT\s.+?)(?:;|\n|$)", raw, re.IGNORECASE | re.DOTALL)
                    if matches:
                        sql_query = matches[0].strip()
                    else:
                        st.error("⚠️ No SQL found. See full model output below.")
                        st.code(raw)
                        st.stop()

                    st.subheader("🧾 Generated SQL (LLM)")
                    sql_query = st.text_area("Edit SQL if needed", value=sql_query, height=120)

                    if st.button("▶️ Run SQL"):
                        try:
                            result = pd.read_sql_query(sql_query, conn)
                            st.success("✅ Query Result")
                            st.dataframe(result)
                        except Exception as e:
                            st.error(f"❌ SQL Execution Error: {e}")

                except Exception as e:
                    st.error(f"❌ OpenRouter API Error: {e}")
else:
    st.info("📤 Upload a CSV file with retail data to begin.")
