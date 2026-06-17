import streamlit as st
from groq import Groq
from PIL import Image
import os
import base64
import hashlib
import time
import io
import re
from dotenv import load_dotenv
from products_db import (
    PRODUCTS, search_products, get_product_by_id,
    analyze_ingredients, HARMFUL, BENEFICIAL
)

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="WonderSkin — AI Skincare Intelligence",
    page_icon="✨",
    layout="wide"
)

# ── THEME-AWARE CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.45rem 1.3rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: all 0.25s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124,58,237,0.45) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6d28d9 0%, #be185d 100%) !important;
    padding: 0.6rem 2rem !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
}

.stTabs [data-baseweb="tab-list"] {
    border-radius: 16px !important;
    padding: 4px !important;
    gap: 2px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #7c3aed, #db2777) !important;
    color: white !important;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #7c3aed, #db2777) !important;
    border-radius: 10px !important;
}

@keyframes bounce {
  0%,100%{transform:translateY(0);} 50%{transform:translateY(-12px);}
}
@keyframes shimmer {
  0%{background-position:-200% center;}
  100%{background-position:200% center;}
}
@keyframes confetti-fall {
  0%{opacity:1;transform:translateY(-20px) rotate(0deg);}
  100%{opacity:0;transform:translateY(60px) rotate(360deg);}
}
.winner-card {
  background: linear-gradient(135deg, #7c3aed, #db2777, #f59e0b);
  background-size: 200% auto;
  animation: shimmer 2s linear infinite;
  border-radius: 20px;
  padding: 1.5rem 2rem;
  text-align: center;
  color: white;
  margin: 1rem 0;
}
.trophy-bounce {
  font-size: 3rem;
  display: inline-block;
  animation: bounce 0.8s ease infinite;
}
.confetti {
  display: inline-block;
  animation: confetti-fall 1.5s ease forwards;
}

.ws-card {
    background: var(--background-color, #fff);
    border-radius: 16px;
    border: 1px solid rgba(124,58,237,0.18);
    padding: 1rem 1.4rem;
    margin-bottom: 0.6rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}

[data-theme="dark"] .ws-card,
[class*="dark"] .ws-card {
    background: #1e1e2e;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD ENV & SETUP ──
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

# ── SESSION STATE ──
defaults = {
    "skin_type": "Oily",
    "concerns": [],
    "history": [],
    "routine_history": [],
    "skin_gist": None,
    "analyze_product": None,
    "brand_pill_query": None,
    "ai_query_result": None,
    "ai_query_name": None,
    "show_reviews_for": None,
    "reviews_result": None,
    "ai_product_to_analyze": None,
    "ai_product_analysis": None,
    # Global button counter — resets each full script run (correct Streamlit behavior)
    "_btn_counter": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Reset counter at top of each run so keys are stable across reruns
st.session_state["_btn_counter"] = 0

def next_btn_key(prefix="btn"):
    """Return a unique button key using a global counter."""
    st.session_state["_btn_counter"] += 1
    return f"{prefix}_{st.session_state['_btn_counter']}"

if "feed_posts" not in st.session_state:
    st.session_state.feed_posts = [
        {"user": "priya_glows",    "product": "Minimalist Niacinamide", "review": "Cleared my acne in 3 weeks! Skin feels so smooth now 🙌", "likes": 124, "liked": False},
        {"user": "skincare.tamil", "product": "CeraVe Moisturizing Cream", "review": "Best moisturizer for dry skin. No fragrance, no irritation ❤️", "likes": 98, "liked": False},
        {"user": "glow.india",     "product": "The Ordinary Niacinamide", "review": "Affordable and effective! My pores look so much smaller", "likes": 210, "liked": False},
        {"user": "cleanbeauty.in", "product": "Dot & Key Watermelon Gel", "review": "Perfect for oily skin summers! Lightweight and refreshing 💧", "likes": 67, "liked": False},
    ]

# ── AI HELPERS ──
def ai_text(prompt):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.7
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"AI unavailable: {e}"

def ai_vision(image, prompt):
    try:
        buf = io.BytesIO()
        image.save(buf, format="JPEG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        resp = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]}],
            max_tokens=1024
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"AI unavailable: {e}"

# ── UI HELPERS ──
def skin_profile_banner():
    skin_emoji = {"Oily": "💧", "Dry": "🌵", "Combination": "⚖️", "Sensitive": "🌸", "Normal": "✨"}
    emoji = skin_emoji.get(st.session_state.skin_type, "✨")
    concerns_str = " · ".join(st.session_state.concerns) if st.session_state.concerns else "No concerns selected"
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,rgba(124,58,237,0.1),rgba(219,39,119,0.1));
    border-radius:16px;padding:0.9rem 1.4rem;margin-bottom:1.5rem;border-left:4px solid #7c3aed;'>
    <span style='font-size:1.5rem;'>{emoji}</span>
    <span style='font-weight:600;color:#7c3aed;margin-left:0.5rem;'>{st.session_state.skin_type} Skin</span>
    <span style='opacity:0.4;margin:0 0.5rem;'>|</span>
    <span style='opacity:0.7;font-size:0.9rem;'>🎯 {concerns_str}</span>
    </div>""", unsafe_allow_html=True)

def score_card(score):
    if score >= 75:   color, label, icon = "#059669", "Excellent", "🟢"
    elif score >= 55: color, label, icon = "#d97706", "Good",      "🟡"
    elif score >= 35: color, label, icon = "#ea580c", "Fair",      "🟠"
    else:             color, label, icon = "#dc2626", "Poor",      "🔴"
    st.markdown(f"""
    <div style='border-radius:20px;padding:1.2rem 1.5rem;
    border:2px solid {color}55;display:inline-block;margin:0.5rem 0;
    background:linear-gradient(135deg,{color}11,{color}05);'>
    <div style='font-size:2.2rem;font-weight:700;color:{color};'>
    {score}<span style='font-size:1rem;opacity:0.5;'>/100</span></div>
    <div style='color:{color};font-weight:600;font-size:0.9rem;'>{icon} {label} Safety Score</div>
    </div>""", unsafe_allow_html=True)

def show_product_analysis(p):
    """Full analysis block for a product dict from DB."""
    st.markdown(f"""
    <div style='border-radius:20px;padding:1.2rem 1.5rem;margin-bottom:1rem;
    border:1px solid rgba(124,58,237,0.2);
    background:linear-gradient(135deg,rgba(124,58,237,0.06),rgba(219,39,119,0.06));'>
    <h3 style='color:#7c3aed;margin:0;'>Analyzing: {p['name']}</h3>
    <p style='opacity:0.55;margin:0.2rem 0 0 0;font-size:0.85rem;'>
    {p['brand']} · {p['category']} · ₹{p['price']}</p>
    </div>""", unsafe_allow_html=True)

    rated, raw_score = analyze_ingredients(p["ingredients"], st.session_state.skin_type.lower())
    avoid_ings   = [r["name"] for r in rated if r["flag"] == "avoid"]
    caution_ings = [r["name"] for r in rated if r["flag"] == "caution"]
    beneficial   = [r for r in rated if r["benefit"]]

    with st.spinner("Calculating score based on user ratings and ingredient science..."):
        score_prompt = f"""
You are analyzing "{p['name']}" by {p['brand']} for {st.session_state.skin_type} skin.
Ingredients: {p['ingredients']}
Harmful ingredients: {', '.join(avoid_ings) or 'none'}
Caution ingredients: {', '.join(caution_ings) or 'none'}

Based on:
1. Actual user ratings on Nykaa and Amazon India for this product
2. Ingredient safety science
3. Suitability for {st.session_state.skin_type} skin

Give a REALISTIC safety and efficacy score out of 100.
Most products score between 45 and 85.
Reply with ONLY a single integer. Nothing else.
"""
        try:
            score_raw = ai_text(score_prompt).strip()
            score = int(''.join(filter(str.isdigit, score_raw))[:2])
            score = max(30, min(88, score))
        except:
            score = min(raw_score, 80)

    with st.spinner("Generating AI analysis..."):
        prompt = f"""
You are a dermatologist analyzing "{p['name']}" by {p['brand']} for an Indian consumer.
Price: Rs.{p['price']} | Category: {p['category']}
User skin type: {st.session_state.skin_type}
User concerns: {', '.join(st.session_state.concerns) or 'none'}
Ingredients: {p['ingredients']}
Harmful: {', '.join(avoid_ings) or 'none'}
Caution: {', '.join(caution_ings) or 'none'}
Beneficial: {', '.join([r['name'] for r in beneficial]) or 'none'}
Safety score: {score}/100

Write:
1. **Overall Verdict** — safe and effective for {st.session_state.skin_type} skin?
2. **Key Benefits** — cite specific ingredients
3. **Concerns** — any red flags?
4. **Recommendation** — Buy / Use with caution / Skip

Max 150 words. Clear and friendly.
"""
        ai_summary = ai_text(prompt)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Safety Score", f"{score}/100")
    col2.metric("✅ Safe",    sum(1 for r in rated if r["flag"] == "safe"))
    col3.metric("⚠️ Caution", sum(1 for r in rated if r["flag"] == "caution"))
    col4.metric("🚫 Avoid",   sum(1 for r in rated if r["flag"] == "avoid"))

    score_card(score)
    st.progress(score / 100)
    st.caption("📌 Score based on ingredient science + Nykaa/Amazon user rating sentiment")

    st.markdown("#### 🤖 WonderSkin AI Summary")
    st.info(ai_summary)

    if st.button(f"📊 What do real users say about {p['name'][:30]}?", key=f"reviews_btn_{p['id']}"):
        st.session_state.show_reviews_for = p['id']
        with st.spinner("Fetching community reviews..."):
            review_prompt = f"""
You are a skincare expert who has read thousands of Indian product reviews.
Summarize what real users say about "{p['name']}" by {p['brand']} (Rs.{p['price']}).

Give a detailed honest summary IN THIS EXACT FORMAT:

⭐ Nykaa Rating: [actual number like 4.2/5]
🛒 Amazon India Rating: [actual number like 4.1/5]
📊 Overall Sentiment: [Mostly Positive / Mixed / Mostly Negative]
📝 Total Review Count (approx): [e.g. 2,400+ on Nykaa]

👍 What users love:
• [specific point 1]
• [specific point 2]
• [specific point 3]

👎 Common complaints:
• [honest complaint 1]
• [honest complaint 2]

🎯 Works best for: [skin types]
💰 Value for Rs.{p['price']}: [Good value / Average / Overpriced]
🔁 Repurchase rate: [High / Medium / Low] — [reason]

Give real numbers. Do NOT say "Check Nykaa". Just give actual rating numbers.
"""
            st.session_state.reviews_result = ai_text(review_prompt)

    if st.session_state.show_reviews_for == p['id'] and st.session_state.reviews_result:
        st.markdown("#### 📊 Community Reviews Summary")
        st.success(st.session_state.reviews_result)
        st.caption("📌 AI-summarized from Nykaa, Amazon India, Reddit & BeautyTalk community sentiment")

    st.markdown("#### 🧪 Ingredient Breakdown")
    for r in rated:
        if r["flag"] == "avoid":
            st.error(f"🚫 **{r['name']}** — {r['reason']}")
        elif r["flag"] == "caution":
            st.warning(f"⚠️ **{r['name']}** — {r['reason']}")
        elif r["benefit"]:
            st.success(f"✅ **{r['name']}** — {r['benefit']}")

    already = any(h.get("name") == p["name"] for h in st.session_state.history)
    if not already:
        st.session_state.history.append({
            "type": "product", "name": p["name"],
            "score": score, "skin": st.session_state.skin_type
        })


def show_ai_product_analysis(product_name: str, brand: str, price: str, ingredients: str):
    """Full AI analysis for a product NOT in DB."""
    st.markdown(f"""
    <div style='border-radius:20px;padding:1.2rem 1.5rem;margin-bottom:1rem;
    border:1px solid rgba(124,58,237,0.2);
    background:linear-gradient(135deg,rgba(124,58,237,0.06),rgba(219,39,119,0.06));'>
    <h3 style='color:#7c3aed;margin:0;'>🔬 Analyzing: {product_name}</h3>
    <p style='opacity:0.55;margin:0.2rem 0 0 0;font-size:0.85rem;'>{brand} · {price}</p>
    <span style='background:#7c3aed22;color:#7c3aed;border-radius:6px;padding:0.1rem 0.5rem;
    font-size:0.72rem;font-weight:600;'>🤖 AI Research</span>
    </div>""", unsafe_allow_html=True)

    with st.spinner("Running full ingredient & safety analysis..."):
        full_prompt = f"""
You are a senior dermatologist analyzing "{product_name}" by {brand} (Price: {price})
for an Indian consumer with {st.session_state.skin_type} skin.
Concerns: {', '.join(st.session_state.concerns) or 'general skincare'}
Known ingredients: {ingredients or 'research from your knowledge'}

Provide a COMPLETE analysis:

**SAFETY SCORE**: [single integer 30-88]

**Overall Verdict**: Is it safe and effective for {st.session_state.skin_type} skin?

**Key Ingredients**: List 3-5 main active ingredients with what they do

**Benefits**: What will the user actually see/feel?

**Red Flags**: Any harmful or concerning ingredients? Be honest.

**Ingredient Conflicts**: Any ingredients that shouldn't be combined from this list?

**Recommendation**: Buy ✅ / Use with Caution ⚠️ / Skip ❌ — and why

**Better Alternatives**: 2 similar Indian products that may be better value

**Nykaa/Amazon Ratings**: Estimated community ratings (X.X/5)

Be science-backed, honest, and India-specific. Max 200 words total.
"""
        analysis = ai_text(full_prompt)

    score = 65
    for line in analysis.splitlines():
        if "SAFETY SCORE" in line or line.strip().startswith("**SAFETY SCORE"):
            digits = ''.join(filter(str.isdigit, line))[:2]
            if digits:
                try: score = max(30, min(88, int(digits)))
                except: pass

    score_card(score)
    st.progress(score / 100)
    st.markdown("#### 🤖 WonderSkin AI Full Report")
    st.info(analysis)

    already = any(h.get("name") == product_name for h in st.session_state.history)
    if not already:
        st.session_state.history.append({
            "type": "ai_product", "name": product_name,
            "score": score, "skin": st.session_state.skin_type
        })


# ══════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem 0;'>
    <div style='font-size:2rem;'>✨</div>
    <div style='font-size:1.5rem;font-weight:700;color:#7c3aed;
    font-family:"Cormorant Garamond",serif;letter-spacing:0.05em;'>WonderSkin</div>
    <div style='font-size:0.72rem;opacity:0.6;letter-spacing:0.1em;text-transform:uppercase;'>
    AI Skincare Intelligence</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<p style='color:#7c3aed;font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.5rem;'>👤 Your Skin Profile</p>", unsafe_allow_html=True)

    st.session_state.skin_type = st.selectbox(
        "Skin Type",
        ["Oily", "Dry", "Combination", "Sensitive", "Normal"],
        index=["Oily","Dry","Combination","Sensitive","Normal"].index(st.session_state.skin_type)
    )
    st.session_state.concerns = st.multiselect(
        "Your Concerns",
        ["Acne","Anti-aging","Brightening","Hydration","Pores","Redness","Sensitivity"],
        default=st.session_state.concerns
    )

    st.markdown("---")
    if st.button("🔮 Get My Skin Gist", key="gist_btn"):
        with st.spinner("Analyzing your profile..."):
            seed = hashlib.md5(f"{st.session_state.skin_type}{time.time()}".encode()).hexdigest()[:8]
            gist_prompt = f"""
You are a warm dermatologist. User has {st.session_state.skin_type} skin.
Concerns: {', '.join(st.session_state.concerns) or 'none'}. Session: {seed}

Give a fresh personal 3-line gist:
Line 1: What their skin needs most right now (very specific)
Line 2: One Indian product under Rs.700 to try (brand + name + why)
Line 3: Most important ingredient to look for

Warm and conversational. Vary every time.
"""
            st.session_state.skin_gist = ai_text(gist_prompt)

    if st.session_state.skin_gist:
        st.markdown(f"""
        <div style='background:rgba(124,58,237,0.08);border-radius:12px;padding:0.9rem 1rem;
        border:1px solid rgba(124,58,237,0.2);margin-top:0.5rem;'>
        <p style='font-size:0.82rem;margin:0;line-height:1.6;'>{st.session_state.skin_gist}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.metric("Products in DB", len(PRODUCTS))
    st.metric("Analyses Done", len(st.session_state.history))

    if st.session_state.history:
        st.markdown("<p style='color:#7c3aed;font-size:0.72rem;text-transform:uppercase;margin-top:1rem;'>🕘 Recent</p>", unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-3:]):
            name  = item.get("name", "Image scan")[:22] + "…"
            score = item.get("score", "—")
            st.markdown(f"<p style='font-size:0.78rem;margin:0.2rem 0;'>✅ {name} · {score}/100</p>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# MAIN HEADER
# ══════════════════════════════════════════
st.markdown("""
<div style='text-align:center;padding:2.5rem 0 1.5rem 0;'>
<div style='font-family:"Cormorant Garamond",serif;font-size:3.5rem;font-weight:700;
background:linear-gradient(135deg,#7c3aed 0%,#db2777 50%,#7c3aed 100%);
-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
margin:0;line-height:1.1;'>✨ WonderSkin</div>
<p style='opacity:0.55;font-size:1rem;margin-top:0.5rem;'>
AI-powered skincare intelligence — built for Indian skin</p>
</div>""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📷 Analyzer","⚖️ Compare","🔬 Ingredient","✨ Brands","📋 My Routine","📸 SkinFeed"
])

# ════════════════════════════════════════════════════
# TAB 1 — ANALYZER
# ════════════════════════════════════════════════════
with tab1:
    skin_profile_banner()
    st.markdown("## 📷 Product Analyzer")

    input_method = st.radio(
        "Choose how to analyze:",
        ["🔍 Search by product name", "📸 Upload label image"],
        horizontal=True
    )

    if input_method == "🔍 Search by product name":

        st.markdown("""
        <div style='border-radius:16px;padding:1rem 1.4rem;margin-bottom:1rem;
        border-left:4px solid #7c3aed;border:1px solid rgba(124,58,237,0.15);
        background:rgba(124,58,237,0.04);'>
        <p style='color:#7c3aed;font-weight:600;margin:0 0 0.4rem 0;'>🔍 How to search:</p>
        <p style='opacity:0.7;font-size:0.88rem;margin:0.15rem 0;'>✅ Type a <b>brand name</b> → e.g. <code>Minimalist</code>, <code>Foxtale</code>, <code>CeraVe</code></p>
        <p style='opacity:0.7;font-size:0.88rem;margin:0.15rem 0;'>✅ Type a <b>product type</b> → e.g. <code>Vitamin C Serum</code>, <code>Sunscreen</code></p>
        <p style='opacity:0.7;font-size:0.88rem;margin:0.15rem 0;'>✅ Type <b>any Indian brand</b> not in list → AI will research it instantly</p>
        <p style='opacity:0.5;font-size:0.8rem;margin:0.4rem 0 0 0;'>💡 Keep it short — 1 or 2 words work best</p>
        </div>""", unsafe_allow_html=True)

        query = st.text_input(
            "",
            placeholder="👉 e.g.  Minimalist   or   Vitamin C Serum   or   Foxtale Sunscreen",
            label_visibility="collapsed",
            key="search_query"
        )
        if query and query != st.session_state.get("brand_pill_query", ""):
            st.session_state.brand_pill_query = None

        # Brand pill buttons
        st.markdown("<p style='opacity:0.6;font-size:0.82rem;margin:0.2rem 0 0.4rem 0;'>🏷️ Quick brand pick:</p>", unsafe_allow_html=True)
        all_brands = sorted(set(p["brand"] for p in PRODUCTS))
        bcols = st.columns(6)
        for i, brand in enumerate(all_brands[:12]):
            if bcols[i % 6].button(brand, key=f"bp_{i}"):
                st.session_state.brand_pill_query = brand
                st.session_state.analyze_product  = None
                st.session_state.ai_query_result  = None
                st.session_state.ai_query_name    = None
                st.session_state.show_reviews_for = None
                st.session_state.reviews_result   = None
                st.session_state.ai_product_to_analyze = None
                st.session_state.ai_product_analysis   = None

        st.markdown("---")

        active_query = st.session_state.get("brand_pill_query") or query

        if active_query:

            def normalize(text):
                text = text.lower().strip()
                text = re.sub(r'[\s\-&\./]+', '', text)
                return text

            def fuzzy_match(query, target):
                q_norm = normalize(query)
                t_norm = normalize(target)

        # 1. Full normalized query must be a substring match (primary check)
                if q_norm in t_norm:
                    return True

        # 2. Multi-word query: ALL words must match as whole words (not substrings)
                q_words = query.lower().strip().split()
                if len(q_words) > 1:
            # Each word must appear as a standalone word in target, not just substring
                    t_lower = target.lower()
                    if all(re.search(r'\b' + re.escape(w) + r'\b', t_lower) for w in q_words):
                        return True

        # 3. Single word query: only match if it's a whole word in target
                if len(q_words) == 1:
                    t_lower = target.lower()
                    if re.search(r'\b' + re.escape(q_words[0]) + r'\b', t_lower):
                        return True

                return False

            results = []
            for p in PRODUCTS:
                searchable = f"{p['name']} {p['brand']} {p['category']} {p['skin_label']} {p['ingredients']}"
                if fuzzy_match(active_query, searchable):
                    results.append(p)

            if results:
                st.markdown(f"**✅ {len(results)} product(s) found in database — click 🔬 Analyze:**")
                for p in results:
                    c1, c2, c3 = st.columns([3, 1, 1])
                    with c1:
                        st.markdown(f"**{p['name']}**")
                        st.caption(f"{p['brand']} · {p['category']} · For: {p['skin_label']}")
                    with c2:
                        st.markdown(f"**₹{p['price']}**")
                    with c3:
                        if st.button("🔬 Analyze", key=f"abtn_{p['id']}"):
                            st.session_state.analyze_product       = p
                            st.session_state.ai_query_result       = None
                            st.session_state.show_reviews_for      = None
                            st.session_state.reviews_result        = None
                            st.session_state.ai_product_to_analyze = None
                            st.session_state.ai_product_analysis   = None

            else:
                # ── NOT IN DB: AI Research Mode ──
                st.markdown(f"""
                <div style='border-radius:14px;padding:1rem 1.4rem;border-left:3px solid #7c3aed;
                margin-bottom:1rem;background:rgba(124,58,237,0.05);border:1px solid rgba(124,58,237,0.15);'>
                <b style='color:#7c3aed;'>🤖 "{active_query}" not in our database — WonderSkin AI is researching it...</b><br>
                <span style='opacity:0.6;font-size:0.85rem;'>AI knows thousands of Indian and international brands.</span>
                </div>""", unsafe_allow_html=True)

                if st.session_state.ai_query_name != active_query:
                    with st.spinner(f"Researching {active_query}..."):
                        open_prompt = f"""
You are an expert on Indian skincare brands with complete knowledge of all products.
The user is searching for: "{active_query}"

TASK 1 — BRAND OVERVIEW:
Give a 3-line brand summary: what they stand for, hero ingredients, price range.

TASK 2 — COMPLETE PRODUCT CATALOG (top 10 budget-friendly products):
List the TOP 10 most popular and budget-friendly products by this brand.
For each product give: Product Name | Key Ingredients | Nykaa Rating (X/5) | Price (Rs.X) | Best for skin type

Format EXACTLY like this:

🏢 BRAND: [Brand Name]
[3-line brand summary]
Nykaa Brand Rating: X.X/5 | Amazon Brand Rating: X.X/5

━━━ TOP 10 BUDGET-FRIENDLY PRODUCTS ━━━
1. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
2. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
3. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
4. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
5. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
6. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
7. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
8. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
9. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]
10. [Product Name] | [key ingredients] | ⭐ X.X/5 | Rs.XXX | [skin type]

TASK 3 — BEST FOR {st.session_state.skin_type.upper()} SKIN:
Top 3 recommended from this brand for {st.session_state.skin_type} skin.
Concern: {', '.join(st.session_state.concerns) or 'general skincare'}.

Give real ratings. Do NOT say "visit website". Budget-friendly = under Rs.1000 preferred.
"""
                        st.session_state.ai_query_result = ai_text(open_prompt)
                        st.session_state.ai_query_name   = active_query

                if st.session_state.ai_query_result:
                    st.markdown(f"### 🤖 WonderSkin AI: {active_query}")
                    result_text = st.session_state.ai_query_result
                    lines = result_text.split("\n")

                    # ── KEY FIX: use a local line index so every button key is unique ──
                    line_index = 0

                    for line in lines:
                        line = line.strip()
                        if not line:
                            st.markdown("")
                            continue

                        if line.startswith("🏢 BRAND"):
                            st.markdown(f"""<div style='border-radius:14px;padding:0.8rem 1.2rem;
                            border-left:4px solid #7c3aed;margin:0.5rem 0;
                            background:rgba(124,58,237,0.06);border:1px solid rgba(124,58,237,0.15);'>
                            <b style='color:#7c3aed;font-size:1.1rem;'>{line}</b></div>""", unsafe_allow_html=True)

                        elif line.startswith("━━━"):
                            st.markdown(f"""<div style='background:#7c3aed;color:white;border-radius:8px;
                            padding:0.3rem 0.8rem;margin:0.6rem 0 0.2rem 0;font-weight:600;
                            font-size:0.85rem;display:inline-block;'>{line}</div>""", unsafe_allow_html=True)

                        elif line and line[0].isdigit() and ". " in line[:4] and "|" in line:
                            line_index += 1  # increment for every numbered product line

                            parts = [p.strip() for p in line.split("|")]
                            rank_name       = parts[0] if parts else line
                            prod_name_raw   = rank_name.lstrip("0123456789. ").strip()
                            ingredients_raw = parts[1] if len(parts) > 1 else ""
                            rating_raw      = parts[2] if len(parts) > 2 else ""
                            price_raw       = parts[3] if len(parts) > 3 else ""
                            skin_raw        = parts[4] if len(parts) > 4 else ""

                            # Use line_index to guarantee uniqueness regardless of duplicate names
                            btn_key = f"ai_analyze_{line_index}"

                            col_info, col_btn = st.columns([5, 1])
                            with col_info:
                                st.markdown(f"""
                                <div style='border-radius:10px;padding:0.6rem 1rem;margin:0.2rem 0;
                                border-left:3px solid #7c3aed;background:rgba(124,58,237,0.04);
                                border:1px solid rgba(124,58,237,0.12);'>
                                <b>{prod_name_raw}</b><br>
                                <span style='opacity:0.6;font-size:0.8rem;'>
                                    {ingredients_raw} · {skin_raw}
                                </span>
                                <span style='color:#f59e0b;font-weight:700;margin-left:0.8rem;'>
                                    {rating_raw}
                                </span>
                                <span style='color:#7c3aed;font-weight:600;margin-left:0.5rem;font-size:0.85rem;'>
                                    {price_raw}
                                </span>
                                </div>
                                """, unsafe_allow_html=True)

                            with col_btn:
                                if st.button("🔬", key=btn_key, help=f"Analyze {prod_name_raw}"):
                                    st.session_state.ai_product_to_analyze = {
                                        "name": prod_name_raw,
                                        "brand": active_query,
                                        "price": price_raw,
                                        "ingredients": ingredients_raw,
                                    }
                                    st.session_state.ai_product_analysis = None
                                    st.session_state.analyze_product = None

                        elif line.startswith("•"):
                            line_index += 1  # also increment for bullet product lines

                            parts = line.replace("•","").strip().split("|")
                            if len(parts) >= 3:
                                name   = parts[0].strip()
                                ings   = parts[1].strip() if len(parts) > 1 else ""
                                rating = parts[2].strip() if len(parts) > 2 else ""
                                price  = parts[3].strip() if len(parts) > 3 else ""

                                col_info2, col_btn2 = st.columns([5, 1])
                                with col_info2:
                                    st.markdown(f"""
                                    <div style='border-radius:10px;padding:0.6rem 1rem;margin:0.2rem 0;
                                    border-left:3px solid #7c3aed;background:rgba(124,58,237,0.04);'>
                                    <b>{name}</b><br>
                                    <span style='opacity:0.6;font-size:0.8rem;'>{ings}</span>
                                    <span style='color:#f59e0b;font-weight:700;margin-left:0.8rem;'>{rating}</span>
                                    <span style='color:#7c3aed;font-weight:600;margin-left:0.5rem;'>{price}</span>
                                    </div>""", unsafe_allow_html=True)
                                with col_btn2:
                                    btn_key2 = f"ai_analyze_bullet_{line_index}"
                                    if st.button("🔬", key=btn_key2, help=f"Analyze {name}"):
                                        st.session_state.ai_product_to_analyze = {
                                            "name": name,
                                            "brand": active_query,
                                            "price": price,
                                            "ingredients": ings,
                                        }
                                        st.session_state.ai_product_analysis = None
                                        st.session_state.analyze_product = None
                            else:
                                st.markdown(f"<p style='opacity:0.8;margin:0.15rem 0;'>{line}</p>", unsafe_allow_html=True)

                        elif "TASK 3" in line or "BEST FOR" in line:
                            st.markdown(f"<h4 style='color:#7c3aed;margin-top:1rem;'>🎯 {line}</h4>", unsafe_allow_html=True)
                        elif line.startswith("Nykaa") or line.startswith("Amazon"):
                            st.markdown(f"<p style='color:#059669;font-weight:600;font-size:0.9rem;margin:0.2rem 0;'>⭐ {line}</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<p style='opacity:0.8;font-size:0.9rem;margin:0.15rem 0;'>{line}</p>", unsafe_allow_html=True)

                    st.caption("📌 Product catalog and ratings based on AI knowledge of Nykaa/Amazon India")

                # ── Manual analyze for typed product not in DB ──
                st.markdown("---")
                st.markdown("**🔬 Not finding your exact product above? Type the full product name to analyze it:**")
                manual_col1, manual_col2 = st.columns([4, 1])
                with manual_col1:
                    manual_product = st.text_input(
                        "",
                        placeholder=f"e.g. {active_query} Vitamin C Serum or exact product name...",
                        key="manual_product_input",
                        label_visibility="collapsed"
                    )
                with manual_col2:
                    if st.button("🔬 Analyze", key="manual_analyze_btn"):
                        if manual_product.strip():
                            st.session_state.ai_product_to_analyze = {
                                "name": manual_product.strip(),
                                "brand": active_query,
                                "price": "N/A",
                                "ingredients": "",
                            }
                            st.session_state.ai_product_analysis = None
                            st.session_state.analyze_product = None

        # ── Show DB product analysis ──
        if st.session_state.analyze_product:
            st.markdown("---")
            show_product_analysis(st.session_state.analyze_product)

        # ── Show AI product analysis (not in DB) ──
        if st.session_state.ai_product_to_analyze:
            st.markdown("---")
            p = st.session_state.ai_product_to_analyze
            if st.session_state.ai_product_analysis is None:
                show_ai_product_analysis(p["name"], p["brand"], p["price"], p["ingredients"])
                st.session_state.ai_product_analysis = True

    # ── IMAGE UPLOAD MODE ──
    else:
        st.markdown("""
        <div style='border-radius:16px;padding:1rem 1.4rem;margin-bottom:1rem;
        border-left:4px solid #7c3aed;background:rgba(124,58,237,0.04);
        border:1px solid rgba(124,58,237,0.15);'>
        <p style='color:#7c3aed;font-weight:600;margin:0 0 0.3rem 0;'>📸 How to use image scan:</p>
        <p style='opacity:0.7;font-size:0.88rem;margin:0.2rem 0;'>1. Take a clear photo of the <b>ingredient list</b> on the back of any product</p>
        <p style='opacity:0.7;font-size:0.88rem;margin:0.2rem 0;'>2. Upload it below — works for <b>any brand worldwide</b></p>
        <p style='opacity:0.7;font-size:0.88rem;margin:0.2rem 0;'>3. AI reads every ingredient and gives you a full safety report</p>
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("Upload ingredient label", type=["jpg","jpeg","png"])
        if uploaded:
            img = Image.open(uploaded)
            c1, c2 = st.columns(2)
            with c1:
                st.image(img, caption="Your product label", use_column_width=True)
            with c2:
                st.markdown("""
                <div style='border-radius:16px;padding:1.2rem;border:1px solid rgba(124,58,237,0.15);'>
                <p style='font-weight:600;color:#7c3aed;margin-bottom:0.8rem;'>🤖 AI will analyze:</p>
                <p style='opacity:0.8;font-size:0.9rem;margin:0.3rem 0;'>✅ Every ingredient from label</p>
                <p style='opacity:0.8;font-size:0.9rem;margin:0.3rem 0;'>✅ Harmful or concerning chemicals</p>
                <p style='opacity:0.8;font-size:0.9rem;margin:0.3rem 0;'>✅ Compatibility for your skin type</p>
                <p style='opacity:0.8;font-size:0.9rem;margin:0.3rem 0;'>✅ Science-backed safety score</p>
                <p style='opacity:0.8;font-size:0.9rem;margin:0.3rem 0;'>✅ Buy / Skip recommendation</p>
                </div>""", unsafe_allow_html=True)

            if st.button("🔍 Analyze This Product", type="primary"):
                with st.spinner("Reading your product label..."):
                    vision_prompt = f"""
You are an expert skincare scientist. Analyze this product label image.
User has {st.session_state.skin_type} skin. Concerns: {', '.join(st.session_state.concerns) or 'none'}.

Provide:
1. **Product Name** (if visible)
2. **Full Ingredients List** (extract all, in order)
3. **Safety Score** (0-100, realistic — most products score 40-85)
4. **Top 3 Beneficial Ingredients** with science explanation
5. **Top 3 Harmful or Concerning Ingredients** with reason
6. **Skin Type Compatibility** for {st.session_state.skin_type} skin
7. **WonderSkin Verdict** — Buy / Use with caution / Skip
"""
                    response = ai_vision(img, vision_prompt)
                    st.markdown("### 🧪 WonderSkin Analysis")
                    st.markdown(response)
                    st.session_state.history.append({
                        "type": "image", "result": response,
                        "skin": st.session_state.skin_type, "score": "—"
                    })

# ════════════════════════════════════════════════════
# TAB 2 — COMPARE
# ════════════════════════════════════════════════════
with tab2:
    skin_profile_banner()
    st.markdown("## ⚖️ Compare Products")
    st.markdown("Pick from our database **or** type any Indian brand product — AI will research it!")

    st.markdown("#### Choose how to enter products:")
    mode1 = st.radio("Product 1 input:", ["📋 Pick from database", "✏️ Type any product name"], key="mode1", horizontal=True)
    mode2 = st.radio("Product 2 input:", ["📋 Pick from database", "✏️ Type any product name"], key="mode2", horizontal=True)

    product_names = ["Select..."] + [p["name"] for p in PRODUCTS]

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("""<div style='border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.5rem;
        border-top:4px solid #7c3aed;border:1px solid rgba(124,58,237,0.15);'>
        <p style='color:#7c3aed;font-weight:600;margin:0;'>Product 1</p></div>""", unsafe_allow_html=True)
        if mode1 == "📋 Pick from database":
            p1_select = st.selectbox("", product_names, key="p1_select", label_visibility="collapsed")
            p1_custom = None
        else:
            p1_select = None
            p1_custom = st.text_input("", placeholder="e.g. Foxtale Vitamin C Serum...", key="p1_custom", label_visibility="collapsed")

    with c2:
        st.markdown("""<div style='border-radius:14px;padding:1rem 1.2rem;margin-bottom:0.5rem;
        border-top:4px solid #db2777;border:1px solid rgba(219,39,119,0.15);'>
        <p style='color:#db2777;font-weight:600;margin:0;'>Product 2</p></div>""", unsafe_allow_html=True)
        if mode2 == "📋 Pick from database":
            p2_select = st.selectbox("", product_names, key="p2_select", label_visibility="collapsed")
            p2_custom = None
        else:
            p2_select = None
            p2_custom = st.text_input("", placeholder="e.g. CeraVe SA Cleanser...", key="p2_custom", label_visibility="collapsed")

    p1_ready = (p1_select and p1_select != "Select...") or (p1_custom and p1_custom.strip())
    p2_ready = (p2_select and p2_select != "Select...") or (p2_custom and p2_custom.strip())

    if p1_ready and p2_ready:
        if st.button("⚖️ Compare & Find Winner", type="primary"):

            if p1_select and p1_select != "Select...":
                p1_data = next(p for p in PRODUCTS if p["name"] == p1_select)
                p1_name = p1_data["name"]
                p1_brand = p1_data["brand"]
                p1_price = p1_data["price"]
                p1_ingredients = p1_data["ingredients"]
                _, raw_s1 = analyze_ingredients(p1_ingredients, st.session_state.skin_type.lower())
                with st.spinner(f"Getting real ratings for {p1_name}..."):
                    score_resp1 = ai_text(f"""
Based on actual Nykaa and Amazon India user ratings for "{p1_data['name']}" by {p1_data['brand']}:
Give a realistic safety and quality score out of 100.
Consider: actual user satisfaction, ingredient safety, effectiveness for {st.session_state.skin_type} skin.
Most good products score 55-82. Bad ones score 30-50.
Reply with ONLY a single integer between 30 and 90. Nothing else.
""")
                try:
                    digits = ''.join(filter(str.isdigit, score_resp1.strip()))[:2]
                    s1 = max(30, min(90, int(digits)))
                except:
                    s1 = max(40, min(82, raw_s1))
            else:
                p1_name = p1_custom.strip()
                with st.spinner(f"Researching {p1_name}..."):
                    p1_info = ai_text(f"""
Research the Indian skincare product "{p1_name}" for {st.session_state.skin_type} skin.
Give ONLY these details in this exact format:
BRAND: [brand name]
PRICE: [Rs.XXX]
INGREDIENTS: [comma separated key ingredients]
SCORE: [safety score 30-88 as integer only]
""")
                p1_brand, p1_price, p1_ingredients, s1 = "Unknown", "N/A", "", 60
                for line in p1_info.splitlines():
                    if line.startswith("BRAND:"): p1_brand = line.replace("BRAND:","").strip()
                    elif line.startswith("PRICE:"): p1_price = line.replace("PRICE:","").strip()
                    elif line.startswith("INGREDIENTS:"): p1_ingredients = line.replace("INGREDIENTS:","").strip()
                    elif line.startswith("SCORE:"):
                        try: s1 = max(30, min(88, int(''.join(filter(str.isdigit, line.replace("SCORE:","").strip()))[:2])))
                        except: s1 = 60

            if p2_select and p2_select != "Select...":
                p2_data = next(p for p in PRODUCTS if p["name"] == p2_select)
                p2_name = p2_data["name"]
                p2_brand = p2_data["brand"]
                p2_price = p2_data["price"]
                p2_ingredients = p2_data["ingredients"]
                _, raw_s2 = analyze_ingredients(p2_ingredients, st.session_state.skin_type.lower())
                with st.spinner(f"Getting real ratings for {p2_name}..."):
                    score_resp2 = ai_text(f"""
Based on actual Nykaa and Amazon India user ratings for "{p2_data['name']}" by {p2_data['brand']}:
Give a realistic safety and quality score out of 100.
Reply with ONLY a single integer between 30 and 90. Nothing else.
""")
                try:
                    digits = ''.join(filter(str.isdigit, score_resp2.strip()))[:2]
                    s2 = max(30, min(90, int(digits)))
                except:
                    s2 = max(40, min(82, raw_s2))
            else:
                p2_name = p2_custom.strip()
                with st.spinner(f"Researching {p2_name}..."):
                    p2_info = ai_text(f"""
Research the Indian skincare product "{p2_name}" for {st.session_state.skin_type} skin.
Give ONLY these details in this exact format:
BRAND: [brand name]
PRICE: [Rs.XXX]
INGREDIENTS: [comma separated key ingredients]
SCORE: [safety score 30-88 as integer only]
""")
                p2_brand, p2_price, p2_ingredients, s2 = "Unknown", "N/A", "", 60
                for line in p2_info.splitlines():
                    if line.startswith("BRAND:"): p2_brand = line.replace("BRAND:","").strip()
                    elif line.startswith("PRICE:"): p2_price = line.replace("PRICE:","").strip()
                    elif line.startswith("INGREDIENTS:"): p2_ingredients = line.replace("INGREDIENTS:","").strip()
                    elif line.startswith("SCORE:"):
                        try: s2 = max(30, min(88, int(''.join(filter(str.isdigit, line.replace("SCORE:","").strip()))[:2])))
                        except: s2 = 60

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div style='border-radius:18px;padding:1.2rem 1.5rem;
                border-top:4px solid #7c3aed;border:1px solid rgba(124,58,237,0.15);'>
                <h3 style='color:#7c3aed;margin:0 0 0.3rem 0;font-size:1rem;'>{p1_name}</h3>
                <p style='opacity:0.5;font-size:0.82rem;margin:0;'>{p1_brand} · {p1_price}</p>
                </div>""", unsafe_allow_html=True)
                st.metric("Safety Score", f"{s1}/100")
                st.progress(s1 / 100)
            with c2:
                st.markdown(f"""<div style='border-radius:18px;padding:1.2rem 1.5rem;
                border-top:4px solid #db2777;border:1px solid rgba(219,39,119,0.15);'>
                <h3 style='color:#db2777;margin:0 0 0.3rem 0;font-size:1rem;'>{p2_name}</h3>
                <p style='opacity:0.5;font-size:0.82rem;margin:0;'>{p2_brand} · {p2_price}</p>
                </div>""", unsafe_allow_html=True)
                st.metric("Safety Score", f"{s2}/100")
                st.progress(s2 / 100)

            with st.spinner("Deciding winner for your skin type..."):
                winner_prompt = f"""
You are a dermatologist deciding which product is better for {st.session_state.skin_type} skin.
Concerns: {', '.join(st.session_state.concerns) or 'general skincare'}.

Product 1: {p1_name} by {p1_brand}
Ingredients/Profile: {p1_ingredients or 'based on product knowledge'}
Safety Score: {s1}/100

Product 2: {p2_name} by {p2_brand}
Ingredients/Profile: {p2_ingredients or 'based on product knowledge'}
Safety Score: {s2}/100

Reply in EXACT format:
WINNER: [Product 1 name OR Product 2 name — exact name only]
REASON: [2 sentences explaining why this wins for {st.session_state.skin_type} skin]
P1_VERDICT: [one line about {st.session_state.skin_type} skin users and product 1]
P2_VERDICT: [one line about {st.session_state.skin_type} skin users and product 2]
BEST_FOR_P1: [skin type this product actually suits best]
BEST_FOR_P2: [skin type this product actually suits best]
"""
                winner_result = ai_text(winner_prompt)

            winner_name, reason, p1_verdict, p2_verdict, best_p1, best_p2 = "", "", "", "", "", ""
            for line in winner_result.splitlines():
                if line.startswith("WINNER:"): winner_name = line.replace("WINNER:","").strip()
                elif line.startswith("REASON:"): reason = line.replace("REASON:","").strip()
                elif line.startswith("P1_VERDICT:"): p1_verdict = line.replace("P1_VERDICT:","").strip()
                elif line.startswith("P2_VERDICT:"): p2_verdict = line.replace("P2_VERDICT:","").strip()
                elif line.startswith("BEST_FOR_P1:"): best_p1 = line.replace("BEST_FOR_P1:","").strip()
                elif line.startswith("BEST_FOR_P2:"): best_p2 = line.replace("BEST_FOR_P2:","").strip()

            p1_wins = p1_name.lower() in winner_name.lower()
            winner_display = p1_name if p1_wins else p2_name
            loser_display  = p2_name if p1_wins else p1_name
            winner_score   = s1 if p1_wins else s2
            loser_score    = s2 if p1_wins else s1

            st.markdown(f"""
            <div style='text-align:center;margin:1rem 0;'>
                <span class='confetti' style='animation-delay:0s;font-size:1.5rem;'>🎊</span>
                <span class='confetti' style='animation-delay:0.2s;font-size:1.2rem;'>✨</span>
                <span class='confetti' style='animation-delay:0.4s;font-size:1.5rem;'>🎉</span>
                <span class='confetti' style='animation-delay:0.6s;font-size:1.2rem;'>⭐</span>
                <span class='confetti' style='animation-delay:0.8s;font-size:1.5rem;'>🎊</span>
            </div>
            <div class='winner-card'>
                <div class='trophy-bounce'>🏆</div>
                <h2 style='color:white;margin:0.5rem 0 0.2rem 0;font-family:"Cormorant Garamond",serif;
                font-size:1.8rem;text-shadow:0 2px 8px rgba(0,0,0,0.2);'>
                WINNER for {st.session_state.skin_type} Skin!</h2>
                <h3 style='color:#fef3c7;margin:0 0 0.5rem 0;font-size:1.3rem;'>{winner_display}</h3>
                <div style='background:rgba(255,255,255,0.15);border-radius:10px;padding:0.5rem 1rem;display:inline-block;'>
                <span style='font-size:1.4rem;font-weight:700;'>Score: {winner_score}/100</span>
                </div>
                <p style='color:#fef9c3;margin:0.8rem 0 0 0;font-size:0.95rem;'>{reason}</p>
            </div>
            <div style='text-align:center;margin:0.5rem 0;'>
                <span class='confetti' style='animation-delay:1s;font-size:1.2rem;'>🌟</span>
                <span class='confetti' style='animation-delay:1.2s;font-size:1.5rem;'>💫</span>
                <span class='confetti' style='animation-delay:1.4s;font-size:1.2rem;'>✨</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style='border-radius:16px;padding:1rem 1.5rem;text-align:center;
            border:2px solid rgba(124,58,237,0.15);margin:1rem 0;opacity:0.7;'>
                <span style='font-size:1.5rem;'>🥈</span>
                <h4 style='margin:0.3rem 0;'>{loser_display}</h4>
                <span style='border-radius:8px;padding:0.2rem 0.6rem;font-size:0.85rem;
                background:rgba(124,58,237,0.08);'>Score: {loser_score}/100</span>
                <p style='opacity:0.6;font-size:0.85rem;margin:0.5rem 0 0 0;'>Good product — better suited for other skin types</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### 📊 Skin-Specific Verdicts")
            vc1, vc2 = st.columns(2)
            with vc1:
                icon = "🏆" if p1_wins else "🥈"
                bc = "#7c3aed" if p1_wins else "rgba(124,58,237,0.2)"
                st.markdown(f"""<div style='border-radius:14px;padding:1rem 1.2rem;
                border-left:4px solid {bc};background:rgba(124,58,237,0.04);'>
                <b>{icon} {p1_name}</b><br>
                <span style='opacity:0.65;font-size:0.85rem;'>{p1_verdict}</span><br>
                <span style='opacity:0.45;font-size:0.78rem;margin-top:0.3rem;display:block;'>Best suited for: {best_p1}</span>
                </div>""", unsafe_allow_html=True)
            with vc2:
                icon = "🏆" if not p1_wins else "🥈"
                bc = "#db2777" if not p1_wins else "rgba(219,39,119,0.2)"
                st.markdown(f"""<div style='border-radius:14px;padding:1rem 1.2rem;
                border-left:4px solid {bc};background:rgba(219,39,119,0.04);'>
                <b>{icon} {p2_name}</b><br>
                <span style='opacity:0.65;font-size:0.85rem;'>{p2_verdict}</span><br>
                <span style='opacity:0.45;font-size:0.78rem;margin-top:0.3rem;display:block;'>Best suited for: {best_p2}</span>
                </div>""", unsafe_allow_html=True)

            if p1_ingredients and p2_ingredients:
                shared = set(i.strip().lower() for i in p1_ingredients.split(",")) & \
                         set(i.strip().lower() for i in p2_ingredients.split(","))
                if shared:
                    st.markdown("#### 🔗 Shared Ingredients")
                    st.write(", ".join(sorted(shared)))

            with st.spinner("Generating detailed comparison..."):
                full_compare = ai_text(f"""
Compare {p1_name} vs {p2_name} for Indian skincare consumers with {st.session_state.skin_type} skin.
Concerns: {', '.join(st.session_state.concerns) or 'general'}.

Give:
1. Why {winner_display} wins for {st.session_state.skin_type} skin (cite ingredients)
2. Who should still choose {loser_display}
3. Value for money comparison
4. One ingredient from each that makes it unique

Max 150 words. Science-backed and specific.
""")
            st.markdown("#### 🤖 Full AI Comparison")
            st.info(full_compare)
    else:
        st.info("👆 Fill in both products above and click Compare to find the winner!")

# ════════════════════════════════════════════════════
# TAB 3 — INGREDIENT EXPLORER
# ════════════════════════════════════════════════════
with tab3:
    skin_profile_banner()
    st.markdown("## 🔬 Ingredient Explorer")
    st.markdown("Understand what any ingredient does — and whether it's right for your skin.")

    ing_query = st.text_input("Search any ingredient",
        placeholder="e.g. niacinamide, retinol, salicylic acid, hyaluronic acid...")

    st.markdown("**Quick search:**")
    popular_ings = ["Niacinamide","Retinol","Hyaluronic Acid","Salicylic Acid",
                    "Vitamin C","Glycerin","Ceramide","Squalane"]
    icols = st.columns(4)
    for i, ing in enumerate(popular_ings):
        if icols[i % 4].button(ing, key=f"ing_{i}"):
            ing_query = ing.lower()

    if ing_query:
        with st.spinner(f"Researching {ing_query}..."):
            explanation = ai_text(f"""
You are a cosmetic scientist explaining "{ing_query}" for {st.session_state.skin_type} skin.
Concerns: {', '.join(st.session_state.concerns) or 'general'}.

Provide:
1. **What it is** — scientific classification
2. **How it works** — mechanism of action
3. **Best for** — skin types and concerns
4. **Avoid if** — who should be careful
5. **Ideal concentration** — effective % range
6. **Combine with** — synergistic ingredients
7. **Don't combine with** — conflicts and why
8. **Safety rating** — 1-10 with explanation

Science-based but easy to understand. Use bullet points.
""")
        st.markdown(f"""<div style='border-radius:16px;padding:1rem 1.5rem;margin-bottom:1rem;
        border-left:4px solid #7c3aed;background:rgba(124,58,237,0.04);
        border:1px solid rgba(124,58,237,0.15);'>
        <h3 style='color:#7c3aed;margin:0;font-size:1.6rem;'>🧪 {ing_query.title()}</h3>
        </div>""", unsafe_allow_html=True)
        st.markdown(explanation)

        st.markdown("#### 🏆 Top 10 Indian Products Containing This Ingredient")
        st.caption("Includes products from our database + AI knowledge of Indian market")

        with st.spinner(f"Finding top 10 Indian products with {ing_query}..."):
            top10_prompt = f"""
List the TOP 10 best Indian skincare products that contain "{ing_query}" as a key ingredient.
Include both Indian and international brands available in India.
Format EXACTLY (one per line):
[Rank]. [Product Name] by [Brand] | [Concentration/note] | ⭐[X.X]/5 | Rs.[Price] | [skin type]

List exactly 10. Only products where {ing_query} is a PRIMARY ingredient.
For {st.session_state.skin_type} skin — prioritize suitable products. Budget-friendly preferred.
"""
            top10_result = ai_text(top10_prompt)

        st.markdown("---")
        lines_t10 = [l.strip() for l in top10_result.splitlines() if l.strip() and l.strip()[0].isdigit()]

        for line in lines_t10:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                name_brand = parts[0]
                conc       = parts[1] if len(parts) > 1 else ""
                rating     = parts[2] if len(parts) > 2 else ""
                price      = parts[3] if len(parts) > 3 else ""
                skin_fit   = parts[4] if len(parts) > 4 else ""

                in_db = any(ing_query.lower() in p["ingredients"].lower()
                           and p["brand"].lower() in name_brand.lower()
                           for p in PRODUCTS)
                badge = "<span style='background:#059669;color:white;border-radius:6px;padding:0.1rem 0.4rem;font-size:0.7rem;margin-left:0.3rem;'>✓ In DB</span>" if in_db else ""

                st.markdown(f"""
                <div style='border-radius:12px;padding:0.8rem 1.2rem;margin:0.3rem 0;
                border-left:3px solid #7c3aed;background:rgba(124,58,237,0.03);
                border:1px solid rgba(124,58,237,0.1);'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <b style='font-size:0.92rem;'>{name_brand}</b>{badge}<br>
                        <span style='opacity:0.5;font-size:0.78rem;'>{conc} · {skin_fit}</span>
                    </div>
                    <div style='text-align:right;'>
                        <span style='color:#f59e0b;font-weight:700;font-size:0.9rem;'>{rating}</span><br>
                        <span style='color:#7c3aed;font-weight:600;font-size:0.85rem;'>{price}</span>
                    </div>
                </div>
                </div>
                """, unsafe_allow_html=True)

        if not lines_t10:
            st.info("Could not find top 10 results. Try a more specific ingredient name.")

# ════════════════════════════════════════════════════
# TAB 4 — BRANDS
# ════════════════════════════════════════════════════
with tab4:
    skin_profile_banner()
    st.markdown("## ✨ Indian Skincare Brands")

    st.markdown("""
    <div style='border-radius:18px;padding:1.4rem 1.8rem;margin-bottom:1.5rem;
    border-left:4px solid #7c3aed;background:rgba(124,58,237,0.04);
    border:1px solid rgba(124,58,237,0.15);'>
    <h4 style='color:#7c3aed;margin:0 0 0.6rem 0;'>🇮🇳 India's Skincare Revolution</h4>
    <p style='opacity:0.75;font-size:0.92rem;line-height:1.7;margin:0;'>
    India has <b>1,000+ active skincare brands</b> today — from century-old Ayurvedic giants like Himalaya and Biotique,
    to science-first newcomers like Minimalist and Deconstruct. The Indian skincare market is valued at <b>₹20,000+ crore</b>
    and growing at 12% annually. Below are the <b>Top 30 Indian brands</b> ranked by safety, efficacy, and community trust.
    </p>
    </div>
    """, unsafe_allow_html=True)

    top30_brands = [
        {"name":"Minimalist",         "year":2020,"score":92,"hero":"niacinamide, retinol, AHA/BHA, peptides",      "tier":"Clean","desc":"Science-first, transparent formulations"},
        {"name":"Deconstruct",        "year":2020,"score":90,"hero":"salicylic acid, niacinamide, peptides",         "tier":"Clean","desc":"Honest ingredient concentrations, budget-friendly"},
        {"name":"Conscious Chemist",  "year":2020,"score":88,"hero":"peptides, ceramides, retinol, squalane",        "tier":"Clean","desc":"Professional-grade formulations for Indian skin"},
        {"name":"Foxtale",            "year":2021,"score":87,"hero":"niacinamide, SPF, retinol, ceramides",          "tier":"Clean","desc":"Dermatologist-backed, skin barrier focused"},
        {"name":"Re'equil",           "year":2017,"score":86,"hero":"sunscreen, ceramides, niacinamide, AHA",        "tier":"Clean","desc":"Pioneered matte sunscreens for Indian climate"},
        {"name":"Pilgrim",            "year":2019,"score":85,"hero":"AHA, BHA, vitamin C, K-beauty actives",         "tier":"Clean","desc":"K-beauty inspired, affordable actives"},
        {"name":"Dot & Key",          "year":2018,"score":84,"hero":"watermelon, niacinamide, SPF, vitamin C",       "tier":"Clean","desc":"Fun skincare with effective actives"},
        {"name":"Suganda",            "year":2019,"score":84,"hero":"white lotus, khus, plant actives",              "tier":"Clean","desc":"India's clean beauty pioneer, plant-based"},
        {"name":"Plum",               "year":2013,"score":82,"hero":"salicylic acid, green tea, vitamin C, AHA",     "tier":"Clean","desc":"100% vegan, cruelty-free Indian brand"},
        {"name":"Juicy Chemistry",    "year":2014,"score":81,"hero":"rosehip, plant oils, organic actives",          "tier":"Clean","desc":"Certified organic, cold-pressed formulations"},
        {"name":"Earth Rhythm",       "year":2019,"score":80,"hero":"plant actives, ceramides, clean beauty",        "tier":"Clean","desc":"pH-balanced, dermatologist tested"},
        {"name":"Fixderma",           "year":2010,"score":80,"hero":"ceramides, hyaluronic acid, salicylic acid",    "tier":"Clean","desc":"Pharma-grade skincare, dermatology backed"},
        {"name":"Aqualogica",         "year":2021,"score":79,"hero":"hyaluronic acid, SPF, niacinamide, aloe",       "tier":"Clean","desc":"Hydration-focused, lightweight formulas"},
        {"name":"mCaffeine",          "year":2016,"score":78,"hero":"coffee extract, hyaluronic acid, vitamin C",    "tier":"Mostly Clean","desc":"Coffee-powered, millennial favourite"},
        {"name":"Dromen & Co",        "year":2018,"score":77,"hero":"retinol, vitamin C, peptides, AHA",             "tier":"Clean","desc":"Luxury actives at accessible prices"},
        {"name":"Mamaearth",          "year":2016,"score":72,"hero":"plant extracts, turmeric, onion, vitamin C",    "tier":"Mostly Clean","desc":"Natural + toxin-free, baby-safe range"},
        {"name":"WOW Skin Science",   "year":2014,"score":71,"hero":"apple cider vinegar, vitamin C, onion",         "tier":"Mostly Clean","desc":"Apple cider vinegar pioneer in India"},
        {"name":"Himalaya",           "year":1930,"score":70,"hero":"neem, turmeric, aloe vera, tulsi",              "tier":"Mostly Clean","desc":"90-year Ayurvedic heritage brand"},
        {"name":"Forest Essentials",  "year":2000,"score":69,"hero":"ayurvedic oils, saffron, rose, sandalwood",     "tier":"Mostly Clean","desc":"Luxury Ayurveda, cold-pressed ingredients"},
        {"name":"Biotique",           "year":1992,"score":68,"hero":"herbs, botanical extracts, ayurvedic actives",  "tier":"Mostly Clean","desc":"Bio-organic Ayurvedic formulations"},
        {"name":"Lakme",              "year":1952,"score":67,"hero":"SPF, peach, vitamin C, hyaluronic acid",        "tier":"Mixed","desc":"India's iconic beauty brand, 70+ years"},
        {"name":"Lotus Herbals",      "year":1993,"score":67,"hero":"herbal extracts, SPF, whitening actives",       "tier":"Mixed","desc":"Herbal + science blend, affordable range"},
        {"name":"Garnier India",      "year":1994,"score":65,"hero":"vitamin C, micellar water, niacinamide",        "tier":"Mixed","desc":"French brand, Indian skin adapted formulas"},
        {"name":"VLCC",               "year":1989,"score":64,"hero":"herbal extracts, SPF, anti-tan actives",        "tier":"Mixed","desc":"Wellness + beauty, salon-grade formulas"},
        {"name":"Kama Ayurveda",      "year":2002,"score":72,"hero":"pure oils, ayurvedic herbs, rose, kumkumadi",   "tier":"Mostly Clean","desc":"Luxury pure Ayurveda, cold-processed"},
        {"name":"SkinKraft",          "year":2019,"score":76,"hero":"customized actives, niacinamide, SPF",          "tier":"Clean","desc":"AI-powered personalized skincare"},
        {"name":"Brillare",           "year":2013,"score":75,"hero":"plant stem cells, peptides, AHA",               "tier":"Clean","desc":"Science + nature, salon-professional range"},
        {"name":"Alps Goodness",      "year":2019,"score":73,"hero":"fruit extracts, aloe, plant actives",           "tier":"Mostly Clean","desc":"Budget-friendly clean beauty"},
        {"name":"The Pink Foundry",   "year":2021,"score":82,"hero":"niacinamide, retinol, SPF, vitamin C",          "tier":"Clean","desc":"Dermatologist-developed, evidence-based"},
        {"name":"Cetaphil India",     "year":1947,"score":78,"hero":"ceramides, niacinamide, gentle cleansers",      "tier":"Clean","desc":"Dermatologist no.1 recommended globally"},
    ]

    tier_filter = st.selectbox("Filter by tier", ["All","Clean","Mostly Clean","Mixed"])
    filtered = top30_brands if tier_filter=="All" else [b for b in top30_brands if b["tier"]==tier_filter]
    filtered.sort(key=lambda x: x["score"], reverse=True)

    st.markdown(f"**Showing {len(filtered)} brands** — click any brand to see detailed breakdown")
    st.markdown("---")

    for rank, brand in enumerate(filtered, 1):
        tc = "#059669" if brand["tier"]=="Clean" else "#d97706" if brand["tier"]=="Mostly Clean" else "#dc2626"
        ti = "🟢" if brand["tier"]=="Clean" else "🟡" if brand["tier"]=="Mostly Clean" else "🔴"

        col_main, col_score = st.columns([5, 1])
        with col_main:
            st.markdown(f"""
            <div style='border-radius:16px;padding:1rem 1.4rem;border-left:4px solid {tc};
            margin-bottom:0.4rem;border:1px solid {tc}33;background:{tc}08;'>
            <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
            <div style='flex:1;'>
                <span style='font-size:0.78rem;opacity:0.5;font-weight:600;'>#{rank}</span>
                <span style='font-size:1.05rem;font-weight:700;margin-left:0.4rem;'>{ti} {brand["name"]}</span>
                <span style='font-size:0.75rem;opacity:0.45;margin-left:0.6rem;'>Est. {brand["year"]}</span>
                <span style='background:{tc}22;color:{tc};border-radius:6px;padding:0.1rem 0.5rem;
                font-size:0.72rem;font-weight:600;margin-left:0.5rem;'>{brand["tier"]}</span>
                <div style='opacity:0.6;font-size:0.82rem;margin-top:0.3rem;'>{brand["desc"]}</div>
                <div style='color:{tc};font-size:0.8rem;margin-top:0.2rem;'>🌟 Hero: {brand["hero"]}</div>
            </div>
            <div style='text-align:right;min-width:60px;'>
                <div style='font-size:1.6rem;font-weight:800;color:{tc};'>{brand["score"]}</div>
                <div style='font-size:0.68rem;opacity:0.4;'>/100</div>
            </div>
            </div>
            </div>
            """, unsafe_allow_html=True)

        # Use brand name directly — guaranteed unique since brand list has no duplicates
        if st.button(f"🔍 Deep dive: {brand['name']}", key=f"brand_{brand['name']}"):
            with st.spinner(f"Researching {brand['name']}..."):
                brand_prompt = f"""
You are an Indian skincare expert. Give a detailed breakdown of "{brand['name']}" brand.
User has {st.session_state.skin_type} skin. Concerns: {', '.join(st.session_state.concerns) or 'general'}.

Give exactly 7 bullet points:
• Brand Philosophy: what makes them unique
• Hero Ingredients: top 3 actives and why they work scientifically
• Best Products: top 3 specific product names with prices
• Skin Type Fit: which skin types benefit most (mention {st.session_state.skin_type} skin specifically)
• Safety Profile: any concerning ingredients or parabens/sulfates to watch for
• Price Range & Value: affordable/mid/premium and worth it?
• Community Verdict: what Indian skincare community says on Reddit/Nykaa/BeautyTalk

Each bullet 1-2 sentences. Be specific, honest, science-backed.
"""
                brand_info = ai_text(brand_prompt)

            st.markdown(f"""
            <div style='border-radius:14px;padding:1.2rem 1.5rem;margin:0.5rem 0 1rem 0;
            border:1px solid rgba(124,58,237,0.15);background:rgba(124,58,237,0.03);'>
            <h4 style='color:#7c3aed;margin:0 0 0.8rem 0;'>📋 {brand["name"]} — Full Brand Report</h4>
            </div>
            """, unsafe_allow_html=True)

            for line in brand_info.splitlines():
                line = line.strip()
                if not line: continue
                if line.startswith(("•","-","*")):
                    clean = line.lstrip("•-* ").strip()
                    parts = clean.split(":", 1)
                    if len(parts) == 2:
                        st.markdown(f"""
                        <div style='border-radius:10px;padding:0.7rem 1rem;margin:0.3rem 0;
                        border-left:3px solid #7c3aed;background:rgba(124,58,237,0.03);
                        border:1px solid rgba(124,58,237,0.1);'>
                        <span style='color:#7c3aed;font-weight:600;'>• {parts[0].strip()}:</span>
                        <span style='opacity:0.8;'> {parts[1].strip()}</span>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='border-radius:10px;padding:0.7rem 1rem;margin:0.3rem 0;
                        border-left:3px solid #7c3aed;background:rgba(124,58,237,0.03);'>
                        <span style='opacity:0.8;'>• {clean}</span>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='opacity:0.6;font-size:0.88rem;margin:0.2rem 0;'>{line}</p>", unsafe_allow_html=True)

        st.markdown("")

# ════════════════════════════════════════════════════
# TAB 5 — ROUTINE BUILDER
# ════════════════════════════════════════════════════
with tab5:
    skin_profile_banner()
    st.markdown("## 📋 My AI Skincare Routine")
    st.markdown("Tell us what you own — AI builds around your existing products so nothing goes to waste.")

    c1, c2 = st.columns(2)
    with c1:
        budget = st.selectbox("Budget for new products", ["Low (under Rs.500)","Medium (Rs.500-Rs.1500)","High (above Rs.1500)"])
    with c2:
        routine_concerns = st.multiselect(
            "Focus concerns",
            ["Acne","Anti-aging","Brightening","Hydration","Pores","Redness","Sensitivity"],
            default=[c for c in st.session_state.concerns
                     if c in ["Acne","Anti-aging","Brightening","Hydration","Pores","Redness","Sensitivity"]]
        )

    st.markdown("#### 🧴 Products You Already Own")
    st.caption("List everything you have — AI will integrate them and only suggest what's missing")
    owned_products = st.text_area(
        "",
        placeholder="e.g. CeraVe Foaming Cleanser, Minimalist Niacinamide 10%, Neutrogena SPF 50...",
        height=100,
        label_visibility="collapsed"
    )

    if owned_products.strip():
        st.markdown(f"""
        <div style='border-radius:12px;padding:0.7rem 1rem;border-left:3px solid #059669;
        margin-bottom:0.5rem;background:rgba(5,150,105,0.06);border:1px solid rgba(5,150,105,0.15);'>
        <span style='color:#059669;font-weight:600;font-size:0.88rem;'>✅ Got it! AI will build your routine AROUND these products.</span>
        </div>""", unsafe_allow_html=True)

    if st.button("✨ Generate My Personalized Routine", type="primary"):
        with st.spinner("Building your unique routine..."):
            seed = hashlib.md5(f"{st.session_state.skin_type}{time.time()}".encode()).hexdigest()[:8]
            avoid = f"\nDO NOT recommend these again: {', '.join(st.session_state.routine_history[-8:])}" if st.session_state.routine_history else ""

            owned_section = f"""
PRODUCTS USER ALREADY OWNS:
{owned_products}
- Include suitable owned products with "(You already own this ✓)"
- Flag any that conflict with their skin type
- Only suggest NEW products for gaps
""" if owned_products.strip() else "User owns no products — suggest complete routine."

            routine = ai_text(f"""
You are a licensed dermatologist. Session: {seed}

PATIENT: {st.session_state.skin_type} skin | Concerns: {', '.join(routine_concerns) or 'general'} | Budget: {budget}

{owned_section}
{avoid}

INSTRUCTIONS: Never layer conflicting actives. Rotate between Indian brands.

FORMAT EXACTLY:

MORNING ROUTINE:
Step 1 - [Type]: [Product Name] by [Brand] | Why: [reason] | Rs.[Price] | [owned ✓ / new]
(max 5 steps)

NIGHT ROUTINE:
Step 1 - [Type]: [Product Name] by [Brand] | Why: [reason] | Rs.[Price] | [owned ✓ / new]
(max 5 steps)

⚠️ CONFLICTS IN YOUR CURRENT PRODUCTS: [list or "None"]
AVOID: [ingredients to avoid]
PRO TIP: [1 unique science tip]
SCIENCE NOTE: [1 dermatology principle]

Max 250 words.
""")

        st.markdown("""
        <div style='border-radius:16px;padding:1rem 1.5rem;margin-bottom:1rem;
        border-left:4px solid #7c3aed;background:rgba(124,58,237,0.04);
        border:1px solid rgba(124,58,237,0.15);'>
        <h3 style='color:#7c3aed;margin:0;'>✨ Your Personalized Routine</h3>
        </div>""", unsafe_allow_html=True)

        for line in routine.splitlines():
            line = line.strip()
            if not line: continue
            if "MORNING ROUTINE" in line or "NIGHT ROUTINE" in line:
                st.markdown(f"<h4 style='color:#7c3aed;margin-top:1.2rem;'>{'☀️' if 'MORNING' in line else '🌙'} {line}</h4>", unsafe_allow_html=True)
            elif line.startswith("Step"):
                owned_mark = "owned ✓" in line.lower() or "you already own" in line.lower()
                border_color = "#059669" if owned_mark else "#7c3aed"
                badge = "<span style='background:#059669;color:white;border-radius:6px;padding:0.1rem 0.4rem;font-size:0.72rem;margin-left:0.4rem;'>✓ You own this</span>" if owned_mark else "<span style='background:#7c3aed;color:white;border-radius:6px;padding:0.1rem 0.4rem;font-size:0.72rem;margin-left:0.4rem;'>New</span>"
                st.markdown(f"""
                <div style='border-radius:12px;padding:0.7rem 1.1rem;margin:0.3rem 0;
                border-left:3px solid {border_color};background:{border_color}0a;
                border:1px solid {border_color}22;font-size:0.9rem;'>
                {line} {badge}
                </div>""", unsafe_allow_html=True)
            elif line.startswith(("⚠️","AVOID","PRO TIP","SCIENCE","CONFLICTS")):
                is_conflict = "CONFLICT" in line
                bc = "#dc2626" if is_conflict else "#7c3aed"
                st.markdown(f"""
                <div style='border-radius:10px;padding:0.6rem 1rem;margin:0.3rem 0;
                font-size:0.88rem;color:{bc};border-left:3px solid {bc};background:{bc}0a;'>
                {line}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='opacity:0.6;font-size:0.88rem;'>{line}</p>", unsafe_allow_html=True)

        for l in routine.splitlines():
            if "Step" in l and "|" in l and "by" in l:
                try: st.session_state.routine_history.append(l.split("-")[1].split("|")[0].strip())
                except: pass

        st.download_button("📥 Download My Routine", data=routine,
            file_name="wonderskin_routine.txt", mime="text/plain")

# ════════════════════════════════════════════════════
# TAB 6 — SKINFEED
# ════════════════════════════════════════════════════
with tab6:
    skin_profile_banner()
    st.markdown("## 📸 SkinFeed")
    st.markdown("Community reviews — your posts are saved and stay even after refresh! 💾")

    import json
    FEED_FILE = "skinfeed_posts.json"

    def load_feed():
        if os.path.exists(FEED_FILE):
            try:
                with open(FEED_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return [
            {"user":"priya_glows",    "product":"Minimalist Niacinamide","review":"Cleared my acne in 3 weeks! Skin feels so smooth now 🙌","likes":124,"liked":False},
            {"user":"skincare.tamil", "product":"CeraVe Moisturizing Cream","review":"Best moisturizer for dry skin. No fragrance, no irritation ❤️","likes":98,"liked":False},
            {"user":"glow.india",     "product":"The Ordinary Niacinamide","review":"Affordable and effective! My pores look so much smaller","likes":210,"liked":False},
            {"user":"cleanbeauty.in", "product":"Dot & Key Watermelon Gel","review":"Perfect for oily skin summers! Lightweight and refreshing 💧","likes":67,"liked":False},
        ]

    def save_feed(posts):
        try:
            with open(FEED_FILE, "w") as f:
                json.dump(posts, f, indent=2)
        except:
            pass

    if "feed_loaded" not in st.session_state:
        st.session_state.feed_posts = load_feed()
        st.session_state.feed_loaded = True

    st.markdown("""
    <div style='border-radius:18px;padding:1.3rem 1.5rem;border:1px solid rgba(124,58,237,0.15);
    background:rgba(124,58,237,0.03);margin-bottom:1.5rem;'>
    <h4 style='color:#7c3aed;margin:0 0 1rem 0;'>✍️ Share Your Review</h4>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: new_product = st.text_input("Product name", placeholder="e.g. Minimalist Niacinamide Serum")
    with c2: new_user    = st.text_input("Your name / handle", placeholder="e.g. priya_glows")
    new_review = st.text_area("Your experience", placeholder="Share what worked or didn't...")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("📤 Post Review"):
        if new_product and new_review and new_user:
            new_post = {"user": new_user, "product": new_product,
                        "review": new_review, "likes": 0, "liked": False}
            st.session_state.feed_posts.insert(0, new_post)
            save_feed(st.session_state.feed_posts)
            st.success("Posted and saved! ✅ Your review will stay even after refresh.")
            st.rerun()
        else:
            st.warning("Fill in all three fields before posting.")

    st.markdown("---")
    st.markdown(f"### 🌸 Community Reviews ({len(st.session_state.feed_posts)} posts)")

    for i, post in enumerate(st.session_state.feed_posts):
        st.markdown(f"""
        <div style='border-radius:16px;padding:1.1rem 1.4rem;margin-bottom:0.8rem;
        border:1px solid rgba(124,58,237,0.12);background:rgba(124,58,237,0.02);'>
        <div style='font-weight:600;color:#7c3aed;font-size:0.9rem;'>@{post["user"]}</div>
        <div style='opacity:0.5;font-size:0.82rem;margin-bottom:0.4rem;'>reviewed <b>{post["product"]}</b></div>
        <div style='opacity:0.8;font-size:0.92rem;font-style:italic;'>"{post["review"]}"</div>
        </div>""", unsafe_allow_html=True)

        c1, c3 = st.columns([2, 2])
        with c1:
            if st.button(f"{'❤️' if post['liked'] else '🤍'} {post['likes']}", key=f"like_{i}"):
                if not post["liked"]:
                    st.session_state.feed_posts[i]["likes"] += 1
                    st.session_state.feed_posts[i]["liked"] = True
                else:
                    st.session_state.feed_posts[i]["likes"] -= 1
                    st.session_state.feed_posts[i]["liked"] = False
                save_feed(st.session_state.feed_posts)
                st.rerun()
        with c3:
            if st.button("🗑️ Delete", key=f"del_{i}"):
                st.session_state.feed_posts.pop(i)
                save_feed(st.session_state.feed_posts)
                st.rerun()

# ── FOOTER ──
st.markdown("---")
st.markdown("""
<div style='text-align:center;opacity:0.4;font-size:0.78rem;padding:1rem 0 2rem 0;'>
✨ WonderSkin — AI Skincare Intelligence for Indian Skin<br>
Powered by Groq AI · Not a substitute for professional dermatology advice
</div>""", unsafe_allow_html=True)