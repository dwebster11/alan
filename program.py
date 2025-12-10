import streamlit as st
import hashlib
import tempfile

def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()

def run_scan(area, hashset):
    matches = []
    total = 10_000_000

    progress = st.progress(0, text="Starting…")
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


st.title("Alan Program")

uploaded = st.file_uploader("Upload file of MD5 hashes (one per line)", type=["txt"])
area = st.text_input("Area Code (3 digits)", max_chars=3)

if st.button("Run Comparison"):
    if not uploaded:
        st.error("Please upload a hash file.")
        st.stop()

    if not area.isdigit() or len(area) != 3:
        st.error("Area code must be exactly 3 digits.")
        st.stop()

    # Load hashes
    st.write("Loading hashes…")
    hashset = {line.strip().lower() for line in uploaded.read().decode().splitlines() if line.strip()}

    st.write(f"Loaded **{len(hashset):,}** hashes. Beginning scan…")

    matches = run_scan(area, hashset)

    st.success(f"Done! Found **{len(matches):,}** matches.")

    # Save to temp file for download
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
                mime="text/plain"
            )
