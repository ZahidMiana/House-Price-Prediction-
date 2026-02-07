import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Load the trained model, scaler, and encoder
@st.cache_resource
def load_models():
    with open('house_price_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('label_encoder.pkl', 'rb') as f:
        encoder = pickle.load(f)
    return model, scaler, encoder

model, scaler, encoder = load_models()

# Page configuration
st.set_page_config(
    page_title="House Price Predictor",
    page_icon="🏠",
    layout="wide"
)

# Title and description
st.title("🏠 California House Price Prediction")
st.markdown("### Enter house details to predict the median house value")

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("Location & Property Details")
    longitude = st.number_input("Longitude", value=-122.23, format="%.2f")
    latitude = st.number_input("Latitude", value=37.88, format="%.2f")
    housing_median_age = st.slider("Housing Median Age (years)", 1, 52, 25)
    
    total_rooms = st.number_input("Total Rooms", value=2000, step=100)
    total_bedrooms = st.number_input("Total Bedrooms", value=400, step=50)
    
with col2:
    st.subheader("Demographics & Income")
    population = st.number_input("Population", value=1000, step=100)
    households = st.number_input("Households", value=400, step=50)
    median_income = st.number_input("Median Income (tens of thousands)", value=3.5, format="%.2f")
    
    ocean_proximity = st.selectbox(
        "Ocean Proximity",
        options=['<1H OCEAN', 'INLAND', 'ISLAND', 'NEAR BAY', 'NEAR OCEAN']
    )

# Predict button
if st.button("🔮 Predict House Price", type="primary"):
    try:
        # Calculate engineered features
        rooms_per_household = total_rooms / households if households > 0 else 0
        population_per_household = population / households if households > 0 else 0
        bedrooms_per_room = total_bedrooms / total_rooms if total_rooms > 0 else 0
        
        # Encode ocean proximity
        ocean_proximity_encoded = encoder.transform([ocean_proximity])[0]
        
        # Create input dataframe
        input_data = pd.DataFrame({
            'longitude': [longitude],
            'latitude': [latitude],
            'housing_median_age': [housing_median_age],
            'total_rooms': [total_rooms],
            'total_bedrooms': [total_bedrooms],
            'population': [population],
            'households': [households],
            'median_income': [median_income],
            'rooms_per_household': [rooms_per_household],
            'population_per_household': [population_per_household],
            'bedrooms_per_room': [bedrooms_per_room],
            'ocean_proximity_encoded': [ocean_proximity_encoded]
        })
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        # Display results
        st.success("### Prediction Complete!")
        st.metric(
            label="Predicted Median House Value",
            value=f"${prediction:,.2f}",
            delta=None
        )
        
        # Additional information
        st.info(f"""
        **Property Summary:**
        - Location: ({latitude}, {longitude})
        - {total_bedrooms} bedrooms in {total_rooms} total rooms
        - {rooms_per_household:.2f} rooms per household
        - Ocean Proximity: {ocean_proximity}
        """)
        
        # Confidence interpretation
        if prediction < 150000:
            st.warning("💰 Budget-friendly property")
        elif prediction < 300000:
            st.info("💵 Mid-range property")
        else:
            st.success("💎 Premium property")
            
    except Exception as e:
        st.error(f"Error making prediction: {str(e)}")

# Sidebar with information
with st.sidebar:
    st.header("📊 About")
    st.write("""
    This app predicts California house prices using a Random Forest model.
    
    **Model Performance:**
    - R² Score: ~0.80
    - RMSE: ~$50,000
    
    **Key Features:**
    - Median Income (most important)
    - Location (lat/long)
    - Ocean Proximity
    - Population per household
    """)
    
    st.header("📝 Instructions")
    st.write("""
    1. Enter property details
    2. Set demographics info
    3. Select ocean proximity
    4. Click 'Predict' button
    """)
    
    st.header("⚙️ Model Info")
    st.write(f"Model: Random Forest Regressor")
    st.write(f"Features: 12 input features")
