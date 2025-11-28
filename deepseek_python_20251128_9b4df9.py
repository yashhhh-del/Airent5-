"""
🏠 AI Property Management & Description Generator
Combined Property Management System + AI Description Generator
Premium Quality with Groq Free API + Property Type Guide
"""

import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime
from io import BytesIO
import time

# Page Configuration
st.set_page_config(
    page_title="AI Property Management System",
    page_icon="🏠",
    layout="wide"
)

# ==================== PROPERTY TYPE GUIDE ====================
class PropertyTypeGuide:
    """Property Type Information System"""
    
    def __init__(self):
        self.property_types = {
            "Agricultural": {
                "description": "Kheti ki zameen - Fasal ugane ke liye",
                "features": ["Farming activities", "Usually shahar se bahar", "Irrigation facilities", "Crop cultivation"],
                "documents": ["7/12 Extract", "Ferfar", "Property Card", "NOC"],
                "restrictions": ["Construction usually not allowed", "Conversion required for building"]
            },
            "Residential": {
                "description": "Ghar/makaan banane ke liye",
                "features": ["NA approved", "Colony/Society mein", "Basic amenities", "Residential construction allowed"],
                "documents": ["Sale Deed", "Property Card", "NA Order", "Building Plan Approval"],
                "restrictions": ["Only residential construction", "Height restrictions apply"]
            },
            "Commercial": {
                "description": "Dukaan, office, showroom ke liye",
                "features": ["Business activities allowed", "Main road location", "High footfall areas", "Parking facility"],
                "documents": ["Sale Deed", "Trade License", "Shop Act License", "Fire NOC"],
                "restrictions": ["Business hours regulations", "Specific business types allowed"]
            },
            "Industrial": {
                "description": "Factory, warehouse, manufacturing ke liye",
                "features": ["Large area", "Industrial zone", "Heavy machinery allowed", "Loading facilities"],
                "documents": ["Sale Deed", "Industrial License", "Pollution Clearance", "Factory License"],
                "restrictions": ["Environmental clearance required", "Specific industry zones"]
            },
            "Institutional": {
                "description": "School, hospital, college ke liye",
                "features": ["Public use", "Educational/Medical facilities", "Large open spaces", "Accessibility"],
                "documents": ["Sale Deed", "Trust/Society Registration", "NOC from authorities", "Building approval"],
                "restrictions": ["Only institutional use", "Strict regulations"]
            },
            "Mixed-Use": {
                "description": "Residential + Commercial dono allowed",
                "features": ["Flexible usage", "Niche shop, upar ghar", "Dual income potential", "Urban areas"],
                "documents": ["Sale Deed", "Mixed-Use Permission", "Building Plan", "Trade License"],
                "restrictions": ["Proportion restrictions", "Separate entries required"]
            }
        }
    
    def display_guide(self):
        """Display property type guide in Streamlit"""
        st.header("🏘️ Property Type Guide")
        st.caption("Comprehensive information about different property types")
        
        # Property type selection
        selected_type = st.selectbox(
            "Select Property Type",
            list(self.property_types.keys()),
            key="property_guide_select"
        )
        
        if selected_type:
            prop_data = self.property_types[selected_type]
            
            # Display property information
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader(f"📖 {selected_type} Property")
                st.info(f"**Description:** {prop_data['description']}")
                
                st.markdown("#### ✅ Key Features")
                for feature in prop_data["features"]:
                    st.markdown(f"✓ {feature}")
                
                st.markdown("#### 📄 Required Documents")
                for doc in prop_data["documents"]:
                    st.markdown(f"📄 {doc}")
            
            with col2:
                st.markdown("#### ⚠️ Restrictions & Regulations")
                for restriction in prop_data["restrictions"]:
                    st.markdown(f"⚠️ {restriction}")
                
                # Quick stats
                st.markdown("#### 📊 Quick Info")
                st.metric("Features Count", len(prop_data["features"]))
                st.metric("Documents Required", len(prop_data["documents"]))
                st.metric("Key Restrictions", len(prop_data["restrictions"]))

# ==================== INTERACTIVE PARSER ====================
class InteractiveParser:
    """Parser with interactive column mapping"""
    
    REQUIRED_FIELDS = {
        'property_type': 'Type of property (flat, villa, pg, shop, office)',
        'bhk': 'Number of bedrooms (2, 3, 1 BHK)',
        'area_sqft': 'Area in square feet',
        'city': 'City name (Mumbai, Delhi, etc)',
        'locality': 'Area/Locality name',
        'furnishing_status': 'Furnishing (unfurnished, semi, fully)',
        'rent_amount': 'Monthly rent amount',
        'deposit_amount': 'Security deposit amount',
        'available_from': 'Date when available',
        'preferred_tenants': 'Type of tenants (Family, Bachelor, etc)'
    }
    
    def __init__(self):
        self.errors = []
    
    def read_file(self, uploaded_file):
        """Read file without any changes"""
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            return df
        except Exception as e:
            self.errors.append(f"Error: {str(e)}")
            return None
    
    def apply_mapping(self, df, mapping):
        """Apply user's column mapping"""
        return df.rename(columns=mapping)
    
    def clean_and_process(self, df):
        """Clean and process data"""
        properties = []
        
        for idx, row in df.iterrows():
            try:
                # Parse amenities
                amenities = []
                if 'amenities' in row.index and pd.notna(row.get('amenities')):
                    amenities = [a.strip() for a in str(row['amenities']).split(',')]
                
                # Parse date
                available_from = row.get('available_from', datetime.now().date())
                if isinstance(available_from, str):
                    available_from = pd.to_datetime(available_from).date()
                elif isinstance(available_from, pd.Timestamp):
                    available_from = available_from.date()
                
                properties.append({
                    'property_type': str(row['property_type']).lower().strip(),
                    'bhk': str(row['bhk']).strip(),
                    'area_sqft': int(float(row['area_sqft'])),
                    'city': str(row['city']).strip(),
                    'locality': str(row['locality']).strip(),
                    'landmark': str(row.get('landmark', '')).strip(),
                    'floor_no': int(float(row['floor_no'])) if pd.notna(row.get('floor_no')) else None,
                    'total_floors': int(float(row['total_floors'])) if pd.notna(row.get('total_floors')) else None,
                    'furnishing_status': str(row['furnishing_status']).lower().strip(),
                    'rent_amount': float(row['rent_amount']),
                    'deposit_amount': float(row['deposit_amount']),
                    'available_from': str(available_from),
                    'preferred_tenants': str(row['preferred_tenants']).strip(),
                    'amenities': amenities,
                    'rough_description': str(row.get('rough_description', '')).strip(),
                })
            except Exception as e:
                self.errors.append(f"Row {idx+2}: {str(e)}")
        
        return properties

# ==================== AI GENERATION ====================
def test_groq_api(api_key):
    """Test Groq API connection with simple request"""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key.strip()}"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "Say 'API is working!'"}],
                "temperature": 0.5,
                "max_tokens": 50
            },
            timeout=15
        )
        
        if response.status_code == 200:
            return True, "✅ API Connection Successful!"
        else:
            return False, f"Error {response.status_code}: {response.text[:200]}"
    except Exception as e:
        return False, f"Connection Error: {str(e)}"

def generate_with_groq(property_data, api_key, retry_count=3, variation_seed=0):
    """Generate PREMIUM description using Groq API with variation support"""
    
    # Variation prompts for different creative angles
    variation_prompts = [
        {
            'focus': 'lifestyle and experience',
            'tone': 'aspirational and emotional',
            'instruction': 'Focus on the lifestyle transformation and daily experiences this property offers. Paint a vivid picture of morning routines, evening relaxation, and the joy of living here.'
        },
        {
            'focus': 'investment value and practicality',
            'tone': 'professional and value-driven',
            'instruction': 'Emphasize the practical benefits, value for money, and smart investment aspects. Highlight cost savings, appreciation potential, and financial wisdom of this choice.'
        },
        {
            'focus': 'location benefits and connectivity',
            'tone': 'convenience-focused and modern',
            'instruction': 'Highlight the strategic location, connectivity advantages, and nearby conveniences. Focus on how this location saves time, offers accessibility, and enhances daily commute.'
        },
        {
            'focus': 'comfort and luxury features',
            'tone': 'premium and sophisticated',
            'instruction': 'Emphasize the premium features, comfort elements, and luxurious living experience. Use elegant language to describe the finer details and upscale amenities.'
        },
        {
            'focus': 'community and safety',
            'tone': 'warm and family-oriented',
            'instruction': 'Focus on the safe neighborhood, community aspects, and family-friendly environment. Highlight security features, neighbor relations, and child-friendly spaces.'
        }
    ]
    
    # Select variation based on seed
    variation = variation_prompts[variation_seed % len(variation_prompts)]
    
    for attempt in range(retry_count):
        try:
            # Clean API key
            api_key = api_key.strip()
            
            bhk = property_data['bhk']
            prop_type = property_data['property_type'].title()
            locality = property_data['locality']
            city = property_data['city']
            district = property_data.get('district', '')
            state = property_data.get('state', '')
            pincode = property_data.get('pincode', '')
            area = property_data['area_sqft']
            rent = property_data['rent_amount']
            furnishing = property_data['furnishing_status']
            amenities = ', '.join(property_data['amenities']) if property_data['amenities'] else 'Standard amenities'
            tenants = property_data['preferred_tenants']
            deposit = property_data['deposit_amount']
            available = property_data['available_from']
            nearby = ', '.join(property_data.get('nearby_points', []))
            landmark = property_data.get('landmark', '')
            floor_no = property_data.get('floor_no', '')
            total_floors = property_data.get('total_floors', '')
            maintenance = property_data.get('maintenance', 0)
            water_supply = ', '.join(property_data.get('water_supply', []))
            water_availability = property_data.get('water_availability', '')
            
            # Include rough_description in prompt
            rough_desc = property_data.get('rough_description', '').strip()
            rough_desc_section = ""
            if rough_desc:
                rough_desc_section = f"""

**Owner's Additional Notes/Description:**
"{rough_desc}"
(IMPORTANT: Please incorporate these owner-provided details naturally and prominently into the description. These are unique selling points!)
"""
            
            # Build full location string
            full_location = f"{locality}, {city}"
            if district:
                full_location += f", {district}"
            if state:
                full_location += f", {state}"
            if pincode:
                full_location += f" - {pincode}"
            
            # Build location details with landmark
            location_details = full_location
            if landmark:
                location_details += f" (Near {landmark})"
            
            # Build floor info
            floor_info = ""
            if floor_no and total_floors:
                floor_info = f"\n- Floor: {floor_no} of {total_floors} floors"
            
            # Build maintenance info
            maintenance_info = ""
            if maintenance and maintenance > 0:
                maintenance_info = f"\n- Maintenance: ₹{maintenance}/month"
            
            # Build water supply info
            water_info = ""
            if water_supply:
                water_info = f"\n- Water Supply: {water_supply} ({water_availability})"

            prompt = f"""You are an expert real estate copywriter specializing in premium property listings that drive high engagement and conversions.

Create a compelling, professional rental property listing for:

**Property Details:**
- Type: {bhk} BHK {prop_type}
- Location: {location_details}
- Area: {area} square feet{floor_info}
- Monthly Rent: ₹{rent:,}
- Security Deposit: ₹{deposit:,}{maintenance_info}{water_info}
- Furnishing: {furnishing} furnished
- Amenities: {amenities}
- Preferred Tenants: {tenants}
- Available From: {available}
- Nearby: {nearby if nearby else 'Various conveniences'}
{rough_desc_section}
**CREATIVE DIRECTION FOR THIS VERSION (Version #{variation_seed + 1}):**
- Primary Focus: {variation['focus']}
- Tone: {variation['tone']}
- Special Instruction: {variation['instruction']}

**Requirements:**
1. **Title**: Create an attention-grabbing, emotional title (8-12 words) that highlights the property's unique value proposition and creates desire. Make it DIFFERENT from generic titles. DO NOT start with "Discover" or "Welcome".
2. **Teaser**: Write a compelling hook (15-20 words) that creates urgency and paints a lifestyle picture
3. **Full Description**: Craft a detailed, engaging description (150-200 words) that:
   - Paints a vivid picture of living there
   - Highlights lifestyle benefits, not just features
   - Uses emotional, sensory language
   - Emphasizes location advantages and convenience
   - Creates FOMO (fear of missing out)
   - Focuses on the experience and feelings
   - Follows the creative direction provided above
   - INCORPORATES any owner notes/rough description provided
4. **Bullet Points**: 5 compelling features written as BENEFITS (not just specs). Focus on what the tenant gains. Make them unique and specific.
5. **SEO Keywords**: 5 highly relevant, search-optimized keywords that people actually search for
6. **Meta Title**: SEO-optimized title (under 60 chars) with primary keyword
7. **Meta Description**: Compelling SEO description (under 160 chars) with call-to-action

**Tone**: {variation['tone']}. Write like you're selling a dream lifestyle, not just a property.

**IMPORTANT - MAKE IT UNIQUE:**
- Use varied vocabulary and expressions
- Try different angles and perspectives  
- Create original metaphors and descriptions
- Avoid repetitive patterns
- Each regeneration should feel fresh and different

Return ONLY valid JSON (no markdown, no ```json):
{{
    "title": "your captivating title here",
    "teaser_text": "your compelling teaser here",
    "full_description": "your detailed engaging description here",
    "bullet_points": ["lifestyle benefit 1", "lifestyle benefit 2", "lifestyle benefit 3", "lifestyle benefit 4", "lifestyle benefit 5"],
    "seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
    "meta_title": "your SEO meta title here",
    "meta_description": "your SEO meta description with CTA here"
}}"""

            # Adjust temperature based on variation for more creativity
            temperature = 0.8 + (variation_seed * 0.05)
            if temperature > 1.0:
                temperature = 0.8 + ((variation_seed % 3) * 0.05)

            # Make API request
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are an expert real estate copywriter creating premium, emotionally engaging property listings. For this generation (Version #{variation_seed + 1}), your focus is on {variation['focus']} with a {variation['tone']} tone. Write compelling, benefit-focused content that sells lifestyle and experience, not just features. Be creative and avoid repetitive patterns. If owner notes are provided, incorporate them prominently. Always respond with valid JSON only, no markdown formatting."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "temperature": temperature,
                    "max_tokens": 2000,
                    "top_p": 0.9
                },
                timeout=30
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Clean markdown formatting if present
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                elif content.startswith('```'):
                    content = content.replace('```', '').strip()
                
                # Parse JSON
                parsed = json.loads(content)
                return parsed
            
            # Handle errors
            elif response.status_code == 429:
                if attempt < retry_count - 1:
                    wait_time = (attempt + 1) * 2
                    st.warning(f"⏳ Rate limit hit. Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    st.error("❌ Rate limit exceeded. Please wait a minute and try again.")
                    return None
            
            elif response.status_code == 401:
                st.error("❌ Invalid API Key")
                st.info("🔑 Get a new API key from: https://console.groq.com/keys")
                return None
            
            elif response.status_code == 400:
                error_data = response.json()
                st.error(f"❌ Bad Request: {error_data}")
                return None
            
            else:
                st.error(f"❌ API Error {response.status_code}")
                with st.expander("🔍 Error Details"):
                    st.code(response.text)
                return None
                
        except requests.exceptions.Timeout:
            if attempt < retry_count - 1:
                st.warning(f"⏳ Timeout. Retrying... (Attempt {attempt + 2}/{retry_count})")
                time.sleep(2)
                continue
            else:
                st.error("❌ Request timeout after multiple attempts")
                return None
        
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON response from Groq")
            with st.expander("🔍 Response Details"):
                st.text(content if 'content' in locals() else "No content received")
            return None
        
        except Exception as e:
            st.error(f"❌ Unexpected Error: {str(e)}")
            return None
    
    return None

def generate_fallback(property_data):
    """Fallback template-based generation"""
    bhk = property_data['bhk']
    prop_type = property_data['property_type'].title()
    locality = property_data['locality']
    city = property_data['city']
    area = property_data['area_sqft']
    rent = property_data['rent_amount']
    furnishing = property_data['furnishing_status'].title()
    rough_desc = property_data.get('rough_description', '').strip()
    
    # Include rough description in fallback if provided
    extra_info = ""
    if rough_desc:
        extra_info = f" {rough_desc}"
    
    return {
        "title": f"Spacious {bhk} BHK {prop_type} for Rent in {locality}",
        "teaser_text": f"Well-maintained {bhk} BHK {prop_type} in prime {locality} location",
        "full_description": f"Looking for a comfortable home? This beautiful {bhk} BHK {prop_type} in {locality}, {city} is perfect for you. Spread across {area} sqft, this {furnishing} furnished property offers great value at ₹{rent:,}/month. Located in a well-connected area with easy access to essential amenities.{extra_info}",
        "bullet_points": [
            f"{bhk} BHK configuration with {area} sqft carpet area",
            f"{furnishing} furnished with modern fittings",
            f"Monthly rent: ₹{rent:,} | Deposit: ₹{property_data['deposit_amount']:,}",
            f"Preferred for: {property_data['preferred_tenants']}",
            f"Available from: {property_data['available_from']}"
        ],
        "seo_keywords": [
            f"{bhk} bhk {city}",
            f"{locality} rental",
            f"{prop_type} for rent {city}",
            f"{furnishing} flat {locality}",
            f"rent {bhk}bhk {city}"
        ],
        "meta_title": f"{bhk} BHK {prop_type} for Rent in {locality}, {city}",
        "meta_description": f"Rent this spacious {bhk} BHK {prop_type} in {locality}, {city}. {area} sqft, {furnishing} furnished. ₹{rent:,}/month. Available now!"
    }

def generate_description(property_data, api_provider, api_key=None, variation_seed=0):
    """Main generation function with multiple providers and variation support"""
    if api_provider == "Groq Premium (Free)" and api_key:
        result = generate_with_groq(property_data, api_key, variation_seed=variation_seed)
        if result:
            return result
    
    # Fallback to template
    st.info("ℹ️ Using template-based generation")
    return generate_fallback(property_data)

# ==================== MAIN APP ====================
def main():
    st.title("🏠 AI Property Management System")
    st.caption("Property Type Guide + Premium Description Generator - FREE with Groq API 🌟")
    
    # Initialize session state
    if 'generated_result' not in st.session_state:
        st.session_state.generated_result = None
    if 'property_data' not in st.session_state:
        st.session_state.property_data = None
    if 'generation_count' not in st.session_state:
        st.session_state.generation_count = 0
    
    # Create main tabs
    tab1, tab2, tab3 = st.tabs(["🏘️ Property Type Guide", "🚀 Description Generator", "📊 Batch Processing"])
    
    with tab1:
        # Property Type Guide
        guide = PropertyTypeGuide()
        guide.display_guide()
    
    with tab2:
        # Single Property Description Generator
        show_single_property_generator()
    
    with tab3:
        # Batch Processing (placeholder for future enhancement)
        st.header("📊 Batch Property Processing")
        st.info("🚧 This feature is under development")
        st.write("Upload multiple property listings to generate descriptions in bulk")
        
        uploaded_file = st.file_uploader(
            "Upload CSV/Excel file with multiple properties",
            type=['csv', 'xlsx'],
            key="batch_upload"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info("Batch processing coming soon!")

def show_single_property_generator():
    """Single Property Description Generator"""
    st.header("🚀 AI Property Description Generator")
    st.caption("Generate premium property descriptions with AI")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # AI Provider Selection
        api_provider = st.selectbox(
            "Select AI Provider",
            ["Groq Premium (Free)", "Template (No API)"],
            help="Groq Premium uses enhanced prompting for free premium quality!",
            key="api_provider_select"
        )
        
        # API Key Input
        api_key = None
        if api_provider != "Template (No API)":
            st.success("🌟 PREMIUM Quality + FREE - Best of Both Worlds!")
            st.info("🆓 Get free Groq API key from: https://console.groq.com/keys")
            api_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", key="groq_api_key")
            
            # Test API button
            if api_key:
                if st.button("🧪 Test API Connection", key="test_api_btn"):
                    with st.spinner("Testing..."):
                        success, message = test_groq_api(api_key)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        st.divider()
        
        # Feature Info
        with st.expander("ℹ️ About Features"):
            st.markdown("""
            **✨ Premium Features:**
            - Property Type Guide with detailed information
            - AI-powered description generation
            - Multiple creative variations
            - SEO-optimized content
            - Professional real estate copywriting
            """)
    
    # Property input form
    st.subheader("📝 Property Details")
    
    # Create tabs for organized input
    tab1, tab2, tab3 = st.tabs(["🏠 Basic Details", "💰 Pricing & Availability", "✨ Features & Amenities"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            property_type = st.selectbox(
                "Property Type *",
                ["Flat", "Villa", "Independent House", "PG/Hostel", "Shop", "Office Space", 
                 "Warehouse", "Land/Plot", "Studio Apartment", "Penthouse", "Agricultural", 
                 "Residential", "Commercial", "Industrial", "Institutional", "Mixed-Use"],
                help="Select the type of property",
                key="prop_type_select"
            )
            
            bhk = st.selectbox(
                "BHK Configuration / Rooms *",
                ["1 RK", "1 BHK", "2 BHK", "3 BHK", "4 BHK", "5 BHK", "5+ BHK", 
                 "Studio", "Other"],
                help="Number of bedrooms, hall, and kitchen",
                key="bhk_select"
            )
            
            area_sqft = st.number_input(
                "Built-up Area (sq ft) *",
                min_value=100,
                max_value=50000,
                value=1000,
                step=200,
                help="Total built-up area of the property",
                key="area_input"
            )
            
            furnishing = st.selectbox(
                "Furnishing Status *",
                ["Unfurnished", "Semi-Furnished", "Fully Furnished"],
                help="Current furnishing level of the property",
                key="furnishing_select"
            )
        
        with col2:
            city = st.text_input(
                "City/Town *",
                value="Mumbai",
                help="City or town name",
                key="city_input"
            )
            
            locality = st.text_input(
                "Area/Locality *",
                value="Andheri West",
                help="Specific area or locality name",
                key="locality_input"
            )
            
            landmark = st.text_input(
                "Landmark (Optional)",
                placeholder="e.g., Near XYZ Mall, Opposite ABC Hospital",
                help="Prominent landmark near the property",
                key="landmark_input"
            )
            
            col_floor1, col_floor2 = st.columns(2)
            with col_floor1:
                floor_no = st.number_input(
                    "Floor Number",
                    min_value=0,
                    max_value=100,
                    value=5,
                    help="Floor on which property is located (0 for ground)",
                    key="floor_no_input"
                )
            
            with col_floor2:
                total_floors = st.number_input(
                    "Total Floors",
                    min_value=1,
                    max_value=100,
                    value=10,
                    help="Total floors in the building",
                    key="total_floors_input"
                )
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            rent = st.number_input(
                "Monthly Rent (₹) *",
                min_value=1000,
                max_value=10000000000,
                value=30000,
                step=5000,
                help="Monthly rental amount",
                key="rent_input"
            )
            
            deposit = st.number_input(
                "Security Deposit (₹) *",
                min_value=0,
                max_value=50000000,
                value=50000,
                step=5000,
                help="Refundable security deposit",
                key="deposit_input"
            )
        
        with col2:
            available = st.date_input(
                "Available From *",
                help="Date when property will be available for move-in",
                key="available_date"
            )
            
            preferred_tenants = st.multiselect(
                "Preferred Tenants *",
                ["Family", "Bachelors", "Students", "Company Lease", "Any"],
                default=["Family"],
                help="Type of tenants preferred (can select multiple)",
                key="tenants_multiselect"
            )
    
    with tab3:
        st.markdown("#### 🏢 Features & Amenities")
        
        col1, col2, col3 = st.columns(3)
        
        amenities = []
        
        with col1:
            if st.checkbox("Lift/Elevator", value=True, key="amenity_lift"):
                amenities.append("Lift")
            if st.checkbox("Parking", value=True, key="amenity_parking"):
                amenities.append("Parking")
            if st.checkbox("Power Backup", value=False, key="amenity_power"):
                amenities.append("Power Backup")
            if st.checkbox("Security", value=True, key="amenity_security"):
                amenities.append("Security")
        
        with col2:
            if st.checkbox("Gym/Fitness Center", value=False, key="amenity_gym"):
                amenities.append("Gym")
            if st.checkbox("Swimming Pool", value=False, key="amenity_pool"):
                amenities.append("Pool")
            if st.checkbox("Garden/Park", value=False, key="amenity_garden"):
                amenities.append("Garden")
            if st.checkbox("Balcony", value=True, key="feature_balcony"):
                amenities.append("Balcony")
        
        with col3:
            if st.checkbox("Modular Kitchen", value=False, key="feature_kitchen"):
                amenities.append("Modular Kitchen")
            if st.checkbox("AC", value=False, key="feature_ac"):
                amenities.append("Air Conditioning")
            if st.checkbox("Geyser", value=False, key="feature_geyser"):
                amenities.append("Geyser")
            if st.checkbox("WiFi/Internet", value=False, key="feature_wifi"):
                amenities.append("Internet")
        
        st.divider()
        
        st.markdown("#### 📄 Additional Description (Optional)")
        rough_description = st.text_area(
            "Owner's Description / Special Features",
            placeholder="Add any additional details, special features, or unique selling points...",
            height=100,
            help="Free text to add any extra information about the property",
            key="rough_desc"
        )
    
    # Prepare property data
    property_data = {
        'property_type': property_type.lower(),
        'bhk': bhk,
        'area_sqft': area_sqft,
        'city': city,
        'locality': locality,
        'landmark': landmark if landmark else '',
        'floor_no': floor_no,
        'total_floors': total_floors,
        'furnishing_status': furnishing.lower(),
        'rent_amount': rent,
        'deposit_amount': deposit,
        'available_from': str(available),
        'preferred_tenants': ', '.join(preferred_tenants),
        'amenities': amenities,
        'rough_description': rough_description if rough_description else ''
    }
    
    # Generate buttons
    col1, col2 = st.columns([1, 1])
    
    with col1:
        generate_clicked = st.button("🚀 Generate Description", type="primary", use_container_width=True)
    
    with col2:
        regenerate_clicked = st.button("🔄 Regenerate", type="secondary", use_container_width=True,
                                      disabled=st.session_state.generated_result is None)
    
    # Handle generation
    if generate_clicked or regenerate_clicked:
        if not city or not locality:
            st.error("❌ Please fill in all required fields marked with *")
            return
        
        st.session_state.property_data = property_data
        
        if regenerate_clicked:
            st.session_state.generation_count += 1
        else:
            st.session_state.generation_count = 0
        
        with st.spinner(f"✨ Generating premium description..."):
            result = generate_description(
                property_data, 
                api_provider, 
                api_key,
                variation_seed=st.session_state.generation_count
            )
        
        if result:
            st.session_state.generated_result = result
            st.success("✅ Premium Description Generated Successfully!")
    
    # Display results
    if st.session_state.generated_result:
        result = st.session_state.generated_result
        property_data = st.session_state.property_data
        
        st.markdown("---")
        st.header("🎉 Generated Property Description")
        
        # Display generated content
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Description")
            st.markdown(f"**Title:** {result['title']}")
            st.markdown(f"**Teaser:** {result['teaser_text']}")
            st.markdown(f"**Full Description:** {result['full_description']}")
            
            st.subheader("✨ Key Features")
            for point in result['bullet_points']:
                st.markdown(f"• {point}")
        
        with col2:
            st.subheader("🔍 SEO Optimization")
            st.markdown("**Keywords:**")
            st.write(", ".join(result['seo_keywords']))
            
            st.markdown("**Meta Title:**")
            st.info(result['meta_title'])
            
            st.markdown("**Meta Description:**")
            st.info(result['meta_description'])
        
        # Download options
        st.divider()
        st.subheader("💾 Download Options")
        
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            # JSON Download
            json_data = json.dumps({
                'property_details': property_data,
                'generated_content': result,
                'generation_version': st.session_state.generation_count + 1
            }, indent=2)
            
            st.download_button(
                "📄 Download JSON",
                json_data,
                f"property_{property_data['locality'].replace(' ', '_')}.json",
                "application/json",
                use_container_width=True
            )
        
        with download_col2:
            # Text Download
            text_content = f"""{result['title']}
{result['teaser_text']}

{result['full_description']}

Key Features:
{chr(10).join(f"• {p}" for p in result['bullet_points'])}

SEO Keywords: {', '.join(result['seo_keywords'])}
Meta Title: {result['meta_title']}
Meta Description: {result['meta_description']}
            """
            
            st.download_button(
                "📝 Download TXT",
                text_content,
                f"property_{property_data['locality'].replace(' ', '_')}.txt",
                "text/plain",
                use_container_width=True
            )

if __name__ == "__main__":
    main()