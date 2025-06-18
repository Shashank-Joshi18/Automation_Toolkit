import streamlit as st
import pandas as pd
from io import BytesIO

st.title("📊 UAD Consolidator")

st.markdown("""
Upload multiple Excel files. The app will skip the first 2 rows, select columns A to AK,
combine them, and allow you to download the final consolidated file.
""")

uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    all_data = []

    for file in uploaded_files:
        try:
            df = pd.read_excel(file, skiprows=2, usecols="A:AK", engine='openpyxl')
            df["Source File"] = file.name  # Optional: track file origin
            all_data.append(df)
        except Exception as e:
            st.warning(f"⚠️ Skipping file **{file.name}** due to error: {e}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        st.success("✅ Successfully combined Excel files!")

        st.subheader("Preview of Consolidated Data:")
        st.dataframe(combined_df)

        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name="Consolidated")
                workbook = writer.book
                worksheet = writer.sheets["Consolidated"]

                # Formats
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#4472C4',
                    'font_color': 'white',
                    'border': 1
                })
                alt_row_format = workbook.add_format({
                    'bg_color': '#F2F2F2'
                })
                source_file_format = workbook.add_format({
                    'bg_color': '#C6EFCE',
                    'border': 1
                })

                # Apply header format
                for col_num, col_name in enumerate(df.columns):
                    worksheet.write(0, col_num, col_name, header_format)

                # Apply row formatting safely
                for row_num, row_data in df.iterrows():
                    for col_num, value in enumerate(row_data):
                        col_name = df.columns[col_num]
                        cell_value = None if pd.isna(value) or pd.isnull(value) else value
                        if col_name == "Source File":
                            worksheet.write(row_num + 1, col_num, cell_value, source_file_format)
                        elif row_num % 2 == 1:
                            worksheet.write(row_num + 1, col_num, cell_value, alt_row_format)
                        else:
                            worksheet.write(row_num + 1, col_num, cell_value)

                # Freeze header
                worksheet.freeze_panes(1, 0)

            return output.getvalue()

        excel_bytes = convert_df_to_excel(combined_df)

        st.download_button(
            label="📥 Download Consolidated File",
            data=excel_bytes,
            file_name="Consolidated_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("❌ No valid Excel files were found.")
