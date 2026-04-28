import re
ORDINAL_MAP = {
    "first": 1, "second": 2, "third": 3, "fourth": 4,
    "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
    "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12,
    "thirteenth": 13, "fourteenth": 14, "fifteenth": 15,
    "sixteenth": 16, "seventeenth": 17, "eighteenth": 18,
    "nineteenth": 19, "twentieth": 20,
    "twenty-first": 21, "twenty-second": 22, "twenty-third": 23,
    "twenty-fourth": 24, "twenty-fifth": 25, "twenty-sixth": 26,
    "twenty-seventh": 27, "twenty-eighth": 28, "twenty-ninth": 29,
    "thirtieth": 30,
    "thirty-first": 31, "thirty-second": 32, "thirty-third": 33,
    "thirty-fourth": 34, "thirty-fifth": 35, "thirty-sixth": 36,
    "thirty-seventh": 37, "thirty-eighth": 38, "thirty-ninth": 39,
    "twenty first": 21, "twenty second": 22, "twenty third": 23,
    "twenty fourth": 24, "twenty fifth": 25, "twenty sixth": 26,
    "twenty seventh": 27, "twenty eighth": 28, "twenty ninth": 29,
    "thirty first": 31, "thirty second": 32, "thirty third": 33,
    "thirty fourth": 34, "thirty fifth": 35, "thirty sixth": 36,
    "thirty seventh": 37, "thirty eighth": 38, "thirty ninth": 39,
}
ONES = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19
}
TENS = {
    "twenty": 20, "thirty": 30
}
STOP_WORDS = r"(?:wireless|wifi|wi-fi|voice|voip|users)"
FLOOR_WORD = r"(?:floor|fl)"
def parse_cardinal(text):
    t = text.strip().lower().replace("-", " ")
    for tens_word, tens_val in TENS.items():
        for ones_word, ones_val in ONES.items():
            if re.search(rf"\b{tens_word}\s+{ones_word}\b", t):
                return tens_val + ones_val
    for tens_word, tens_val in TENS.items():
        if re.search(rf"\b{tens_word}\b", t):
            return tens_val
    for ones_word, ones_val in ONES.items():
        if re.search(rf"\b{ones_word}\b", t):
            return ones_val
    return None
def extract_floor(text):
    t = text.lower()
    # 1) numeric ordinal with optional space before/after "floor/fl"
    m = re.search(rf"\b(\d+)(st|nd|rd|th)\s*{FLOOR_WORD}\b", t)
    if m:
        return int(m.group(1))
    m = re.search(rf"\b{FLOOR_WORD}\s*(\d+)(st|nd|rd|th)?\b", t)
    if m:
        return int(m.group(1))
    # 2) plain "floor/fl N" with optional space
    m = re.search(rf"\b{FLOOR_WORD}\s*([0-9]+)\b", t)
    if m:
        return int(m.group(1))
    # 3) spelled-out ordinal with optional space before/after "floor/fl"
    for word in sorted(ORDINAL_MAP, key=len, reverse=True):
        if re.search(rf"\b{FLOOR_WORD}\s*{re.escape(word)}\b", t):
            return ORDINAL_MAP[word]
        if re.search(rf"\b{re.escape(word)}\s*{FLOOR_WORD}\b", t):
            return ORDINAL_MAP[word]
        if re.search(rf"\b{FLOOR_WORD}{re.escape(word)}(?:\W|$)", t):
            return ORDINAL_MAP[word]
        if re.search(rf"\b{re.escape(word)}{FLOOR_WORD}\b", t):
            return ORDINAL_MAP[word]
    # 4) joined cardinal after "floor/fl" e.g. "floortwelve" or "fltwelve"
    for word in sorted(ONES, key=len, reverse=True):
        if re.search(rf"\b{FLOOR_WORD}{re.escape(word)}(?:\W|$)", t):
            return ONES[word]
    for tens_word, tens_val in sorted(TENS.items(), key=lambda x: len(x[0]), reverse=True):
        for ones_word, ones_val in sorted(ONES.items(), key=lambda x: len(x[0]), reverse=True):
            if re.search(rf"\b{FLOOR_WORD}{re.escape(tens_word)}{re.escape(ones_word)}(?:\W|$)", t):
                return tens_val + ones_val
        if re.search(rf"\b{FLOOR_WORD}{re.escape(tens_word)}(?:\W|$)", t):
            return tens_val
    # 5) joined cardinal before "floor/fl" e.g. "twelvefloor" or "twelvefl"
    for word in sorted(ONES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(word)}{FLOOR_WORD}\b", t):
            return ONES[word]
    for tens_word, tens_val in sorted(TENS.items(), key=lambda x: len(x[0]), reverse=True):
        for ones_word, ones_val in sorted(ONES.items(), key=lambda x: len(x[0]), reverse=True):
            if re.search(rf"\b{re.escape(tens_word)}{re.escape(ones_word)}{FLOOR_WORD}\b", t):
                return tens_val + ones_val
        if re.search(rf"\b{re.escape(tens_word)}{FLOOR_WORD}\b", t):
            return tens_val
    # 6) cardinal written number after "floor/fl"
    m = re.search(rf"\b{FLOOR_WORD}\s+([\w\s-]+?)\s+{STOP_WORDS}", t)
    if m:
        candidate = m.group(1).strip()
        val = parse_cardinal(candidate)
        if val:
            return val
    # 7) cardinal written number before "floor/fl"
    m = re.search(rf"([\w\s-]+?)\s+{FLOOR_WORD}\b", t)
    if m:
        candidate = m.group(1).strip()
        val = parse_cardinal(candidate)
        if val:
            return val
    return None
def extract_device(text):
    t = text.lower()
    found = []
    if re.search(r"\b(voip|voice)\b", t):
        found.append("voice")
    if re.search(r"\b(wireless|wifi|wi-fi)\b", t):
        found.append("wireless")
    if len(found) == 2:
        return "ambiguous"
    if len(found) == 1:
        return found[0]
    return None
def extract_users(text):
    return "users" in text.lower()
def extract_entities_item(item):
    if isinstance(item, dict):
        desc = item.get("description", "")
        old_vlan = item.get("vlan", None)
        if old_vlan is not None:
            try:
                old_vlan = int(old_vlan)
            except (ValueError, TypeError):
                old_vlan = None
        base = {k: v for k, v in item.items() if k != "vlan"}
    else:
        desc = str(item)
        old_vlan = None
        base = {}
    cleaned = desc.strip().replace("_", " ").lower()
    extracted = {
        "original-text": cleaned,
        "floor-number": extract_floor(cleaned),
        "device-type": extract_device(cleaned),
        "users": extract_users(cleaned),
    }
    if old_vlan is not None:
        extracted["old_vlan"] = old_vlan
    base.update(extracted)
    return base
def extract_entities_list(data):
    return [extract_entities_item(x) for x in data]
class FilterModule(object):
    def filters(self):
        return {
            "extract_entities": extract_entities_list
        }