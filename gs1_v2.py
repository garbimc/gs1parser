import streamlit as st
import pyperclip  # For copying text to clipboard

# Set page configuration
st.set_page_config(
    page_title="GS1 Barcode Parser",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stTextInput input {
        font-size: 16px;
        padding: 10px;
    }
    .stMarkdown h1 {
        color: #4CAF50;
    }
    .copy-button {
        background-color: #008CBA;
        color: white;
        border-radius: 5px;
        padding: 5px 10px;
        font-size: 14px;
        margin-left: 10px;
    }
    .copy-button:hover {
        background-color: #007B9E;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def parse_gs1_barcode(barcode):
    parsed_data = {}
    i = 0
    while i < len(barcode):
        if barcode[i:i+2] == '01':
            parsed_data['SKU'] = barcode[i+2:i+16]  # SKU is 14 characters long
            i += 16
        elif barcode[i:i+2] == '17':
            parsed_data['ExpirationDate'] = barcode[i+2:i+8]  # Expiration date is 6 characters long
            i += 8
        elif barcode[i:i+2] == '10':
            # Lot number ends when the '240' identifier starts
            next_index = barcode.find('240', i+2)
            if next_index == -1:
                parsed_data['LotNumber'] = barcode[i+2:]
                i = len(barcode)
            else:
                parsed_data['LotNumber'] = barcode[i+2:next_index]
                i = next_index
        elif barcode[i:i+2] == '21':
            # Serial number ends when the '240' identifier starts
            next_index = barcode.find('240', i+2)
            if next_index == -1:
                parsed_data['SerialNumber'] = barcode[i+2:]
                i = len(barcode)
            else:
                parsed_data['SerialNumber'] = barcode[i+2:next_index]
                i = next_index
        elif barcode[i:i+3] == '240':
            parsed_data['UDI'] = barcode[i+3:i+13]  # UDI is 10 characters long
            i += 13
        elif barcode[i:i+2] == '11':
            parsed_data['ManufactureDate'] = barcode[i+2:i+8]  # Manufacture date is 6 characters long
            i += 8
        elif barcode[i:i+2] == '15':
            parsed_data['BestBefore'] = barcode[i+2:i+8]  # Best before date is 6 characters long
            i += 8
        else:
            i += 1
    return parsed_data

def main():
    st.title("📋 GS1 Barcode Parser")
    st.markdown("### Parse GS1 barcodes with ease!")
    barcode = st.text_input("Enter the GS1 Barcode:", placeholder="e.g., 010871472998502017260626212294602400304215383")

    if barcode:
        parsed_data = parse_gs1_barcode(barcode)
        st.write("### Parsed GS1 Barcode Information:")
        for key, value in parsed_data.items():
            st.write(f"**{key}:** {value}")
            # Add a button to copy the value to clipboard
            if st.button(f"Copy {key}", key=f"copy_{key}"):
                pyperclip.copy(value)
                st.success(f"Copied {key} to clipboard!")

if __name__ == "__main__":
    main()