import streamlit as st
import requests
import json

st.set_page_config(
    page_title="AI Property Description Writer",
    page_icon="🏡",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px;
        font-size: 16px;
        font-weight: bold;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
    }
    .description-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        min-height: 300px;
    }
    .info-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

if 'description' not in st.session_state:
    st.session_state.description = ""
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

st.title("🏡 AI Land Property Description Writer")
st.markdown("Generate professional land property descriptions instantly using AI")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Groq API Key",
        type="password",
        value=st.session_state.api_key,
        help="Get your free API key from console.groq.com"
    )
    st.session_state.api_key = api_key
    
    st.markdown("---")
    st.markdown("""
    ### How to Use:
    1. Get free API key from console.groq.com
    2. Enter API key in the field above
    3. Fill property details
    4. Click Generate
    5. Edit and copy description
    
    ### Features:
    - AI-powered descriptions
    - Regenerate for variations
    - Fully editable output
    - Multiple property types
    - Professional formatting
    """)

if not st.session_state.api_key:
    st.markdown("""
    <div class="info-box">
        <h4>API Key Required</h4>
        <p>Please enter your Groq API key in the sidebar to get started.</p>
        <p>Get your free API key from <a href="https://console.groq.com" target="_blank">console.groq.com</a></p>
    </div>
    """, unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    st.header("📋 Property Details")
    
    property_type = st.selectbox(
        "Property Type",
        ["Residential Plot", "Commercial Plot", "Agricultural Land", "Industrial Plot", "Farm Land"]
    )
    
    location = st.text_input(
        "Location *",
        placeholder="e.g., Near Highway, City Center",
        help="Enter the property location"
    )
    
    col_area1, col_area2 = st.columns([2, 1])
    with col_area1:
        area = st.text_input(
            "Area *",
            placeholder="1000",
            help="Enter the property area"
        )
    with col_area2:
        unit = st.selectbox(
            "Unit",
            ["sq ft", "sq yards", "acres", "hectares"]
        )
    
    price = st.text_input(
        "Price",
        placeholder="e.g., ₹50 Lakhs",
        help="Enter the property price"
    )
    
    col_fr1, col_fr2 = st.columns(2)
    with col_fr1:
        facing = st.selectbox(
            "Facing",
            ["East", "West", "North", "South", "North-East", "South-East", "North-West", "South-West"]
        )
    with col_fr2:
        road_width = st.text_input(
            "Road Width",
            placeholder="e.g., 40 ft"
        )
    
    surroundings = st.text_input(
        "Surroundings",
        placeholder="Schools, hospitals, markets nearby",
        help="What's around the property?"
    )
    
    amenities = st.text_input(
        "Amenities",
        placeholder="Water, electricity, drainage",
        help="Available amenities"
    )
    
    legal_status = st.selectbox(
        "Legal Status",
        ["Clear Title", "Approved Layout", "RERA Approved", "Freehold", "Leasehold"]
    )
    
    additional_info = st.text_area(
        "Additional Information",
        placeholder="Any other details...",
        height=100
    )
    
    seo_keywords = st.text_input(
        "SEO Keywords (Optional)",
        placeholder="e.g., prime location, investment opportunity, gated community",
        help="Add keywords for better SEO optimization"
    )
    
    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        generate_button = st.button(
            "Generate Description", 
            disabled=not (st.session_state.api_key and location and area), 
            use_container_width=True
        )
    with col_btn2:
        regenerate_button = st.button(
            "Regenerate", 
            disabled=not (st.session_state.api_key and location and area and st.session_state.description), 
            use_container_width=True
        )

with col2:
    st.header("📄 Generated Description")
    
    def generate_description_from_api(temperature=0.7):
        prompt = f"""Write a professional and attractive property description for a land listing based on the following details:

Property Type: {property_type}
Location: {location}
Area: {area} {unit}
Price: {price if price else 'Not specified'}
Facing: {facing}
Road Width: {road_width if road_width else 'Not specified'}
Surroundings: {surroundings if surroundings else 'Not specified'}
Amenities: {amenities if amenities else 'Not specified'}
Legal Status: {legal_status}
Additional Information: {additional_info if additional_info else 'None'}
SEO Keywords to include: {seo_keywords if seo_keywords else 'None'}

Write a compelling description that highlights the key features, location advantages, and investment potential. Naturally incorporate the SEO keywords throughout the description for better search engine optimization. Keep it professional, engaging, and around 150-200 words. Make sure the keywords flow naturally in the text."""

        with st.spinner("Generating description..."):
            try:
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {st.session_state.api_key}"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": temperature,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.description = data['choices'][0]['message']['content']
                    st.success("Description generated successfully!")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
                    st.error("Please check your API key and try again.")
            
            except Exception as e:
                st.error(f"Error generating description: {str(e)}")
    
    if generate_button or regenerate_button:
        if not st.session_state.api_key:
            st.error("Please enter your Groq API key in the sidebar!")
        elif not location or not area:
            st.error("Please fill in at least Location and Area fields!")
        else:
            temperature = 0.9 if regenerate_button else 0.7
            generate_description_from_api(temperature)
    
    if st.session_state.description:
        col_act1, col_act2, col_act3 = st.columns(3)
        with col_act1:
            if st.button("Copy to Clipboard", use_container_width=True):
                st.code(st.session_state.description, language=None)
                st.success("Ready to copy! Select the text above.")
        with col_act2:
            st.download_button(
                label="Download",
                data=st.session_state.description,
                file_name="property_description.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_act3:
            if st.button("Clear", use_container_width=True):
                st.session_state.description = ""
                st.rerun()
        
        st.markdown("---")
        
        edited_description = st.text_area(
            "Edit Description (if needed)",
            value=st.session_state.description,
            height=350,
            help="You can edit the generated description here"
        )
        st.session_state.description = edited_description
    else:
        st.markdown("""
        <div class="description-box">
            <div style="text-align: center; padding: 50px;">
                <h3 style="color: #666;">No Description Yet</h3>
                <p style="color: #999;">Fill in the property details and click "Generate Description" to create your listing</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>Made with Streamlit & Groq AI | Get your free API key at <a href="https://console.groq.com" target="_blank">console.groq.com</a></p>
</div>
""", unsafe_allow_html=True)
