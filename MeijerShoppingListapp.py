import streamlit as st

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
if 'delete_index' not in st.session_state:
    st.session_state.delete_index = None
if 'delete_category' not in st.session_state:
    st.session_state.delete_category = None

trigger_rerun = False

# Sidebar for actions
with st.sidebar:
    st.header("Options")
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
    ))
else:
    item = st.text_input("Item Name")

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
        trigger_rerun = True

# Display shopping list with edit/delete icons
def display_list(items, category):
    for i, item in enumerate(items):
        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.markdown(f"- {item}")
        with col2:
            if st.button("✏️", key=f"edit_{category}_{i}"):
                st.session_state.edit_index = i
                st.session_state.edit_category = category
                st.experimental_rerun()
        with col3:
            if st.button("❌", key=f"delete_{category}_{i}"):
                st.session_state.delete_index = i
                st.session_state.delete_category = category

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

# Handle deletion after loop
delete_index = st.session_state.delete_index
delete_category = st.session_state.delete_category
if delete_index is not None and delete_category is not None:
    if delete_category == "Pickup" and 0 <= delete_index < len(st.session_state.pickup_items):
        st.session_state.pickup_items.pop(delete_index)
        trigger_rerun = True
    elif delete_category == "In-Store" and 0 <= delete_index < len(st.session_state.instore_items):
        st.session_state.instore_items.pop(delete_index)
        trigger_rerun = True
    st.session_state.delete_index = None
    st.session_state.delete_category = None

# Trigger rerun at the end only if flagged
if trigger_rerun:
    st.experimental_rerun()
