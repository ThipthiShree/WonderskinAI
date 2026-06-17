PRODUCTS = [
    # ── MINIMALIST ──
    {"id": 1,  "name": "Minimalist 10% Niacinamide Serum",      "brand": "Minimalist",     "category": "Serum",       "price": 599,  "skin_label": "oily,combination,acne",     "ingredients": "water, niacinamide, zinc pca, tamarindus indica seed extract, arginine, pentylene glycol, sodium benzoate"},
    {"id": 2,  "name": "Minimalist 0.3% Retinol Serum",         "brand": "Minimalist",     "category": "Serum",       "price": 649,  "skin_label": "dry,normal,aging",           "ingredients": "water, retinol, squalane, pentylene glycol, carbomer, sodium hydroxide, phenoxyethanol"},
    {"id": 3,  "name": "Minimalist 5% Vitamin C Serum",         "brand": "Minimalist",     "category": "Serum",       "price": 549,  "skin_label": "all,brightening",            "ingredients": "water, ascorbic acid, ferulic acid, vitamin e, hyaluronic acid, pentylene glycol"},
    {"id": 4,  "name": "Minimalist SPF 50 Sunscreen",           "brand": "Minimalist",     "category": "Sunscreen",   "price": 349,  "skin_label": "all",                        "ingredients": "water, zinc oxide, titanium dioxide, niacinamide, glycerin, phenoxyethanol"},

    # ── MAMAEARTH ──
    {"id": 5,  "name": "Mamaearth Ubtan Face Wash",             "brand": "Mamaearth",      "category": "Cleanser",    "price": 299,  "skin_label": "normal,combination",         "ingredients": "water, turmeric extract, saffron extract, chickpea flour, glycerin, coconut oil, sodium lauryl sulfate"},
    {"id": 6,  "name": "Mamaearth Vitamin C Serum",             "brand": "Mamaearth",      "category": "Serum",       "price": 549,  "skin_label": "all,brightening",            "ingredients": "water, ascorbic acid, turmeric extract, hyaluronic acid, glycerin, phenoxyethanol, fragrance"},
    {"id": 7,  "name": "Mamaearth Tea Tree Face Wash",          "brand": "Mamaearth",      "category": "Cleanser",    "price": 249,  "skin_label": "oily,acne",                  "ingredients": "water, tea tree oil, neem extract, salicylic acid, glycerin, sodium lauryl sulfate"},

    # ── DOT & KEY ──
    {"id": 8,  "name": "Dot & Key Watermelon Moisturizer",      "brand": "Dot & Key",      "category": "Moisturizer", "price": 495,  "skin_label": "oily,combination",           "ingredients": "water, watermelon extract, hyaluronic acid, glycerin, niacinamide, cetearyl alcohol, phenoxyethanol"},
    {"id": 9,  "name": "Dot & Key Pore Minimizing Serum",       "brand": "Dot & Key",      "category": "Serum",       "price": 595,  "skin_label": "oily,combination,acne",      "ingredients": "water, niacinamide, salicylic acid, zinc pca, glycerin, sodium hyaluronate"},
    {"id": 10, "name": "Dot & Key SPF 50 Sunscreen",            "brand": "Dot & Key",      "category": "Sunscreen",   "price": 595,  "skin_label": "all",                        "ingredients": "water, zinc oxide, niacinamide, hyaluronic acid, glycerin, titanium dioxide"},

    # ── MCAFFEINE ──
    {"id": 11, "name": "mCaffeine Coffee Face Wash",            "brand": "mCaffeine",      "category": "Cleanser",    "price": 349,  "skin_label": "oily,combination",           "ingredients": "water, coffee extract, hyaluronic acid, glycerin, sodium lauryl sulfate, phenoxyethanol"},
    {"id": 12, "name": "mCaffeine Coffee Body Lotion",          "brand": "mCaffeine",      "category": "Body",        "price": 449,  "skin_label": "all",                        "ingredients": "water, coffee extract, shea butter, glycerin, cetearyl alcohol, phenoxyethanol, fragrance"},
    {"id": 13, "name": "mCaffeine Naked Coffee Face Scrub",     "brand": "mCaffeine",      "category": "Scrub",       "price": 399,  "skin_label": "all",                        "ingredients": "water, coffee granules, coconut oil, shea butter, glycerin, cetearyl alcohol"},

    # ── PLUM ──
    {"id": 14, "name": "Plum Green Tea Pore Cleansing Wash",    "brand": "Plum",           "category": "Cleanser",    "price": 225,  "skin_label": "oily,acne,combination",      "ingredients": "water, green tea extract, glycerin, sodium lauryl sulfate, salicylic acid, phenoxyethanol"},
    {"id": 15, "name": "Plum 1% Salicylic Acid Serum",         "brand": "Plum",           "category": "Serum",       "price": 545,  "skin_label": "oily,acne",                  "ingredients": "water, salicylic acid, niacinamide, zinc pca, glycerin, sodium hyaluronate"},

    # ── HIMALAYA ──
    {"id": 16, "name": "Himalaya Purifying Neem Face Wash",     "brand": "Himalaya",       "category": "Cleanser",    "price": 175,  "skin_label": "oily,acne,combination",      "ingredients": "water, neem extract, turmeric, glycerin, sodium lauryl sulfate, citric acid"},
    {"id": 17, "name": "Himalaya Moisturizing Aloe Face Wash",  "brand": "Himalaya",       "category": "Cleanser",    "price": 175,  "skin_label": "dry,normal,sensitive",       "ingredients": "water, aloe vera extract, honey extract, glycerin, sodium lauryl sulfate"},

    # ── CERAVE ──
    {"id": 18, "name": "CeraVe Moisturizing Cream",            "brand": "CeraVe",         "category": "Moisturizer", "price": 1499, "skin_label": "dry,sensitive,normal",       "ingredients": "water, glycerin, ceramide np, ceramide ap, ceramide eop, hyaluronic acid, niacinamide, petrolatum, cetearyl alcohol, phenoxyethanol"},
    {"id": 19, "name": "CeraVe Foaming Facial Cleanser",       "brand": "CeraVe",         "category": "Cleanser",    "price": 999,  "skin_label": "oily,combination,normal",    "ingredients": "water, glycerin, niacinamide, ceramide np, ceramide ap, sodium lauryl sulfate, hyaluronic acid"},

    # ── THE ORDINARY ──
    {"id": 20, "name": "The Ordinary Niacinamide 10% + Zinc",  "brand": "The Ordinary",   "category": "Serum",       "price": 690,  "skin_label": "oily,combination,acne",      "ingredients": "water, niacinamide, zinc pca, tamarindus indica seed extract, arginine, glycerin, phenoxyethanol"},
    {"id": 21, "name": "The Ordinary Hyaluronic Acid 2% + B5", "brand": "The Ordinary",   "category": "Serum",       "price": 590,  "skin_label": "dry,normal,sensitive",       "ingredients": "water, hyaluronic acid, panthenol, glycerin, sodium hyaluronate, phenoxyethanol"},
    {"id": 22, "name": "The Ordinary AHA 30% BHA 2% Peel",     "brand": "The Ordinary",   "category": "Treatment",   "price": 790,  "skin_label": "oily,combination,acne",      "ingredients": "water, glycolic acid, salicylic acid, lactic acid, tartaric acid, hyaluronic acid, glycerin"},

    # ── NEUTROGENA ──
    {"id": 23, "name": "Neutrogena Ultra Sheer SPF 50+",        "brand": "Neutrogena",     "category": "Sunscreen",   "price": 699,  "skin_label": "all",                        "ingredients": "water, homosalate, octisalate, zinc oxide, glycerin, cetearyl alcohol, phenoxyethanol"},
    {"id": 24, "name": "Neutrogena Oil Free Acne Wash",         "brand": "Neutrogena",     "category": "Cleanser",    "price": 599,  "skin_label": "oily,acne",                  "ingredients": "water, salicylic acid, glycerin, sodium lauryl sulfate, aloe vera, phenoxyethanol"},

    # ── CETAPHIL ──
    {"id": 25, "name": "Cetaphil Gentle Skin Cleanser",         "brand": "Cetaphil",       "category": "Cleanser",    "price": 799,  "skin_label": "sensitive,dry,normal",       "ingredients": "water, glycerin, cetearyl alcohol, sodium lauryl sulfate, methylparaben, propylparaben"},
    {"id": 26, "name": "Cetaphil Moisturizing Cream",           "brand": "Cetaphil",       "category": "Moisturizer", "price": 899,  "skin_label": "dry,sensitive,normal",       "ingredients": "water, glycerin, petrolatum, cetearyl alcohol, niacinamide, panthenol, phenoxyethanol"},

    # ── GARNIER ──
    {"id": 27, "name": "Garnier Bright Complete Vitamin C Serum","brand": "Garnier",       "category": "Serum",       "price": 499,  "skin_label": "all,brightening",            "ingredients": "water, ascorbic acid, glycerin, niacinamide, lemon extract, phenoxyethanol, fragrance"},
    {"id": 28, "name": "Garnier Micellar Cleansing Water",      "brand": "Garnier",        "category": "Cleanser",    "price": 399,  "skin_label": "all,sensitive",              "ingredients": "water, glycerin, hexylene glycol, disodium cocoamphodiacetate, phenoxyethanol"},

    # ── LAKME ──
    {"id": 29, "name": "Lakme Sun Expert SPF 50",               "brand": "Lakme",          "category": "Sunscreen",   "price": 320,  "skin_label": "all",                        "ingredients": "water, zinc oxide, titanium dioxide, glycerin, cetearyl alcohol, phenoxyethanol, fragrance"},
    {"id": 30, "name": "Lakme Peach Milk Moisturizer",          "brand": "Lakme",          "category": "Moisturizer", "price": 249,  "skin_label": "normal,dry",                 "ingredients": "water, peach extract, milk protein, glycerin, cetearyl alcohol, mineral oil, fragrance"},

    # ── WOW ──
    {"id": 31, "name": "WOW Apple Cider Vinegar Face Wash",     "brand": "WOW",            "category": "Cleanser",    "price": 399,  "skin_label": "oily,combination,acne",      "ingredients": "water, apple cider vinegar, hyaluronic acid, glycerin, sodium lauryl sulfate, phenoxyethanol"},
    {"id": 32, "name": "WOW Vitamin C Serum",                   "brand": "WOW",            "category": "Serum",       "price": 599,  "skin_label": "all,brightening",            "ingredients": "water, ascorbic acid, hyaluronic acid, vitamin e, ferulic acid, glycerin"},

    # ── DECONSTRUCT ──
    {"id": 33, "name": "Deconstruct Brightening Serum",         "brand": "Deconstruct",    "category": "Serum",       "price": 695,  "skin_label": "all,brightening",            "ingredients": "water, niacinamide, alpha arbutin, hyaluronic acid, glycerin, phenoxyethanol"},
    {"id": 34, "name": "Deconstruct Exfoliating Toner",         "brand": "Deconstruct",    "category": "Toner",       "price": 545,  "skin_label": "oily,acne,combination",      "ingredients": "water, salicylic acid, glycolic acid, lactic acid, niacinamide, glycerin"},
    {"id": 35, "name": "Deconstruct Hydrating Moisturizer",     "brand": "Deconstruct",    "category": "Moisturizer", "price": 595,  "skin_label": "all",                        "ingredients": "water, hyaluronic acid, ceramide np, niacinamide, glycerin, squalane, phenoxyethanol"},

    # ── FOXTALE ──
    {"id": 36, "name": "Foxtale Dewy Sunscreen SPF 50",         "brand": "Foxtale",        "category": "Sunscreen",   "price": 649,  "skin_label": "all",                        "ingredients": "water, zinc oxide, niacinamide, hyaluronic acid, glycerin, titanium dioxide, phenoxyethanol"},
    {"id": 37, "name": "Foxtale Retinol Night Cream",           "brand": "Foxtale",        "category": "Moisturizer", "price": 849,  "skin_label": "dry,normal,aging",           "ingredients": "water, retinol, ceramide np, peptides, squalane, glycerin, phenoxyethanol"},
    {"id": 38, "name": "Foxtale Vitamin C Serum",               "brand": "Foxtale",        "category": "Serum",       "price": 749,  "skin_label": "all,brightening",            "ingredients": "water, ascorbic acid, niacinamide, ferulic acid, hyaluronic acid, glycerin"},

    # ── PILGRIM ──
    {"id": 39, "name": "Pilgrim Vitamin C Serum",               "brand": "Pilgrim",        "category": "Serum",       "price": 595,  "skin_label": "all,brightening",            "ingredients": "water, ascorbic acid, ferulic acid, vitamin e, hyaluronic acid, niacinamide, glycerin"},
    {"id": 40, "name": "Pilgrim AHA BHA Peel",                  "brand": "Pilgrim",        "category": "Treatment",   "price": 695,  "skin_label": "oily,combination,acne",      "ingredients": "water, glycolic acid, salicylic acid, lactic acid, green tea extract, aloe vera"},
    {"id": 41, "name": "Pilgrim Red Vine SPF 50",               "brand": "Pilgrim",        "category": "Sunscreen",   "price": 499,  "skin_label": "all",                        "ingredients": "water, zinc oxide, titanium dioxide, red vine extract, niacinamide, glycerin, phenoxyethanol"},

    # ── RE'EQUIL ──
    {"id": 42, "name": "Re'equil Ultra Matte Sunscreen",        "brand": "Re'equil",       "category": "Sunscreen",   "price": 595,  "skin_label": "oily,combination",           "ingredients": "water, zinc oxide, titanium dioxide, silica, glycerin, phenoxyethanol"},
    {"id": 43, "name": "Re'equil Ceramide Barrier Repair",      "brand": "Re'equil",       "category": "Moisturizer", "price": 799,  "skin_label": "dry,sensitive,normal",       "ingredients": "water, ceramide np, ceramide ap, niacinamide, hyaluronic acid, glycerin, squalane"},

    # ── CONSCIOUS CHEMIST ──
    {"id": 44, "name": "Conscious Chemist Peptide Serum",       "brand": "Conscious Chemist", "category": "Serum",    "price": 895,  "skin_label": "aging,dry,normal",           "ingredients": "water, peptides, ceramide np, hyaluronic acid, niacinamide, squalane, glycerin"},
    {"id": 45, "name": "Conscious Chemist Retinol Serum",       "brand": "Conscious Chemist", "category": "Serum",    "price": 995,  "skin_label": "aging,dry,normal",           "ingredients": "water, retinol, ceramide np, peptides, hyaluronic acid, squalane, glycerin"},

    # ── SUGANDA ──
    {"id": 46, "name": "Suganda White Lotus Serum",             "brand": "Suganda",        "category": "Serum",       "price": 750,  "skin_label": "sensitive,dry,normal",       "ingredients": "water, white lotus extract, hyaluronic acid, glycerin, niacinamide, aloe vera extract"},
    {"id": 47, "name": "Suganda Khus Toner",                    "brand": "Suganda",        "category": "Toner",       "price": 450,  "skin_label": "oily,combination,sensitive", "ingredients": "water, vetiver extract, witch hazel, glycerin, aloe vera extract, phenoxyethanol"},
    {"id": 48, "name": "Suganda Saffron Glow Serum",            "brand": "Suganda",        "category": "Serum",       "price": 850,  "skin_label": "all,brightening",            "ingredients": "water, saffron extract, vitamin c, hyaluronic acid, glycerin, niacinamide"},

    # ── JUICY CHEMISTRY ──
    {"id": 49, "name": "Juicy Chemistry Rosehip Face Oil",      "brand": "Juicy Chemistry", "category": "Serum",      "price": 995,  "skin_label": "dry,aging,sensitive",        "ingredients": "rosehip seed oil, sea buckthorn oil, jojoba oil, vitamin e, lavender essential oil"},
    {"id": 50, "name": "Juicy Chemistry Kumkumadi Night Cream", "brand": "Juicy Chemistry", "category": "Moisturizer","price": 1195, "skin_label": "dry,aging,normal",           "ingredients": "water, saffron extract, sandalwood oil, almond oil, shea butter, glycerin, vitamin e"},

    # ── EARTH RHYTHM ──
    {"id": 51, "name": "Earth Rhythm Vitamin C Face Wash",      "brand": "Earth Rhythm",   "category": "Cleanser",    "price": 395,  "skin_label": "all,brightening",            "ingredients": "water, ascorbic acid, aloe vera extract, glycerin, sodium lauryl sulfate, green tea extract"},
    {"id": 52, "name": "Earth Rhythm Ceramide Moisturizer",     "brand": "Earth Rhythm",   "category": "Moisturizer", "price": 695,  "skin_label": "dry,sensitive,normal",       "ingredients": "water, ceramide np, hyaluronic acid, squalane, glycerin, shea butter, phenoxyethanol"},
]

# ── HARMFUL INGREDIENTS ──
HARMFUL = {
    "sodium lauryl sulfate":  {"flag": "caution", "reason": "Can strip natural oils, may irritate sensitive skin"},
    "sodium laureth sulfate": {"flag": "caution", "reason": "Mild irritant for sensitive skin"},
    "fragrance":              {"flag": "caution", "reason": "Common allergen — avoid if skin is sensitive"},
    "parfum":                 {"flag": "caution", "reason": "Common allergen, may cause irritation"},
    "methylparaben":          {"flag": "avoid",   "reason": "Paraben preservative, potential hormone disruptor"},
    "propylparaben":          {"flag": "avoid",   "reason": "Paraben preservative, potential hormone disruptor"},
    "mineral oil":            {"flag": "caution", "reason": "Can clog pores for oily/acne-prone skin"},
    "alcohol denat":          {"flag": "caution", "reason": "Drying alcohol, may irritate sensitive skin"},
    "formaldehyde":           {"flag": "avoid",   "reason": "Known carcinogen, banned in many countries"},
    "homosalate":             {"flag": "caution", "reason": "Chemical UV filter with some safety concerns"},
}

# ── BENEFICIAL INGREDIENTS ──
BENEFICIAL = {
    "niacinamide":        {"benefit": "Reduces pores, controls oil, brightens skin"},
    "hyaluronic acid":    {"benefit": "Deep hydration, plumps and smooths skin"},
    "retinol":            {"benefit": "Anti-aging, boosts collagen, reduces fine lines"},
    "glycerin":           {"benefit": "Humectant — draws moisture into skin"},
    "ceramide np":        {"benefit": "Restores skin barrier, locks in moisture"},
    "ceramide ap":        {"benefit": "Supports skin barrier integrity"},
    "ceramide eop":       {"benefit": "Essential ceramide for barrier repair"},
    "salicylic acid":     {"benefit": "Unclogs pores, fights acne, exfoliates"},
    "ascorbic acid":      {"benefit": "Vitamin C — brightens, protects from UV damage"},
    "zinc oxide":         {"benefit": "Mineral SPF, calms inflammation"},
    "glycolic acid":      {"benefit": "AHA — exfoliates dead skin, improves texture"},
    "squalane":           {"benefit": "Lightweight moisturizer, non-comedogenic"},
    "green tea extract":  {"benefit": "Antioxidant, reduces redness and irritation"},
    "neem extract":       {"benefit": "Antibacterial, natural acne fighter"},
    "turmeric extract":   {"benefit": "Anti-inflammatory, brightening"},
    "aloe vera extract":  {"benefit": "Soothes, hydrates, calms irritation"},
    "ferulic acid":       {"benefit": "Boosts stability and effectiveness of Vitamin C"},
    "panthenol":          {"benefit": "Vitamin B5 — soothes, heals and softens skin"},
    "zinc pca":           {"benefit": "Controls sebum production, reduces acne"},
    "peptides":           {"benefit": "Boosts collagen, firms and plumps skin"},
    "shea butter":        {"benefit": "Rich moisturizer, repairs dry and cracked skin"},
    "titanium dioxide":   {"benefit": "Gentle mineral SPF, ideal for sensitive skin"},
    "sodium hyaluronate": {"benefit": "Smaller form of hyaluronic acid — penetrates deeper"},
    "alpha arbutin":      {"benefit": "Brightens dark spots, evens skin tone"},
    "lactic acid":        {"benefit": "Gentle AHA exfoliant, hydrating and brightening"},
    "witch hazel":        {"benefit": "Natural astringent, reduces redness and pores"},
    "rosehip seed oil":   {"benefit": "Rich in vitamins A and C, anti-aging and brightening"},
    "white lotus extract":{"benefit": "Antioxidant-rich, soothes and brightens"},
    "saffron extract":    {"benefit": "Brightening, antioxidant, evens skin tone"},
    "vetiver extract":    {"benefit": "Antibacterial, soothes oily and sensitive skin"},
}


def search_products(query, brand_filter=None):
    """Fuzzy multi-word search across name, brand, category, skin_label."""
    query_lower = query.lower().strip()
    query_words = query_lower.split()
    results = []
    for p in PRODUCTS:
        searchable = f"{p['name']} {p['brand']} {p['category']} {p['skin_label']}".lower()
        if any(word in searchable for word in query_words):
            if brand_filter and brand_filter != "All":
                if p["brand"] != brand_filter:
                    continue
            results.append(p)
    return results


def get_product_by_id(pid):
    for p in PRODUCTS:
        if p["id"] == pid:
            return p
    return None


def analyze_ingredients(ingredient_string, skin_type):
    """
    Analyze ingredient list and return (results, score).
    Score is realistic (typically 35–88 range).
    """
    ingredients = [i.strip().lower() for i in ingredient_string.split(",")]
    results = []

    for ing in ingredients:
        flag    = "safe"
        reason  = ""
        benefit = ""

        for harm_key, harm_val in HARMFUL.items():
            if harm_key in ing:
                flag   = harm_val["flag"]
                reason = harm_val["reason"]
                break

        for ben_key, ben_val in BENEFICIAL.items():
            if ben_key in ing:
                benefit = ben_val["benefit"]
                break

        results.append({
            "name"   : ing,
            "flag"   : flag,
            "reason" : reason,
            "benefit": benefit
        })

    total   = max(len(results), 1)
    avoid   = sum(1 for r in results if r["flag"] == "avoid")
    caution = sum(1 for r in results if r["flag"] == "caution")
    safe    = sum(1 for r in results if r["flag"] == "safe")

    # Realistic scoring formula
    base  = ((safe * 10) + (caution * 4)) / total
    score = int(base - (avoid * 12) - (caution * 1.2))
    score = max(25, min(88, score))  # Realistic range: 25–88

    return results, score