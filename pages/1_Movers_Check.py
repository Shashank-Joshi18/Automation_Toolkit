import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
from pathlib import Path

st.title("Movers check report generator:")

# 1. Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, skiprows=2)
    st.subheader("Original Excel Data:")
    st.dataframe(df)

    # Backup original column names
    original_columns = df.columns.tolist()

    # 2. Add new columns (leave blank initially)
    new_columns = ["Contact for AM", "Responsible for inviting/Regional team", "Comments", "Meeting scheduled on"]
    for col in new_columns:
        df[col] = ""

    # 3. Connect to SQL DB
    base_dir = Path(__file__).resolve().parent.parent  # One level above /pages
    db_path = base_dir / "utils" / "database.db"

    if not db_path.exists():
        st.error(f"❌ Database file not found at: {db_path}")
        st.stop()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 4. Get unique organizations from Excel
    df.rename(columns={"Organization": "organization"}, inplace=True)
    orgs = tuple(df["organization"].dropna().unique())
    if orgs:
        placeholders = ",".join(["?"] * len(orgs))
        query = f"SELECT organization, contact_for_am FROM [IdM-Reporting-2-OrganizationalR] WHERE organization IN ({placeholders})"
        contact_df = pd.read_sql(query, conn, params=orgs)

        # Group and merge contacts
        contact_df = contact_df.groupby("organization")["contact_for_am"].apply(lambda x: ", ".join(x.unique())).reset_index()
        df = df.merge(contact_df, how="left", on="organization")
        df["Contact for AM"] = df["contact_for_am"]
        df.drop(columns=["contact_for_am"], inplace=True)

    # 5. Custom assignment logic for "Responsible for inviting/Regional team"
    def assign_responsible(row):
        division = str(row.get("Division", "")).strip()
        country = str(row.get("Country/Region", "")).strip()
        location = str(row.get("Location", "")).strip()
        organization = str(row.get("organization", "")).strip()
        contact_am = str(row.get("Contact for AM", "")).strip()

        # --- Specific case rules ---
        if division == "GS" and country == "CR":
            return "Mora Maria Fernanda (GS/PBX-AM)"
        if division == "GS" and country == "RO" and location == "Tim":
            return "Margea Petru-Marius (SO/ISG-AIM)"
        if country == "CN" and location == "Cgd":
            return "GS/RMX4"
        if "GS/ORS4-LA" in contact_am:
            return "LA team"
        if division == "GS" and country == "HU" and organization.startswith("GS/HRS"):
            return "SIMON BETTINA (C/DSO-HU)"

        # --- General country mapping ---
        country_team_mapping = {
            "US": "NA (US, CA) team",
            "CA": "NA (US, CA) team",
            "MX": "NA (MX) team",
            "BR": "LA team",
            "CN": "APAC team",
            "RU": "N/A"
        }
        return country_team_mapping.get(country, "GS/RMX4")  # Default fallback

    df["Responsible for inviting/Regional team"] = df.apply(assign_responsible, axis=1)

    st.subheader("Movers Report generation")
    st.dataframe(df)

    # 6. Download option
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
            workbook = writer.book
            worksheet = writer.sheets["Sheet1"]

            # Define formats
            header_format_blue = workbook.add_format({
                'bold': True, 'bg_color': '#4472C4', 'color': 'white', 'border': 1
            })
            header_format_green = workbook.add_format({
                'bold': True, 'bg_color': '#70AD47', 'color': 'white', 'border': 1
            })
            red_row_format = workbook.add_format({
            'bg_color': '#FFCCCC'  # Light red background
        })
            # Freeze header row
            worksheet.freeze_panes(1, 0)
            worksheet.set_row(0, 40)
            # Set column widths
            default_width = 8
            custom_widths = {
                "organization": 12,
                "Location": 8,
                "Contact for AM": 20,
                "Responsible for inviting/Regional team": 8
            }

            for idx, col in enumerate(df.columns):
                header_format = header_format_blue if col in original_columns else header_format_green
                worksheet.write(0, idx, col, header_format)
                width = custom_widths.get(col, default_width)
                worksheet.set_column(idx, idx, width)

            # Highlight rows where Manager Full Name appears more than once
            if "Manager Full Name" in df.columns:
                manager_counts = df["Manager Full Name"].value_counts()
                duplicated_managers = manager_counts[manager_counts > 1].index.tolist()

                for row_num, row in df.iterrows():
                    if row["Manager Full Name"] in duplicated_managers:
                        worksheet.set_row(row_num + 1, None, red_row_format)
        return output.getvalue()

    excel_bytes = convert_df_to_excel(df)
    st.download_button(
        label="Download Modified Excel",
        data=excel_bytes,
        file_name="modified_excel.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
