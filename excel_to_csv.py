import pandas as pd
import os

def convert_excel_to_csv(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".xlsx") or file.endswith(".xls"):
            file_path = os.path.join(folder_path, file)
            try:
                excel_data = pd.read_excel(file_path, sheet_name=None)  
                for sheet_name, df in excel_data.items():
                    csv_file_name = f"{os.path.splitext(file)[0]}_{sheet_name}.csv"
                    csv_path = os.path.join(folder_path, csv_file_name)
                    df.to_csv(csv_path, index=False)
                    print(f" Converted: {file} [Sheet: {sheet_name}] → {csv_file_name}")
            except Exception as e:
                print(f" Error processing {file}: {e}")


folder = "excel_files"
convert_excel_to_csv(folder)
