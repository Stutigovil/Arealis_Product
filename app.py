# # # import streamlit as st
# # # import pandas as pd
# # # import sqlite3
# # # import requests

# # # # --- SETUP ---
# # # TOGETHER_API_KEY = st.secrets.get("TOGETHER_API_KEY", "your-together-api-key")
# # # TOGETHER_MODEL_URL = "https://api.together.xyz/v1/chat/completions"
# # # headers = {
# # #     "Authorization": f"Bearer {TOGETHER_API_KEY}",
# # #     "Content-Type": "application/json"
# # # }

# # # # # --- SIDEBAR NAVIGATION ---
# # # # st.sidebar.title("SmartReturns")
# # # # st.sidebar.markdown("Sustainability Platform")
# # # # st.sidebar.markdown("---")
# # # # menu = st.sidebar.radio("Platform", [
# # # #     "Dashboard", "Insights", "Hub Network", "Advanced Analytics",
# # # #     "Data Management", "Data Explorer", "Worker Interface"
# # # # ])

# # # st.title("📊 Product Category Insights")
# # # st.caption("Return patterns and sustainability impact by category")

# # # # --- UPLOAD CSV ---
# # # uploaded_file = st.file_uploader("📁 Upload your Retail Dataset", type=["csv"])
# # # if uploaded_file:
# # #     df = pd.read_csv(uploaded_file)
# # #     st.success("✅ File uploaded successfully!")

# # #     # Display section cards by category
# # #     if 'category' in df.columns:
# # #         categories = df['category'].unique()
# # #         cols = st.columns(3)
# # #         for i, cat in enumerate(categories):
# # #             with cols[i % 3]:
# # #                 cat_df = df[df['category'] == cat]
# # #                 st.subheader(cat)
# # #                 st.metric("Total Returns", len(cat_df))
# # #                 if 'co2_saved' in cat_df.columns:
# # #                     st.metric("Avg CO₂ Saved", f"{cat_df['co2_saved'].mean():.1f} kg")
# # #                 if 'value' in cat_df.columns:
# # #                     st.metric("Avg Value", f"₹{cat_df['value'].mean():.0f}")
# # #                 if 'return_reason' in cat_df.columns:
# # #                     reasons = cat_df['return_reason'].value_counts().nlargest(3).index.tolist()
# # #                     st.write("**Top Return Reasons**")
# # #                     for r in reasons:
# # #                         st.button(r, disabled=True)
# # #                 st.button("View Details")

# # #     # Upload to SQLite
# # #     conn = sqlite3.connect(":memory:")
# # #     df.to_sql("data", conn, index=False, if_exists="replace")

# # #     # NL → SQL Prompt Window
# # #     st.markdown("---")
# # #     st.header("🧠 Ask Questions About Your Data")
# # #     schema = ", ".join(df.columns)
# # #     user_input = st.text_input("Type your question (e.g., What is the avg return value for electronics?)")

# # #     if user_input:
# # #         with st.spinner("Generating SQL query..."):
# # #             nl_prompt = f"""
# # # You are an expert SQL assistant. Convert the following user question to a valid SQLite SQL query. Use GROUP BY and COUNT properly when needed.

# # # Only return a single SQL query without any explanation.

# # # Table name: data
# # # Columns: {schema}

# # # User: {user_input}
# # # SQL:
# # # """


# # #             try:
# # #                 payload = {
# # #                     "model": "meta-llama/Llama-3-8b-chat-hf",
# # #                     "messages": [
# # #                         {"role": "user", "content": nl_prompt}
# # #                     ]
# # #                 }
# # #                 response = requests.post(TOGETHER_MODEL_URL, headers=headers, json=payload)
# # #                 output = response.json()
# # #                 sql_query = output["choices"][0]["message"]["content"].strip().split("\n")[0]
# # #                 st.code(sql_query, language="sql")
# # #                 result = pd.read_sql_query(sql_query, conn)
# # #                 st.success("✅ Result")
# # #                 st.dataframe(result)

# # #                 explain_prompt = f"""
# # # You are a helpful assistant. Explain the following SQL query and its result in simple English that a non-technical user can understand.

# # # SQL Query:
# # # {sql_query}

# # # Result:
# # # {result.head(5).to_markdown(index=False)}

# # # Explanation:
# # # """

# # #                 explain_payload = {
# # #                     "model": "meta-llama/Llama-3-8b-chat-hf",
# # #                     "messages": [
# # #                         {"role": "user", "content": explain_prompt}
# # #                     ]
# # #                 }
# # #                 response2 = requests.post(TOGETHER_MODEL_URL, headers=headers, json=explain_payload)
# # #                 explanation = response2.json()["choices"][0]["message"]["content"].strip()
# # #                 if "don’t always understand" in explanation.lower() or len(explanation) < 10:
# # #                     explanation = "The query ran, but the result was too minimal or unclear to explain well."

# # #                 st.markdown(f"### 📝 Explanation\n{explanation}")
# # #             except Exception as e:
# # #                 st.error(f"Error: {e}")
# # # else:
# # #     st.warning("Please upload a dataset to begin.")
# # import streamlit as st
# # import pandas as pd
# # import sqlite3
# # import requests

# # # --- SETUP ---
# # TOGETHER_API_KEY = st.secrets.get("TOGETHER_API_KEY", "your-together-api-key")
# # TOGETHER_MODEL_URL = "https://api.together.xyz/v1/chat/completions"
# # headers = {
# #     "Authorization": f"Bearer {TOGETHER_API_KEY}",
# #     "Content-Type": "application/json"
# # }

# # st.title("🛍️ Fashion Retail Insights (NLP ↔ SQL)")
# # st.caption("Upload your sales data and ask questions in plain English.")

# # # --- UPLOAD CSV ---
# # uploaded_file = st.file_uploader("📁 Upload your Fashion Sales Dataset", type=["csv"])
# # if uploaded_file:
# #     df = pd.read_csv(uploaded_file)
# #     st.success("✅ File uploaded successfully!")

# #     # Show preview
# #     st.markdown("### 🔍 Data Preview")
# #     st.dataframe(df.head())

# #     # Upload to in-memory SQLite
# #     conn = sqlite3.connect(":memory:")
# #     df.to_sql("data", conn, index=False, if_exists="replace")
# #     try:
# #     # 🔍 Confirm actual SQLite table contents
# #         test_preview = pd.read_sql_query("SELECT * FROM data LIMIT 5", conn)
# #         st.dataframe(test_preview)
# #     except Exception as e:
# #         st.error(f"❌ Could not preview SQLite table: {e}")
# #     # --- Ask Natural Language Question ---
# #     st.markdown("---")
# #     st.markdown("### 🤖 Ask a Question About Your Data")
# #     schema = ", ".join(df.columns)
# #     user_input = st.text_input("E.g., What was the most sold product?")

# #     if user_input:
# #         with st.spinner("Generating SQL query..."):
# #             # Step 1: Prompt LLM to convert NL → SQL
# #             schema = ", ".join(df.columns)
# #             nl_to_sql_prompt = f"""
# # You are a SQL expert. Given the table below with columns:

# # {schema}

# # Generate a valid SQLite SQL query ONLY using these columns.

# # User question: {user_input}
# # SQL:
# # """

# #             try:
# #                 payload = {
# #                     "model": "meta-llama/Llama-3-8b-chat-hf",
# #                     "messages": [
# #                         {"role": "user", "content": nl_to_sql_prompt}
# #                     ]
# #                 }
# #                 response = requests.post(TOGETHER_MODEL_URL, headers=headers, json=payload)
# #                 output = response.json()
# #                 import re

# #                 # Get full content
# #                 raw_sql_output = output["choices"][0]["message"]["content"]

# #                 # Extract the actual SQL using regex
# #                 matches = re.findall(r"(?i)(SELECT\s.+?)(?:;|\n|$)", raw_sql_output, re.DOTALL)
# #                 if matches:
# #                     sql_query = matches[0].strip()
# #                 else:
# #                     st.error("❌ Could not extract a valid SQL query from the model response.")
# #                     st.stop()

# #                 st.code(sql_query, language="sql")

# #                 # Step 2: Execute the SQL
# #                 try:
# #                     result = pd.read_sql_query(sql_query, conn)
# #                     st.success("✅ Query Result")
# #                     st.dataframe(result)

# #                     # Step 3: Explain the result
# #                     explain_prompt = f"""
# # You are a helpful assistant. Explain the following SQL query and its result in simple English for a business user.

# # SQL Query:
# # {sql_query}

# # Result:
# # {result.head(5).to_markdown(index=False)}

# # Explanation:
# # """
# #                     explain_payload = {
# #                         "model": "meta-llama/Llama-3-8b-chat-hf",
# #                         "messages": [
# #                             {"role": "user", "content": explain_prompt}
# #                         ]
# #                     }
# #                     response2 = requests.post(TOGETHER_MODEL_URL, headers=headers, json=explain_payload)
# #                     explanation = response2.json()["choices"][0]["message"]["content"].strip()

# #                     # Fallback for bad explanations
# #                     if "don’t always understand" in explanation.lower() or len(explanation) < 10:
# #                         explanation = "The query ran, but the result was too minimal or unclear to explain well."

# #                     st.markdown(f"### 📝 Explanation\n{explanation}")

# #                 except Exception as sql_error:
# #                     st.error(f"❌ SQL Execution Error: {sql_error}")

# #             except Exception as e:
# #                 st.error(f"❌ Error while calling LLM: {e}")
# # else:
# #     st.warning("Please upload a dataset to begin.")
# import streamlit as st
# import pandas as pd
# import sqlite3

# st.title("🔍 Test SQL on Uploaded CSV")

# # Upload CSV
# uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
# if uploaded_file:
#     df = pd.read_csv(uploaded_file)

#     # Clean column names
#     df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    
#     st.write("📄 Columns in CSV:", list(df.columns))
#     st.dataframe(df.head())

#     # Upload to SQLite
#     conn = sqlite3.connect(":memory:")
#     df.to_sql("data", conn, index=False, if_exists="replace")

#     # Show SQLite schema
#     schema_df = pd.read_sql_query("PRAGMA table_info(data);", conn)
#     st.write("🧱 SQLite Table Schema")
#     st.dataframe(schema_df)

#     # Manual SQL test
#     if "product" in df.columns and "quantity" in df.columns:
#         try:
#             sql = "SELECT product, SUM(quantity) as total_quantity FROM data GROUP BY product"
#             st.code(sql, language="sql")
#             result = pd.read_sql_query(sql, conn)
#             st.success("✅ SQL ran successfully!")
#             st.dataframe(result)
#         except Exception as e:
#             st.error(f"❌ SQL error: {e}")
#     else:
#         st.warning("⚠️ 'product' or 'quantity' column not found in your data.")
# else:
#     st.info("📥 Please upload a CSV to begin.")
# import streamlit as st
# import pandas as pd
# import sqlite3
# import requests
# import re

# # === TOGETHER API SETUP ===
# TOGETHER_API_KEY = st.secrets.get("TOGETHER_API_KEY", "your-together-api-key")
# TOGETHER_MODEL_URL = "https://api.together.xyz/v1/chat/completions"
# headers = {
#     "Authorization": f"Bearer {TOGETHER_API_KEY}",
#     "Content-Type": "application/json"
# }

# st.title("🔍 NLP to SQL Tester")

# # === FILE UPLOAD ===
# uploaded_file = st.file_uploader("📥 Upload your CSV", type=["csv"])
# if uploaded_file:
#     df = pd.read_csv(uploaded_file)
#     df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

#     st.write("📄 Columns:", list(df.columns))
#     st.dataframe(df.head())

#     # === UPLOAD TO SQLITE ===
#     conn = sqlite3.connect(":memory:")
#     df.to_sql("data", conn, index=False, if_exists="replace")

#     # === USER PROMPT ===
#     user_prompt = st.text_input("💬 Ask a question (e.g. What is the most sold product?)")

#     if user_prompt:
#         st.markdown("---")
#         with st.spinner("Generating SQL..."):
#             schema = ", ".join(df.columns)
#             prompt = f"""
# You are an expert SQLite assistant.
# Convert the following question into a valid SQLite SQL query using only these columns:
# {schema}

# Only return the SQL query.

# Question: {user_prompt}
# SQL:
# """
#             try:
#                 payload = {
#                     "model": "meta-llama/Llama-3-8b-chat-hf",
#                     "messages": [{"role": "user", "content": prompt}]
#                 }
#                 response = requests.post(TOGETHER_MODEL_URL, headers=headers, json=payload)
#                 raw = response.json()["choices"][0]["message"]["content"]

#                 # Extract SQL
#                 matches = re.findall(r"(SELECT\s.+?)(?:;|\n|$)", raw, re.IGNORECASE | re.DOTALL)
#                 if matches:
#                     sql_query = matches[0].strip()
#                     st.code(sql_query, language="sql")

#                     # Run query
#                     try:
#                         result = pd.read_sql_query(sql_query, conn)
#                         st.success("✅ Query Result")
#                         st.dataframe(result)
#                     except Exception as e:
#                         st.error(f"❌ SQL Execution Error: {e}")
#                 else:
#                     st.error("⚠️ Couldn't extract a SQL query from the response.")

#             except Exception as e:
#                 st.error(f"❌ API Error: {e}")
# else:
#     st.info("📤 Please upload a CSV to start.")
import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
import re

# === SETUP ===
GENAI_API_KEY = st.secrets.get("GEMINI_API_KEY", "your-gemini-api-key")
genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

st.title("🧠 Gemini SQL Analyst")
st.caption("Upload retail data → Ask questions → Get SQL + answers!")

# === CSV UPLOAD ===
uploaded_file = st.file_uploader("📁 Upload your CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")  # Clean col names
    st.write("📊 Columns:", list(df.columns))
    st.dataframe(df.head())

    # === SAVE TO SQLITE ===
    conn = sqlite3.connect(":memory:")
    df.to_sql("data", conn, index=False, if_exists="replace")

    # === USER PROMPT ===
    question = st.text_input("💬 Ask a question (e.g., Which product sold most?)")
    if question:
        with st.spinner("💡 Generating SQL from your question..."):
            schema = ", ".join(df.columns)
            prompt = f"""
You are a data analyst. Convert the user's question to a valid SQLite SQL query.
Use only the following table and columns:
Table: data
Columns: {schema}

Only return the raw SQL without explanation or markdown.

User Question: {question}
"""
            try:
                gemini_response = model.generate_content(prompt)
                raw_sql = gemini_response.text.strip()

                # Extract the actual SQL query
                matches = re.findall(r"(SELECT\s.+?)(?:;|\n|$)", raw_sql, re.IGNORECASE | re.DOTALL)
                if matches:
                    sql_query = matches[0].strip()
                    st.code(sql_query, language="sql")

                    try:
                        result = pd.read_sql_query(sql_query, conn)
                        st.success("✅ Query Result")
                        st.dataframe(result)

                        # Optional Explanation
                        explain = st.checkbox("📝 Also explain the result in plain English")
                        if explain:
                            result_snippet = result.head(5).to_markdown(index=False)
                            explain_prompt = f"""
You are a helpful assistant. Explain this SQL query and its result in simple English.

SQL: {sql_query}

Result:
{result_snippet}
"""
                            explanation = model.generate_content(explain_prompt).text.strip()
                            st.markdown("### 🔍 Explanation")
                            st.markdown(explanation)

                    except Exception as e:
                        st.error(f"❌ SQL Execution Error: {e}")
                else:
                    st.error("⚠️ Could not extract a SQL query from Gemini's response.")

            except Exception as e:
                st.error(f"❌ Gemini API Error: {e}")
else:
    st.info("📤 Upload a CSV to get started.")
