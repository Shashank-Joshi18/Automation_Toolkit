import streamlit as st
import pandas as pd
import re

st.title("Access Right Transformer")

# File uploader
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    # Read Excel
    df = pd.read_excel(uploaded_file)

    if "Access Right" not in df.columns:
        st.error("The file must contain a column named 'Access Right'")
    else:
        transformed = []
        exceptions = []

        for val in df["Access Right"]:
            if pd.isna(val):  # Handle blanks
                transformed.append(val)
                exceptions.append("Empty")
                continue

            val_str = str(val)

            if "_" not in val_str:
                # No underscore → exception
                transformed.append(val_str)
                exceptions.append("No underscore")
            else:
                parts = val_str.split("_", 1)  # split only at the first _
                prefix, rest = parts[0], parts[1]

                # Check if already contains XXXX or STAR
                if rest.startswith("XXXX") or rest.startswith("STAR"):
                    transformed.append(val_str)
                    exceptions.append("")
                else:
                    # Replace whatever comes after first _ with XXXX
                    # and keep the rest unchanged
                    if "_" in rest:
                        rest_parts = rest.split("_", 1)
                        new_val = f"{prefix}_XXXX_{rest_parts[1]}"
                    else:
                        # only one part after _
                        new_val = f"{prefix}_XXXX"

                    transformed.append(new_val)
                    exceptions.append("")

        # Create output DataFrame
        df_out = df.copy()
        df_out["Transformed Access Right"] = transformed
        df_out["Exception"] = exceptions

        st.write("### Processed Data")
        st.dataframe(df_out)

        # Download option
        output_file = "transformed_access_rights.xlsx"
        df_out.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("Download Result Excel", f, file_name=output_file)
