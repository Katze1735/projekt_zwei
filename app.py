import streamlit as st
from supabase import create_client
import uuid

# -------------------------
# Supabase Connection
# -------------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Clothing Catalog")

# -------------------------
# Upload Section
# -------------------------

st.header("Upload Clothing Item")

uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"])

# IMAGE PREVIEW
if uploaded_file is not None:
    st.subheader("Preview")
    st.image(uploaded_file, width=300)

name = st.text_input("Item name")

clothing_type = st.selectbox(
    "Clothing type",
    ["shirt", "pants", "jacket", "hoodie", "shoes", "other"]
)

color = st.selectbox(
    "Color",
    ["black", "white", "blue", "red", "green", "yellow", "brown"]
)

if st.button("Upload"):
    if uploaded_file:

        file_id = str(uuid.uuid4())
        path = f"{file_id}_{uploaded_file.name}"

        # Upload to Supabase storage
        supabase.storage.from_("clothing-images").upload(
            path,
            uploaded_file.getvalue()
        )

        # Get public URL
        image_url = supabase.storage.from_("clothing-images").get_public_url(path)

        # Insert metadata into database
        supabase.table("clothing_items").insert({
            "name": name,
            "clothing_type": clothing_type,
            "color": color,
            "image_url": image_url
        }).execute()

        st.success("Item uploaded!")

# -------------------------
# Browse Section
# -------------------------

st.header("Browse Clothing")
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2F1.bp.blogspot.com%2F-ePC0IzZyyVs%2FTjIb-fgX1MI%2FAAAAAAAALBc%2F-eMi_QGmisI%2Fs1600%2FMRI%252528Magnetic%252BResonance%252BImaging%252529%252BScan%252BMachine%252B%2525287%252529.JPG&f=1&nofb=1&ipt=c31fafe21bb2e54953068314769073934d9f1b129b2e48562d4c649a2cd5b78c");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
type_filter = st.multiselect(
    "Filter by type",
    ["shirt", "pants", "jacket", "hoodie", "shoes", "other"]
)

color_filter = st.multiselect(
    "Filter by color",
    ["black", "white", "blue", "red", "green", "yellow", "brown"]
)

query = supabase.table("clothing_items").select("*")

if type_filter:
    query = query.in_("clothing_type", type_filter)

if color_filter:
    query = query.in_("color", color_filter)

response = query.execute()
items = response.data

# -------------------------
# Display Items
# -------------------------

cols = st.columns(4)

for i, item in enumerate(items):
    with cols[i % 4]:
        st.image(item["image_url"], use_container_width=True)
        st.caption(item["name"])
        st.write(f"{item['clothing_type']} | {item['color']}")
