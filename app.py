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
        path = f"{file_id}.jpg"

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
