import streamlit as st

st.set_page_config(page_title="Shopping List App", layout="centered")
st.title("Weekly Shopping List")

# Initialize session state if not already done
if 'pickup_items' not in st.session_state:
    st.session_state.pickup_items = []
if 'instore_items' not in st.session_state:
    st.session_state.instore_items = []

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
item = st.text_input("Item Name")
category = st.selectbox("Category", ["Pickup", "In-Store"])

if st.button("Add Item"):
    if item:
        if category == "Pickup":
            st.session_state.pickup_items.append(item)
        else:
            st.session_state.instore_items.append(item)
        st.experimental_rerun()

# Display shopping list
st.subheader("Pickup Items")
if st.session_state.pickup_items:
    for i, item in enumerate(st.session_state.pickup_items):
        st.markdown(f"- {item}")
else:
    st.caption("No pickup items yet.")

st.subheader("In-Store Items")
if st.session_state.instore_items:
    for i, item in enumerate(st.session_state.instore_items):
        st.markdown(f"- {item}")
else:
    st.caption("No in-store items yet.")
