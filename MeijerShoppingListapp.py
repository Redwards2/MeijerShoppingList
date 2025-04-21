import streamlit as st
import re
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Shopping List App", layout="centered")
st.title("Weekly Shopping List")

# Initialize session state if not already done
if 'pickup_items' not in st.session_state:
    st.session_state.pickup_items = []
if 'instore_items' not in st.session_state:
    st.session_state.instore_items = []
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None
if 'edit_category' not in st.session_state:
    st.session_state.edit_category = None
if 'new_item' not in st.session_state:
    st.session_state.new_item = ""
if 'saved_lists' not in st.session_state:
    st.session_state.saved_lists = {}

# Basic category keyword matching (can expand later)
def detect_category(item_name):
    item_lower = item_name.lower()
    if any(word in item_lower for word in ["milk", "eggs", "bread", "butter", "juice"]):
        return "Pickup"
    return "In-Store"

# Aisle info scraping function
def get_aisle_info(item_name):
    query = item_name.replace(" ", "+")
    search_url = f"https://www.meijer.com/search/{query}.html"
    try:
        response = requests.get(search_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        link_tag = soup.select_one("a.product-tile--title__link")
        if not link_tag:
            return None
        product_url = "https://www.meijer.com" + link_tag.get("href")
        product_response = requests.get(product_url, timeout=10)
        product_soup = BeautifulSoup(product_response.text, "html.parser")
        aisle_tag = product_soup.find(string=re.compile("Aisle.*Section", re.IGNORECASE))
        if aisle_tag:
            return aisle_tag.strip()
    except:
        return None
    return None

# Sidebar for actions
with st.sidebar:
    st.header("Options")

    st.subheader("💾 Save Current List")
    save_name = st.text_input("List Name", key="save_input")
    if st.button("Save List") and save_name:
        st.session_state.saved_lists[save_name] = {
            "pickup": list(st.session_state.pickup_items),
            "instore": list(st.session_state.instore_items),
        }
        st.success(f"Saved list as '{save_name}'")

    st.subheader("📂 Load Saved List")
    if st.session_state.saved_lists:
        list_names = list(st.session_state.saved_lists.keys())
        selected_list = st.selectbox("Select a list to load", list_names)
        if st.button("Load List"):
            data = st.session_state.saved_lists[selected_list]
            st.session_state.pickup_items = data.get("pickup", [])
            st.session_state.instore_items = data.get("instore", [])
            st.success(f"Loaded list: {selected_list}")
    else:
        st.caption("No saved lists yet.")

    st.markdown("---")
    if st.button("Clear List"):
        st.session_state.pickup_items = []
        st.session_state.instore_items = []
    if st.button("Sample List"):
        st.session_state.pickup_items = ["Milk", "Eggs"]
        st.session_state.instore_items = ["Bananas", "Chicken"]

# Input section
st.subheader("Add New Item")
if st.session_state.edit_index is not None:
    item = st.text_input("Edit Item", value=(
        st.session_state.pickup_items[st.session_state.edit_index]
        if st.session_state.edit_category == "Pickup"
        else st.session_state.instore_items[st.session_state.edit_index]
    ), key="edit_input")
else:
    item = st.text_input("Item Name", value=st.session_state.new_item, key="new_input")

# Handle safe selectbox default index
default_index = 0
if st.session_state.edit_category == "In-Store":
    default_index = 1

category = st.selectbox("Category", ["Pickup", "In-Store"], index=default_index)

if st.button("Save Item"):
    if item:
        if st.session_state.edit_index is not None:
            if category == "Pickup":
                st.session_state.pickup_items[st.session_state.edit_index] = item
            else:
                st.session_state.instore_items[st.session_state.edit_index] = item
            st.session_state.edit_index = None
            st.session_state.edit_category = None
        else:
            if category == "Pickup":
                st.session_state.pickup_items.append(item)
            else:
                st.session_state.instore_items.append(item)
        st.session_state.new_item = ""

# Import texted list
st.subheader("📥 Import Pasted List")
import_text = st.text_area("Paste your shopping list here (comma or newline separated):", height=100)
if st.button("Import List"):
    if import_text.strip():
        raw_items = [x.strip() for x in import_text.replace(",", "\n").splitlines() if x.strip()]
        for item in raw_items:
            category = detect_category(item)
            if category == "Pickup":
                st.session_state.pickup_items.append(item)
            else:
                st.session_state.instore_items.append(item)
        st.success(f"Imported {len(raw_items)} items using auto-categorization!")

# Display shopping list with edit/delete/fetch aisle icons
def display_list(items, category):
    for i, item in enumerate(items):
        col1, col2, col3, col4 = st.columns([6, 1, 1, 2])
        with col1:
            st.markdown(f"- {item}")
        with col2:
            if st.button("✏️", key=f"edit_{category}_{i}"):
                st.session_state.edit_index = i
                st.session_state.edit_category = category
        with col3:
            if st.button("❌", key=f"delete_{category}_{i}"):
                if category == "Pickup" and 0 <= i < len(st.session_state.pickup_items):
                    st.session_state.pickup_items.pop(i)
                elif category == "In-Store" and 0 <= i < len(st.session_state.instore_items):
                    st.session_state.instore_items.pop(i)
        with col4:
            if st.button("🛒 Aisle", key=f"aisle_{category}_{i}"):
                aisle_info = get_aisle_info(item)
                if aisle_info:
                    items[i] = f"{item} ({aisle_info})"
                else:
                    st.warning("Aisle info not found.")

st.subheader("Pickup Items")
if st.session_state.pickup_items:
    display_list(st.session_state.pickup_items, "Pickup")
else:
    st.caption("No pickup items yet.")

st.subheader("In-Store Items")
if st.session_state.instore_items:
    display_list(st.session_state.instore_items, "In-Store")
else:
    st.caption("No in-store items yet.")
