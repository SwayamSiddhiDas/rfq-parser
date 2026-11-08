

import re
import geonamescache

CATEGORY_KEYWORDS = [
    ("fibc", [
        "fibc", "f.i.b.c", "jumbo bag", "jumbo sack", "jambo bag", "jumbobag",
        "bulk bag", "bulkbag", "ton bag", "tonne bag", "big bag",
        "container bag", "baffle bag", "u-panel", "u panel",
        "4 loop", "four loop", "single loop", "jumbo",
    ]),
    ("bopp_bag", [
        "bopp bag", "bopp bags", "bopp sack", "bopp sacks", "bopp laminated",
        "bopp woven", "bopp pp", "bopp bori", "bopp katta",
        "multicolor bopp", "printed bopp", "boop bag", "bop bag",
    ]),
    ("mono_carton", [
        "mono carton", "monocarton", "mono-carton", "mono cartan", "mono cartoon",
        "duplex box", "duplex carton", "duplex board", "folding carton",
        "printed carton", "sbs carton", "pharma carton", "medicine box",
        "sweet box", "cake box",
    ]),
    ("corrugated_box", [
        "corrugated", "corugated", "corrugted", "corrogated",
        "3 ply", "3-ply", "3ply", "5 ply", "5-ply", "5ply",
        "7 ply", "7-ply", "7ply", "9 ply", "9-ply", "9ply",
        "master carton", "shipper carton", "shipping carton", "kraft box",
        "cardboard box", "packing box", "carton box", "cartoon box",
        "dabba", "peti", "boxes", "box",
    ]),
    ("pouch", [
        "pouch", "pouches", "poch", "pouche", "standup", "stand up", "stand-up",
        "zipper", "ziplock", "zip lock", "spout", "doypack",
        "center seal", "centre seal", "3 side seal", "three side seal",
        "quad seal", "gusset pouch", "pillow pouch", "vacuum bag",
        "retort", "sachet", "thaili",
    ]),
    ("film", [
        "bopp film", "shrink", "shrnk", "stretch", "strech", "strecth", "strach",
        "cling film", "ldpe film", "hdpe film", "lldpe film", "pet film",
        "bopet", "cpp film", "metpet", "mulch film", "silage film",
        "laminating film", "lamination film", "packaging film", "plastic roll",
        "laminated roll", "printed roll", "film roll", "sheet roll",
        "wrap", "film",
    ]),
    ("woven_sack", [
        "woven sack", "woven bag", "wooven", "wovan", "pp woven", "hdpe woven",
        "pp bag", "pp bags", "pp sack", "hdpe bag", "hdpe sack",
        "cement bag", "cement sack", "ad star", "ad-star", "adstar",
        "block bottom", "valve bag", "fertilizer bag", "sand bag",
        "sugar bag", "rice bag", "ata bag", "atta bag", "flour bag",
        "grain bag", "bori", "katta", "gunny", "rafia", "raffia",
        "woven", "sacks", "sack",
    ]),
]

SCALE_MULTIPLIERS = {
    "k": 1_000,
    "thousand": 1_000,
    "hazaar": 1_000,
    "hazar": 1_000,
    "hajar": 1_000,
    "hajaar": 1_000,
    "hzr": 1_000,
    "hjr": 1_000,
    "lakh": 100_000,
    "lakhs": 100_000,
    "lac": 100_000,
    "lacs": 100_000,
    "lkh": 100_000,
    "lack": 100_000,
    "lacks": 100_000,
    "cr": 10_000_000,
    "crore": 10_000_000,
    "crores": 10_000_000,
    "karod": 10_000_000,
}

HINDI_NUM_WORDS = {
    "ek": 1, "one": 1,
    "do": 2, "two": 2,
    "teen": 3, "three": 3,
    "chaar": 4, "char": 4, "four": 4,
    "paanch": 5, "panch": 5, "five": 5,
    "chhah": 6, "che": 6, "six": 6,
    "saat": 7, "sat": 7, "seven": 7,
    "aath": 8, "ath": 8, "eight": 8,
    "nau": 9, "nine": 9,
    "das": 10, "dus": 10, "ten": 10,
    "gyarah": 11, "barah": 12, "pandra": 15, "pandrah": 15,
    "bees": 20, "pachis": 25, "pachees": 25, "tees": 30,
    "chalis": 40, "pachas": 50, "saath": 60, "sattar": 70,
    "assi": 80, "nabbe": 90, "sau": 100,
    "dedh": 1.5, "dhai": 2.5, "sadhe": 0.5,
}

UNIT_ALIASES = {
    # pcs
    "pc": "pcs", "pcs": "pcs", "piece": "pcs", "pieces": "pcs",
    "pices": "pcs", "peices": "pcs", "pis": "pcs",
    "nos": "pcs", "no": "pcs", "nag": "pcs", "nug": "pcs",
    "unit": "pcs", "units": "pcs", "bag": "pcs", "bags": "pcs",
    "sack": "pcs", "sacks": "pcs", "box": "pcs", "boxes": "pcs",
    "carton": "pcs", "cartons": "pcs", "pouch": "pcs", "pouches": "pcs",
    "bori": "pcs", "katta": "pcs", "peti": "pcs", "dabba": "pcs",
    # kg
    "kg": "kg", "kgs": "kg", "kilo": "kg", "kilos": "kg",
    "kilogram": "kg", "kilograms": "kg",
    # mt
    "mt": "mt", "m.t": "mt", "m.t.": "mt", "ton": "mt", "tons": "mt",
    "tonne": "mt", "tonnes": "mt", "tns": "mt",
    "metric ton": "mt", "metric tons": "mt", "metric tonne": "mt", "metric tonnes": "mt",
}

LOCATION_STOPWORDS = {
    "bag", "bags", "box", "boxes", "film", "roll", "rolls", "pouch", "sack",
    "sacks", "carton", "mono", "jumbo", "bulk", "woven", "kraft", "plain",
    "printed", "white", "brown", "clear", "black", "blue", "green", "red",
    "yellow", "orange", "pink", "silver", "gold", "food", "grade", "sugar",
    "rice", "wheat", "cement", "sand", "salt", "flour", "atta", "maida",
    "fertilizer", "chemical", "seed", "seeds", "grain", "feed", "coal",
    "packing", "packaging", "pack", "wrap", "shrink", "stretch", "liner",
    "loop", "star", "ply", "layer", "gsm", "mic", "micron", "microns",
    "gauge", "inch", "mm", "cm", "meter", "kg", "kgs", "mt", "ton", "tons",
    "tonne", "pcs", "piece", "pieces", "nos", "nag", "unit", "units",
    "lakh", "lakhs", "lac", "lacs", "crore", "hazaar", "hazar", "thousand",
    "ek", "do", "teen", "char", "panch", "che", "saat", "aath", "nau", "das",
    "sau", "dedh", "dhai", "need", "want", "require", "required", "urgent",
    "quote", "quotation", "rate", "rates", "price", "best", "order", "buy",
    "supply", "supplier", "delivery", "deliver", "send", "for", "with",
    "from", "to", "in", "at", "on", "of", "and", "or", "the", "a", "an",
    "chahiye", "chaiye", "chahie", "bhejo", "batao", "dena", "lena", "hai",
    "mein", "me", "se", "ko", "ka", "ki", "ke", "wala", "wali", "wale",
    "bopp", "fibc", "ldpe", "hdpe", "lldpe", "pp", "pet", "bopet", "cpp",
    "duplex", "corrugated", "laminated", "lamination", "gloss", "matte",
    "matt", "zipper", "spout", "standup", "gusset", "center", "seal",
    "heavy", "duty", "light", "small", "medium", "large", "big", "size",
    "capacity", "weight", "filling", "sample", "custom", "standard", "normal",
    "bori", "katta", "peti", "dabba", "thaili", "mandi", "kilo", "export",
}


def _build_place_index() -> dict[str, str]:
    """Build a lowercase name -> canonical place name mapping using geonamescache."""
    gc = geonamescache.GeonamesCache()
    places: dict[str, str] = {}

    for country in gc.get_countries().values():
        name = country["name"]
        low = name.lower()
        if low not in LOCATION_STOPWORDS and len(low) >= 3:
            places[low] = name

    cities = list(gc.get_cities().values())
    cities.sort(key=lambda c: (c.get("countrycode") == "IN", c.get("population", 0)))

    for city in cities:
        name = city["name"]
        low = name.lower()
        if low not in LOCATION_STOPWORDS and len(low) >= 3:
            places[low] = name

    
    aliases = {
        "gurgaon": "Gurgaon", "gurugram": "Gurugram",
        "bangalore": "Bangalore", "bengaluru": "Bengaluru",
        "bombay": "Bombay", "baroda": "Baroda", "calcutta": "Calcutta",
        "madras": "Madras", "cochin": "Cochin", "poona": "Poona",
        "vizag": "Vizag", "banaras": "Banaras", "trivandrum": "Trivandrum",
        "pondicherry": "Pondicherry", "allahabad": "Allahabad",
        "belgaum": "Belgaum", "hubli": "Hubli", "bellary": "Bellary",
        "mysore": "Mysore", "mangalore": "Mangalore", "gauhati": "Guwahati",
        "baddi": "Baddi", "vapi": "Vapi", "silvassa": "Silvassa",
        "ankleshwar": "Ankleshwar", "morbi": "Morbi", "sanand": "Sanand",
        "halol": "Halol", "dahej": "Dahej", "peenya": "Peenya",
        "okhla": "Okhla", "bawana": "Bawana", "naraina": "Naraina",
        "kundli": "Kundli", "manesar": "Manesar", "rudrapur": "Rudrapur",
        "haridwar": "Haridwar", "pantnagar": "Pantnagar", "pithampur": "Pithampur",
        "mandideep": "Mandideep", "chakan": "Chakan", "bhosari": "Bhosari",
        "tarapur": "Tarapur", "taloja": "Taloja", "bhiwandi": "Bhiwandi",
        "vasai": "Vasai", "palghar": "Palghar", "sri city": "Sri City",
        "hosur": "Hosur", "sivakasi": "Sivakasi", "tirupur": "Tirupur",
        "uae": "UAE", "usa": "USA", "uk": "UK",
    }
    places.update(aliases)
    return places


PLACES = _build_place_index()


def parse_category(text: str) -> str | None:
    """Return one of the 7 allowed categories based on priority keyword rules."""
    low = f" {text.lower()} "

    # Treat BOPP rolls and films as film before applying the BOPP-bag rule.
    if re.search(r"\bbopp\b", low) and re.search(r"\b(?:roll|film)\b", low):
        return "film"

    # BOPP-laminated woven bags/sacks count as bopp_bag unless another film form is named.
    if "bopp" in low and not any(w in low for w in ["film", "roll", "wrap", "tape"]):
        return "bopp_bag"

    for category, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in low:
                return category

    if "bag" in low or "bags" in low:
        return "woven_sack"
    if "carton" in low or "cartons" in low:
        return "corrugated_box"
    return None

def parse_gsm(text: str) -> int | None:
    """Extract GSM value (e.g., '65 gsm', 'gsm 80', '120gsm')."""
    match = re.search(
        r"\b(?:(\d{2,4})\s*(?:gsm|g\.s\.m\.?|gram\s*per\s*sq)|(?:gsm|g\.s\.m\.?)\s*[:=-]?\s*(\d{2,4}))\b",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return int(match.group(1) or match.group(2))


def parse_micron(text: str) -> int | None:
    """Extract thickness in microns (e.g., '25 mic', '50 micron', '40 microns')."""
    match = re.search(
        r"\b(?:(\d{1,4})\s*(?:microns?|mics?|mcron|mikron|um|\u03bcm)|(?:microns?|mics?)\s*[:=-]?\s*(\d{1,4}))\b",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None
    return int(match.group(1) or match.group(2))


def _strip_traps_and_specs(text: str) -> str:
    """Remove phone numbers, fill-weight/capacity traps, and product specifications."""
    cleaned = text.lower()

    # Remove numbers immediately following phone or contact labels.
    cleaned = re.sub(
        r"\b(?:call|phone|ph|mob|mobile|whatsapp|contact)\b\s*(?:[:#]\s*)?(?:\+91[\s-]*)?(?:0[\s-]*)?\d(?:[\d -]*\d)?",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    # Remove standalone 10-digit phone numbers, including +91/0 prefixes and separators.
    cleaned = re.sub(
        r"(?<![\d+])(?:\+91[\s-]*)?(?:0[\s-]*)?(?:\d[\s-]*){9}\d(?!\d)",
        " ",
        cleaned,
    )

    # Remove GSM and micron specs.
    cleaned = re.sub(r"\b\d+(?:\.\d+)?\s*(?:gsm|g\.s\.m\.?|microns?|mics?|mcron|mikron|um|\u03bcm)\b", " ", cleaned)
    cleaned = re.sub(r"\b(?:gsm|g\.s\.m\.?|microns?|mics?)\s*[:=-]?\s*\d+(?:\.\d+)?\b", " ", cleaned)

    # Remove ply counts and loop/seal counts.
    cleaned = re.sub(r"\b\d+\s*[-]?\s*(?:ply|layer|layers|loop|loops|side\s*seal)\b", " ", cleaned)

    # Remove dimensions such as 12x18 or 10 x 12 x 15 inch.
    cleaned = re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:mm|cm|inch|in|ft|m)?\s*[x*×]\s*\d+(?:\.\d+)?(?:\s*[x*×]\s*\d+(?:\.\d+)?)?\s*(?:mm|cm|inch|inches|in|ft|m)?\b",
        " ",
        cleaned,
    )

    # Treat rating as capacity and remove weight values attached to capacity descriptors.
    cleaned = re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:kg|kgs|kilo|ton|tons|tonne|mt|ltr|liter|litre|ml|gm|g)\s*(?:capacity|cap\.?|rating|filling|fill|load|loading|swl|wala|wali|wale|size|packing)\b",
        " ",
        cleaned,
    )
    cleaned = re.sub(
        r"\b(?:capacity|cap|rating|swl|filling|load|size)\s*(?:of\s*)?[:=-]?\s*\d+(?:\.\d+)?\s*(?:kg|kgs|kilo|ton|tons|tonne|mt|ltr|gm|g)\b",
        " ",
        cleaned,
    )

    # Remove a product fill weight written as a weight plus up to two words and packing.
    cleaned = re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:kg|kgs|kilo)\s+(?:[a-z]+\s+){0,2}packing\b",
        " ",
        cleaned,
    )

    # Remove weights used to describe the contents or size of a package.
    cleaned = re.sub(
        r"\b(?:for\s+)?\d+(?:\.\d+)?\s*(?:kg|kgs|kilo|gm|g|ltr|ml)\s+(?:pp\s+|hdpe\s+|bopp\s+|woven\s+|jumbo\s+|bulk\s+|cement\s+|rice\s+|sugar\s+|atta\s+|flour\s+|fertilizer\s+|standup\s+|zipper\s+)*(?:bag|bags|sack|sacks|pouch|pouches|box|boxes|carton|cartons|bori|katta|thaili|jar|container)\b",
        " ",
        cleaned,
    )
    cleaned = re.sub(
        r"\b(?:bag|bags|sack|sacks|pouch|pouches|box|boxes|bori|katta)\s+(?:of|for)\s+\d+(?:\.\d+)?\s*(?:kg|kgs|kilo|gm|g|ltr|ml)\b",
        " ",
        cleaned,
    )
    return cleaned


def _parse_num_token(raw_num: str) -> float:
    """Convert a numeric token (digits with Indian commas or Hindi/English number word) to float."""
    token = raw_num.strip().lower().replace(",", "")
    if token in HINDI_NUM_WORDS:
        return float(HINDI_NUM_WORDS[token])
    return float(token)


def parse_quantity_and_unit(text: str, category: str | None) -> tuple[int | float | None, str | None]:
    """Extract order quantity and normalize unit to 'pcs', 'kg', or 'mt'."""
    cleaned = _strip_traps_and_specs(text)

    num_words_pattern = "|".join(sorted(HINDI_NUM_WORDS.keys(), key=len, reverse=True))
    num_pattern = rf"(?:\d[\d,]*(?:\.\d+)?|\b(?:{num_words_pattern})\b)"
    scale_keys = "|".join(sorted(SCALE_MULTIPLIERS.keys(), key=len, reverse=True))
    unit_keys = "|".join(sorted((re.escape(k) for k in UNIT_ALIASES.keys()), key=len, reverse=True))

    pattern = re.compile(
        rf"(?P<num>{num_pattern})"
        rf"(?:\s*(?P<scale>{scale_keys})\b)?"
        rf"(?:\s*(?P<unit>{unit_keys})\b)?",
        re.IGNORECASE,
    )

    candidates = []
    for m in pattern.finditer(cleaned):
        raw_num = m.group("num")
        scale = (m.group("scale") or "").lower()
        raw_unit = (m.group("unit") or "").lower()

        if raw_num.lower() in HINDI_NUM_WORDS and not scale and not raw_unit:
            continue

        try:
            val = _parse_num_token(raw_num)
        except ValueError:
            continue

        if scale:
            val *= SCALE_MULTIPLIERS[scale]

        qty: int | float = int(round(val)) if abs(val - round(val)) < 1e-9 else round(val, 4)
        norm_unit = UNIT_ALIASES.get(raw_unit)

        score = (2 if norm_unit else 0) + (2 if scale else 0) + (1 if val >= 50 else 0)
        if score > 0 or val >= 10:
            candidates.append((score, qty, norm_unit))

    if not candidates:
        return None, None

    # Prefer piece counts on bag, sack, box, pouch, and carton orders when scores tie.
    count_categories = {"fibc", "bopp_bag", "mono_carton", "corrugated_box", "pouch", "woven_sack"}
    prefer_count = category in count_categories
    candidates.sort(
        key=lambda x: (x[0], prefer_count and x[2] == "pcs"),
        reverse=True,
    )
    _, best_qty, best_unit = candidates[0]

    if best_unit is None:
        best_unit = "kg" if category == "film" and best_qty < 5000 else "pcs"

    return best_qty, best_unit

def parse_location(text: str) -> str | None:
    """Find a delivery city or fall back to capitalised location-like words."""
    # Exclude contact terms themselves and skip only the immediate word after via/on.
    word_matches = list(re.finditer(r"[A-Za-z]+", text))
    if not word_matches:
        return None

    words = [m.group() for m in word_matches]
    low_words = [w.lower() for w in words]
    n = len(words)

    contact_words = {
        "call", "phone", "ph", "mob", "mobile", "whatsapp", "contact",
        "email", "mail", "sms", "telegram", "fax", "sir", "madam",
        "dear", "bhai", "gidc", "midc",
    }
    fallback_stopwords = {
        "ji", "via", "on", "hello", "hi", "please", "kindly", "thanks",
        "thank", "regards", "team", "factory", "plant", "office",
        "industrial", "estate", "area", "godown", "warehouse",
    }
    excluded = (
        LOCATION_STOPWORDS
        | set(HINDI_NUM_WORDS)
        | set(SCALE_MULTIPLIERS)
        | contact_words
        | fallback_stopwords
    )
    preps = {
        "in", "to", "at", "from", "near", "delivery", "dispatch",
        "require", "location", "for", "mein", "me",
    }

    # Track the exact word after via/on without blocking words after contact labels or numbers.
    tokens = list(re.finditer(r"[A-Za-z]+|\d+", text))
    word_index = {match.start(): i for i, match in enumerate(word_matches)}
    skipped_indices = set()
    for i, token in enumerate(tokens[:-1]):
        if token.group().lower() in {"via", "on"}:
            next_token = tokens[i + 1]
            if next_token.start() in word_index:
                skipped_indices.add(word_index[next_token.start()])

    # Check exact place names while excluding contact words and the skipped via/on word.
    for i, word in enumerate(low_words):
        if word in preps:
            for span in (3, 2, 1):
                start = i + 1
                end = start + span
                if end <= n and start not in skipped_indices:
                    phrase_words = low_words[start:end]
                    if any(part in excluded for part in phrase_words):
                        continue
                    phrase = " ".join(phrase_words)
                    if phrase in PLACES:
                        return PLACES[phrase]

    # Keep the general place lookup but reject contact terms and skipped words.
    matches = []
    for span in (3, 2, 1):
        for i in range(n - span + 1):
            phrase_words = low_words[i:i + span]
            if i in skipped_indices or any(part in excluded for part in phrase_words):
                continue
            phrase = " ".join(phrase_words)
            if phrase in PLACES:
                is_capitalized = words[i][0].isupper()
                matches.append((span, is_capitalized, i, PLACES[phrase]))

    if matches:
        matches.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
        return matches[0][3]

    # Exclude measurement units before applying the capitalised-word fallback.
    unit_words = {
        part.lower()
        for unit in UNIT_ALIASES
        for part in re.findall(r"[A-Za-z]+", unit)
    }
    unit_words.update({
        "gsm", "mic", "micron", "microns", "mics", "mcron", "mikron",
        "um", "inch", "inches", "mm", "cm", "ft", "meter", "meters",
        "ltr", "liter", "litre", "ml", "gm", "g",
    })
    excluded |= unit_words

    # Return the last capitalised word unless it is excluded or immediately follows via/on.
    for i in range(n - 1, -1, -1):
        if words[i][0].isupper() and low_words[i] not in excluded and i not in skipped_indices:
            return words[i]

    return None


def parse_rfq(text: str) -> dict:
    """Parse an unstructured B2B packaging RFQ message into 6 structured fields."""
    if not text or not text.strip():
        return {
            "category": None,
            "quantity": None,
            "unit": None,
            "gsm": None,
            "micron": None,
            "location": None,
        }

    category = parse_category(text)
    gsm = parse_gsm(text)
    micron = parse_micron(text)
    quantity, unit = parse_quantity_and_unit(text, category)
    location = parse_location(text)

    return {
        "category": category,
        "quantity": quantity,
        "unit": unit,
        "gsm": gsm,
        "micron": micron,
        "location": location,
    }