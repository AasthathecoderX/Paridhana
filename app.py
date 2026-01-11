# Force redeploy - Updated SDK
import os
import re
import json
import base64
from pathlib import Path
from urllib.parse import quote

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image  # noqa: F401

from google import genai
from google.genai import types


# ================== ENV & CLIENTS ==================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Missing GEMINI_API_KEY environment variable.")
    st.stop()

gemini_client = genai.Client(api_key=GEMINI_API_KEY)


# ================== STREAMLIT CONFIG ==================

st.set_page_config(page_title="Paridhana", layout="wide")

# Session state
if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""
if "search_text" not in st.session_state:
    st.session_state["search_text"] = ""
if "design_text" not in st.session_state:
    st.session_state["design_text"] = ""
if "design_image_bytes" not in st.session_state:
    st.session_state["design_image_bytes"] = None
if "products" not in st.session_state:
    st.session_state["products"] = []
if "budget" not in st.session_state:
    st.session_state["budget"] = 2000


# ================== BACKGROUND IMAGE ==================

def set_bg(image_file: str = "bg.png"):
    if not Path(image_file).exists():
        return

    img_bytes = Path(image_file).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url("data:image/jpeg;base64,{encoded}") no-repeat center center fixed;
            background-size: cover;
            font-family: "Georgia", "Times New Roman", serif;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


set_bg("bg.png")


# ================== GLOBAL CSS + HEADER ==================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1800px !important;
    }
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    .vintage-header-wrapper {
        width: 100%;
        text-align: center;
        margin-top: 0.25rem;
        margin-bottom: 1.8rem;
    }
    .vintage-title {
        font-family: "Playfair Display", "Georgia", serif;
        font-size: 3.4rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #3b2314;
        margin-bottom: 0.2rem;
    }
    .vintage-subtitle {
        font-family: "Cormorant Garamond", "Georgia", serif;
        font-size: 1.3rem;
        font-weight: 500;
        color: #4a2b17;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }
    .vintage-divider {
        width: 360px;
        height: 1px;
        margin: 0.9rem auto 0 auto;
        background: linear-gradient(to right, transparent, #4a2b17, transparent);
        opacity: 0.9;
    }

    .main-row {
        display: flex;
        gap: 0 !important;
        align-items: stretch;
        width: 100%;
    }
    .main-col {
        flex: 1;
        display: flex;
        flex-direction: column;
        width: 100%;
        max-width: 100% !important;
    }

    .vintage-panel {
        flex: 1;
        background: #fefaf4;
        border-radius: 14px;
        padding: 1.6rem 1.4rem 1.8rem 1.4rem;
        box-shadow:
          0 20px 55px rgba(0, 0, 0, 0.18),
          0 0 0 1px rgba(74, 43, 23, 0.12);
        border: 1px solid rgba(74, 43, 23, 0.15);
        display: flex;
        flex-direction: column;
        gap: 0.9rem;
        margin-top: -1.5rem !important;
        width: 100%;
    }
    .vintage-panel h3 {
        font-family: "Playfair Display", "Georgia", serif;
        font-size: 1.25rem;
        letter-spacing: 0.09em;
        text-transform: uppercase;
        color: #3b2314;
        margin-bottom: 0.4rem;
    }
    .vintage-label {
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #4a2b17;
        margin-bottom: 0.25rem;
    }

    /* Global text in dark brown */
    .stMarkdown, .stTextInput, .stNumberInput, .stCaption, p, label {
        color: #3b2314 !important;
    }

    /* Make all input elements wider */
    textarea, input[type="number"], input[type="text"] {
        width: 100% !important;
        box-sizing: border-box !important;
        background-color: #f3ebe0 !important;
        color: #3b2314 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(74, 43, 23, 0.35) !important;
        padding: 0.75rem !important;
    }

    /* Placeholder text - make it brown */
    textarea::placeholder,
    input::placeholder,
    textarea::-webkit-input-placeholder,
    input::-webkit-input-placeholder,
    textarea::-moz-placeholder,
    input::-moz-placeholder,
    textarea:-ms-input-placeholder,
    input:-ms-input-placeholder {
        color: #3b2314 !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }
    
    /* Additional Streamlit placeholder styling */
    .stTextArea textarea::placeholder {
        color: #3b2314 !important;
    }
    
    .stNumberInput input::placeholder {
        color: #3b2314 !important;
    }

    /* BUTTONS: Force white text on all levels */
    button[kind="primary"],
    .stButton > button {
        background-color: #4a2b17 !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 999px !important;
        border: none !important;
        padding: 0.6rem 1.6rem !important;
        width: 100% !important;
    }

    /* Target the inner text wrapper inside button */
    .stButton > button * {
        color: #ffffff !important;
        fill: #ffffff !important;
    }

    /* Target span, div inside button */
    .stButton button span,
    .stButton button div {
        color: #ffffff !important;
    }

    .stButton>button:hover {
        background-color: #63331c !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.18);
    }

    .results-wrapper {
        margin-top: 0.6rem;
        width: 100%;
    }

    /* Remove stray top box/spacer inside columns */
    div[data-testid="stVerticalBlock"] > div:empty {
        display: none !important;
    }
    div[data-testid="stVerticalBlock"] > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    </style>

    <div class="vintage-header-wrapper">
        <div class="vintage-title">Paridhana</div>
        <div class="vintage-subtitle">
            AI-powered outfit designer and shopping assistant
        </div>
        <div class="vintage-divider"></div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ================== GEMINI HELPERS ==================

def generate_design_text(user_text: str) -> str:
    if not user_text.strip():
        return ""

    prompt = f"""
    You are a fashion design assistant.
    Based on this description, describe a detailed outfit design (colors, fabric, drape, patterns):

    "{user_text}"
    """

    try:
        resp = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        return resp.text or ""
    except Exception as e:
        st.error(f"Design generation error: {e}")
        return ""


def extract_outfit_tags_from_image(image_bytes: bytes) -> dict:
    try:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg",
        )

        prompt = """
        You are a fashion tagging assistant.
        Look at this outfit image and describe it in a compact JSON object.

        IMPORTANT:
        - Respond with ONLY valid JSON, no markdown, no text outside JSON.
        - Keys: "colors", "garment_type", "style", "fabric", "length", "occasion", "fit", "keywords"
        - Each value should be a short string, except "keywords" which is a comma-separated string.
        """

        resp = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image_part],
            config=types.GenerateContentConfig(temperature=0.3),
        )

        text = (resp.text or "").strip()
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group()

        tags = json.loads(text)
        if isinstance(tags, dict):
            return tags
        return {}
    except Exception as e:
        st.error(f"Image tagging error: {e}")
        return {}


def search_products_with_gemini(
    outfit_text: str,
    search_text: str,
    budget: int,
    sites: list[str],
    image_tags: dict | None = None,
) -> list[dict]:
    if not outfit_text.strip() and not image_tags:
        st.warning("Please generate a design first before searching for products.")
        return []

    sites_str = ", ".join(sites)

    combined_description = outfit_text
    if image_tags:
        tags_str = ", ".join(
            f"{k}: {v}" for k, v in image_tags.items() if v
        )
        combined_description += f"\nImage tags: {tags_str}"

    prompt = f"""
    You are a fashion shopping assistant.
    Generate a JSON array of fashion products from Indian e-commerce sites.

    Outfit description:
    \"\"\"{combined_description}\"\"\"

    Extra search filters from user:
    \"\"\"{search_text}\"\"\"

    Budget (INR): {budget}
    Sites (use only in "site" field, do NOT invent API calls): {sites_str}

    TASK:
    - Propose realistic fashion products that match the outfit and filters.
    - All prices must be <= {budget}.
    - Titles should look like real listings from these sites.

    IMPORTANT:
    - Return ONLY a valid JSON array. No markdown, no extra text.
    - Each product must have: "title", "price" (number), "site".
    """

    try:
        resp = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.3),
        )

        response_text = (resp.text or "").strip()
        json_match = re.search(r"\[.*\]", response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group()

        products = json.loads(response_text)

        if isinstance(products, list) and len(products) > 0:
            filtered = []
            for p in products:
                try:
                    price_val = float(p.get("price", budget + 1))
                except Exception:
                    price_val = budget + 1
                if price_val <= budget:
                    site = (p.get("site") or "").lower()
                    title = p.get("title", "")
                    query = requests.utils.quote(title)

                    if "amazon" in site:
                        url = f"https://www.amazon.in/s?k={query}"
                    elif "myntra" in site:
                         url = f"https://www.myntra.com/{query}?rawQuery={query}"
                    elif "ajio" in site:
                        url = f"https://www.ajio.com/search/?text={query}"
                    elif "flipkart" in site:
                        url = f"https://www.flipkart.com/search?q={query}"
                    else:
                        url = f"https://www.google.com/search?q={query}"    
                    p["url"] = url

                    filtered.append(p)

            return filtered
        else:
            st.warning("No products found. Try a different search.")
            return []

    except json.JSONDecodeError as e:
        st.error(f"Failed to parse product data: {e}")
        st.info("The API response was not valid JSON. Showing dummy products instead.")
        return generate_dummy_products(combined_description, budget, sites)
    except Exception as e:
        st.error(f"Search error: {e}")
        return generate_dummy_products(combined_description, budget, sites)


def generate_dummy_products(outfit_text: str, budget: int, sites: list) -> list[dict]:
    dummy_products = [
        {
            "title": "Premium Silk Saree",
            "price": min(budget, 1800),
            "site": sites[0] if sites else "Amazon",
        },
        {
            "title": "Designer Ethnic Wear",
            "price": min(budget, 2500),
            "site": sites[1] if len(sites) > 1 else "Myntra",
        },
        {
            "title": "Traditional Organza Saree",
            "price": min(budget, 2200),
            "site": sites[2] if len(sites) > 2 else "Ajio",
        },
    ]

    for p in dummy_products:
        site = p["site"].lower()
        title = p["title"]
        query = requests.utils.quote(title)

        if "amazon" in site:
            p["url"] = f"https://www.amazon.in/s?k={query}"
        elif "myntra" in site:
            p["url"] = f"https://www.myntra.com/{query}?rawQuery={query}"
        elif "ajio" in site:
            p["url"] = f"https://www.ajio.com/search/?text={query}"
        else:
            p["url"] = f"https://www.flipkart.com/search?q={query}"
    return [p for p in dummy_products if p["price"] <= budget]



# ================== POLLINATIONS.AI IMAGE GENERATION ==================
def generate_design_image(prompt: str) -> bytes | None:
    full_prompt = (
        "High-quality fashion illustration, full body, front view, clean studio background. "
        + prompt
    )
    try:
        url = f"https://image.pollinations.ai/prompt/{quote(full_prompt)}"
        response = requests.get(url, timeout=30)
        
        # Check for successful response and valid image data
        if response.status_code == 200:
            content = response.content
            
            # Validate that content is not empty and looks like an image
            # Check for JPEG header (FF D8 FF) or PNG header (89 50 4E 47)
            if len(content) > 100:
                if content[:2] == b'\xff\xd8' or content[:4] == b'\x89PNG':
                    return content
            
            # If we got here, the response doesn't look like a valid image
            st.warning("Image generation service returned invalid data. Please try again.")
            return None
        else:
            st.error(f"Image generation failed: HTTP {response.status_code}")
            return None
            
    except requests.Timeout:
        st.error("Image generation timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"Image generation error: {str(e)}")
        return None

# ================== UI LAYOUT ==================

st.markdown('<div class="main-row">', unsafe_allow_html=True)
col1, col_spacer, col2 = st.columns([2, 1, 2])

# -------- LEFT: DESIGN + IMAGE --------

# -------- LEFT: DESIGN + IMAGE --------

with col1:
    st.write("### Design your look")
    st.markdown('<div class="vintage-label">Outfit description</div>', unsafe_allow_html=True)

    prompt_text = st.text_area(
        "Describe your outfit",
        key="prompt",
        placeholder="e.g., elegant navy blue saree with silver border for evening wedding",
        label_visibility="collapsed",
        height=180,
    )

    generate_clicked = st.button("Generate design", use_container_width=True)

    if generate_clicked:
        if not prompt_text.strip():
            st.error("Please enter a description first.")
        else:
            with st.spinner("Generating design and image..."):
                design_text = generate_design_text(prompt_text)
                image_bytes = generate_design_image(prompt_text)

                st.session_state["design_text"] = design_text
                st.session_state["design_image_bytes"] = image_bytes

            st.success("Design generated successfully!")
            st.rerun()

    if st.session_state.get("design_text"):
        st.markdown("#### Design description")
        st.markdown(f"""
            <div style="
            background-color: #f3ebe0;
            border: 1px solid rgba(74, 43, 23, 0.35);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        ">
            <p style="color: #3b2314; margin: 0;">{st.session_state["design_text"]}</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.get("design_image_bytes"):
        st.markdown("#### Design image")
        st.image(st.session_state["design_image_bytes"], use_container_width=True)


# -------- SPACER (MIDDLE COLUMN) --------

with col_spacer:
    st.empty()
# -------- RIGHT: SEARCH OUTFITS --------

with col2:
    st.write("### Find similar outfits")
    st.markdown('<div class="vintage-label">Budget (₹)</div>', unsafe_allow_html=True)
    budget_val = st.number_input(
        "Budget (₹)",
        min_value=100,
        value=st.session_state.get("budget", 2000),
        step=100,
        key="budget",
        label_visibility="collapsed",
    )

    st.markdown('<div class="vintage-label">Search filters</div>', unsafe_allow_html=True)
    search_text = st.text_area(
        "Search filters",
        key="search_text",
        placeholder="e.g., search by color, fabric, or style",
        label_visibility="collapsed",
    )

    search_clicked = st.button("Search", use_container_width=True)

    if search_clicked:
        outfit_text = st.session_state.get("prompt", "")
        image_bytes = st.session_state.get("design_image_bytes", None)

        if not image_bytes and not outfit_text.strip():
            st.error("Please generate a design first!")
        else:
            image_tags = {}
            if image_bytes:
                with st.spinner("Understanding your outfit image..."):
                    image_tags = extract_outfit_tags_from_image(image_bytes)

            with st.spinner("Searching for products..."):
                sites = ["Amazon", "Myntra", "Ajio", "Flipkart"]
                st.session_state["products"] = search_products_with_gemini(
                    outfit_text,
                    search_text,
                    budget_val,
                    sites,
                    image_tags=image_tags,
                )

            if st.session_state["products"]:
                st.success("Search completed!")
                st.rerun()

    if st.session_state["products"]:
        st.markdown("#### Similar outfits found")
        
        products_html = '<div style="background-color: #f3ebe0; border: 1px solid rgba(74, 43, 23, 0.35); border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">'
        
        for product in st.session_state["products"]:
            title = product.get('title', 'Untitled product')
            price = product.get('price', 'N/A')
            site = product.get('site', 'Unknown')
            url = product.get('url', '#')
            
            products_html += f'<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(74, 43, 23, 0.15);"><div style="flex: 2;"><strong style="color: #3b2314;">{title}</strong></div><div style="flex: 1; text-align: center; color: #3b2314;">₹{price}</div><div style="flex: 1; text-align: center; color: #3b2314;">{site}</div><div style="flex: 1; text-align: center;"><a href="{url}" target="_blank" style="background-color: #1a1a2e; color: white; padding: 0.4rem 0.8rem; border-radius: 4px; text-decoration: none; font-size: 0.85rem; display: inline-block;">View</a></div></div>'
        
        products_html += "</div>"
        
        st.markdown(products_html, unsafe_allow_html=True)


st.markdown("</div>", unsafe_allow_html=True)
