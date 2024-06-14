import streamlit as st
import pandas as pd
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Nota Mas Fana",
    page_icon="💀",
    layout="centered",
)

dayname_dict = {
    'Monday': 'Senin',
    'Tuesday': 'Selasa',
    'Wednesday': 'Rabu',
    'Thursday': 'Kamis',
    'Friday': 'Jumat',
    'Saturday': 'Sabtu',
    'Sunday': 'Minggu'
}

# Format numbers to use dot as thousands separator
def format_number(number):
    return '{:,}'.format(number).replace(',', '.')

# Function to read data from CSV
def load_data():
    try:
        data = pd.read_csv('nota.csv')
    except FileNotFoundError:
        data = pd.DataFrame(columns=['tanggal', 'barang', 'jumlah', 'harga', 'total'])
    return data

# Function to save data to CSV
def save_data(data):
    data.to_csv('nota.csv', index=False)

# Function to calculate total price
def calculate_total(jumlah, harga):
    return jumlah * harga

# Function to delete a row
def delete_row(index):
    data = st.session_state.data
    data = data.drop(index).reset_index(drop=True)
    st.session_state.data = data
    save_data(data)
    st.success("Nota berhasil dihapus!")
    st.experimental_rerun()
    
def get_filtered_data(data):
    st.title("Total Keseluruhan Berdasarkan Tanggal")
    filter_date = st.date_input("Pilih Tanggal", value=datetime.now())
    filtered_data = data[data['tanggal'] == pd.to_datetime(filter_date).strftime('%Y-%m-%d')]
    if not filtered_data.empty:
        filtered_data['tanggal'] = pd.to_datetime(filtered_data['tanggal'])
        dayname = filtered_data['tanggal'].dt.day_name().iloc[0]
        dayname = dayname_dict[dayname]
        st.subheader(f"{dayname} Tanggal: {filter_date.strftime('%d-%m-%Y')}")
        st.subheader("Total Keseluruhan: Rp" + format_number(filtered_data['total'].sum()))
    else:
        st.write("Tidak ada data untuk tanggal tersebut.")
        
    st.title("Total Keseluruhan: Rp" + format_number(data['total'].sum()))

# Function to edit a row
def edit_row(index):
    data = st.session_state.data
    row = data.loc[index]

    # Use unique form key to differentiate forms
    with st.form(key=f'edit_form_{index}'):
        tanggal = st.date_input("Tanggal", value=pd.to_datetime(row['tanggal']))
        barang = st.text_input("Nama Barang", value=row['barang'])
        jumlah = st.number_input("Jumlah", min_value=0, step=1, value=int(row['jumlah']))
        harga = st.number_input("Harga per Satuan", min_value=1000, step=500, value=int(row['harga']))

        submit_button = st.form_submit_button(label="Update")

        if submit_button:
            # Update data directly
            data.at[index, 'tanggal'] = tanggal
            data.at[index, 'barang'] = barang
            data.at[index, 'jumlah'] = jumlah
            data.at[index, 'harga'] = harga
            data.at[index, 'total'] = calculate_total(jumlah, harga)

            # Save updated data
            st.session_state.data = data
            save_data(data)

            # Provide feedback to the user
            st.success("Nota berhasil diperbarui!")
            st.experimental_rerun()

# Load data from CSV if not already in session state
if 'data' not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

# Sidebar navigation
st.sidebar.title("Navigasi")
page = st.sidebar.selectbox("Pilih Halaman", ["Tambah Nota", "Kelola Nota"])

# Add Note Page
if page == "Tambah Nota":
    st.title("Tambah Nota Baru")

    # Form input
    with st.form(key='nota_form'):
        tanggal = st.date_input("Tanggal", value=datetime.now())
        barang = st.text_input("Nama Barang")
        jumlah = st.number_input("Jumlah", min_value=0, step=1)
        harga = st.number_input("Harga per Satuan", min_value=1000, step=500)
        submit_button = st.form_submit_button(label="Tambahkan")
        

    get_filtered_data(data)
    # If form is submitted, add new data to CSV
    if submit_button:
        total = calculate_total(jumlah, harga)
        new_row = {'tanggal': tanggal, 'barang': barang, 'jumlah': jumlah, 'harga': harga, 'total': total}

        # Convert new_row to a DataFrame if it's a dictionary
        if isinstance(new_row, dict):
            new_row = pd.DataFrame([new_row])

        # Append the new row using pd.concat
        data = pd.concat([data, new_row], ignore_index=True)
        st.session_state.data = data

        save_data(data)
        st.success(f"Nota untuk {barang} ditambahkan!")
        st.experimental_rerun()
    # Total keseluruhan berdasarkan tanggal


# Manage Notes Page (Edit and Delete)
elif page == "Kelola Nota":
    st.title("Kelola Nota")

    # Add date input to filter data
    st.subheader("Filter Nota Berdasarkan Tanggal")
    filter_date = st.date_input("Pilih Tanggal", value=datetime.now())

    if not data.empty:
        data['tanggal'] = pd.to_datetime(data['tanggal'])  # Ensure 'tanggal' is datetime
        filtered_data = data[data['tanggal'] == pd.to_datetime(filter_date)]

        if not filtered_data.empty:
            st.write(f"Menampilkan nota untuk tanggal: {filter_date.strftime('%d-%m-%Y')}")
            for index, row in filtered_data.iterrows():
                st.write(row.to_frame().T.to_html(index=False), unsafe_allow_html=True)
                if st.button("Edit", key=f"edit_{index}"):
                    edit_row(index)
                if st.button("Hapus", key=f"delete_{index}"):
                    delete_row(index)
        else:
            st.write("Tidak ada data untuk tanggal tersebut.")
    else:
        st.write("Tidak ada data untuk ditampilkan.")

# Display total price overall
total_keseluruhan = data['total'].sum()
st.sidebar.subheader(f"Total Keseluruhan: Rp{format_number(total_keseluruhan)}")
