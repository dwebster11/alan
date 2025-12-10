import streamlit as st
import hashlib
import pandas as pd
import tempfile

def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def generate_variants(area, subscriber):
    """Generate formatting variants for a given number."""
    base10 = f"{area}{subscriber}"
    a, b, c = area, subscriber[:3], subscriber[3:]

    variants = [
        base10,                           # 4151234567
        "1" + base10,                     # 14151234567
        "+1" + base10,                    # +14151234567

        f"{a}-{b}-{c}",                   # 415-123-4567
        f"({a}){b}-{c}",                  # (415)123-4567
        f"({a}) {b}-{c}",                 # (415) 123-4567
        f"{a} {b} {c}",                   # 415 123 4567
        f"{a}.{b}.{c}",                   # 415.123.4567

        f"1-{a}-{b}-{c}",                 # 1-415-123-4567
        f"+1-{a}-{b}-{c}",                # +1-415-123-4567
        f"+1 ({a}) {b}-{c}",              # +1 (415) 123-4567
        f"+1 {a} {b} {c}",                # +1 415 123 4567
    ]

    # remove duplicates just in case
    return list(set(variants))

def run_scan(area, hashset):
    matches = []
    total = 10_000_000

    progress = st.progress(0, text="Starting scan…")

    for i in range(total):
        subscriber = f"{i:07d}"

        # Generate all variants
        variants = generate_variants(area, subscriber)

        for v in variants:
            h = md5_hex(v)
            if h in hashset:
                matches.append((v, h))
                break  # stop after first match

        # Update progress
        if i % 100000 == 0:
            progress.progress(i / total, text=f"Scanning… {i:,}/{total:,}")

    progress.progress(1.0, text="Completed.")
    return matches


# ------------------------------
# Streamlit UI
# ------------------------------
st.title("Alan Project)")

uploaded = st.file_uploader("Upload CSV", type=["csv"])

if uploaded is not None:
    df = pd.read_csv(uploaded)
    st.write(f"Loaded CSV: **{df.shape[0]:,} rows**, **{df.shape[1]:,} columns**")

    column = st.selectbox("Select the column containing MD5 hashes", df.columns)

    hashset = {
        str(v).strip().lower()
        for v in df[column].dropna().unique()
        if str(v).strip()
    }

    st.write(f"Using **{len(hashset):,} unique hashes**")

area = st.text_input("Area Code (3 digits)", max_chars=3)

if st.button("Run Comparison"):
    if uploaded is None:
        st.error("Upload a CSV first.")
        st.stop()

    if not area.isdigit() or len(area) != 3:
        st.error("Area code must be exactly 3 digits.")
        st.stop()

    st.write(f"Starting comparison for area code **{area}**…")

    matches = run_scan(area, hashset)

    st.success(f"Done! Found **{len(matches):,}** matches.")

    if matches:
        with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as f:
            for num, h in matches:
                f.write(f"{num},{h}\n")
            temp_path = f.name

        with open(temp_path, "rb") as f:
            st.download_button(
                label="Download Matches",
                data=f,
                file_name="matches.txt",
                mime="text/plain",
            )
