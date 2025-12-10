import streamlit as st
import hashlib
import pandas as pd
import tempfile

def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def run_scan(area, hashset):
    matches = []
    total = 10_000_000

    progress = st.progress(0, text="Starting scan…")
    for i in range(total):
        subscriber = f"{i:07d}"
        full_number = f"{area}{subscriber}"
        h = md5_hex(full_number)

        if h in hashset:
            matches.append((full_number, h))

        if i % 100000 == 0:
            progress.progress(i / total, text=f"Scanning… {i:,}/{total:,}")

    progress.progress(1.0, text="Completed.")
    return matches


st.title("📞 MD5 Hash Checker (One Area Code | CSV Input | Opt-In Data Only)")

uploaded = st.file_uploader("Upload CSV File Containing MD5 Hashes", type=["csv"])

if uploaded is not None:
    # Load CSV
    df = pd.read_csv(uploaded)

    st.write(f"CSV loaded: **{df.shape[0]:,} rows**, **{df.shape[1]:,} columns**")

    # Let user pick which column contains the hashes
    column = st.selectbox("Select the column that contains MD5 hashes", df.columns)

    # Prepare hashset
    hashset = {
        str(v).strip().lower()
        for v in df[column].dropna().unique()
        if str(v).strip()
    }

    st.write(f"Using **{len(hashset):,} unique hashes** from column: `{column}`")

area = st.text_input("Area Code (3 digits)", max_chars=3)

if st.button("Run Comparison"):
    if uploaded is None:
        st.error("Please upload a CSV file first.")
        st.stop()

    if not area.isdigit() or len(area) != 3:
        st.error("Area code must be exactly 3 digits.")
        st.stop()

    st.write(f"Starting comparison for area code **{area}**…")

    # Run scan
    matches = run_scan(area, hashset)

    st.success(f"Done! Found **{len(matches):,}** matches.")

    # Download file
    if matches:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
            for num, h in matches:
                f.write(f"{num},{h}\n")
            temp_path = f.name

        with open(temp_path, "rb") as f:
            st.download_button(
                label="Download Matching Phone Numbers",
                data=f,
                file_name="matches.txt",
                mime="text/plain",
            )
