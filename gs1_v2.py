import streamlit as st
import pyperclip  # For copying text to clipboard
from barcode import EAN13
from barcode.writer import ImageWriter
from io import BytesIO

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
    .container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def generate_ean13_barcode(data):
    """Generate an EAN-13 barcode and return it as an image."""
    # Ensure the data is 12 or 13 digits long
    if len(data) < 12:
        data = data.ljust(12, '0')  # Pad with zeros if necessary
    elif len(data) > 13:
        data = data[:13]  # Truncate to 13 digits
    # Create an EAN-13 barcode with smaller size
    writer = ImageWriter()
    writer.set_options({
        'module_width': 0.2,  # Reduce the width of each barcode module
        'module_height': 10,  # Reduce the height of the barcode
        'font_size': 8,       # Reduce the font size of the barcode text
        'quiet_zone': 2       # Reduce the quiet zone (empty space around the barcode)
    })
    ean13 = EAN13(data, writer=writer)
    buffer = BytesIO()
    ean13.write(buffer)
    buffer.seek(0)
    return buffer

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
            # Lot number ends when the '240' identifier starts or GS character is found
            next_index = min(
                barcode.find('240', i+2),
                barcode.find('', i+2)
            )
            if next_index == -1:
                parsed_data['LotNumber'] = barcode[i+2:]
                i = len(barcode)
            else:
                parsed_data['LotNumber'] = barcode[i+2:next_index]
                i = next_index
        elif barcode[i:i+2] == '21':
            # Serial number ends when the '240' identifier starts or GS character is found
            next_index = min(
                barcode.find('240', i+2),
                barcode.find('', i+2)
            )
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
        
        # Use columns to create a better layout
        for key, value in parsed_data.items():
            with st.container():
                st.markdown('<div class="container">', unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{key}:** {value}")
                with col2:
                    if st.button(f"Copy {key}", key=f"copy_{key}"):
                        pyperclip.copy(value)
                        st.success(f"Copied {key} to clipboard!")
                # Generate and display EAN-13 barcode
                st.write(f"**EAN-13 Barcode for {key}:**")
                try:
                    barcode_image = generate_ean13_barcode(value)
                    st.image(barcode_image, caption=f"{key}: {value}", use_column_width=False, width=200)  # Adjust width here
                except Exception as e:
                    st.error(f"Failed to generate EAN-13 barcode for {key}: {e}")
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()