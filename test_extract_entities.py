import unittest
import re
# ---------------------------
# ORDINAL WORD MAP (expanded)
# ---------------------------
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
    m = re.search(r"\b(\d+)(st|nd|rd|th)\s*floor\b", t)
    if m:
        return int(m.group(1))
    m = re.search(r"\bfloor\s*(\d+)(st|nd|rd|th)?\b", t)
    if m:
        return int(m.group(1))
    m = re.search(r"\bfloor\s*([0-9]+)\b", t)
    if m:
        return int(m.group(1))
    for word in sorted(ORDINAL_MAP, key=len, reverse=True):
        if re.search(rf"\bfloor\s*{re.escape(word)}\b", t):
            return ORDINAL_MAP[word]
        if re.search(rf"\b{re.escape(word)}\s*floor\b", t):
            return ORDINAL_MAP[word]
        if re.search(rf"\bfloor{re.escape(word)}(?:\W|$)", t):
            return ORDINAL_MAP[word]
        if re.search(rf"\b{re.escape(word)}floor\b", t):
            return ORDINAL_MAP[word]
    for word in sorted(ONES, key=len, reverse=True):
        if re.search(rf"\bfloor{re.escape(word)}(?:\W|$)", t):
            return ONES[word]
    for tens_word, tens_val in sorted(TENS.items(), key=lambda x: len(x[0]), reverse=True):
        for ones_word, ones_val in sorted(ONES.items(), key=lambda x: len(x[0]), reverse=True):
            if re.search(rf"\bfloor{re.escape(tens_word)}{re.escape(ones_word)}(?:\W|$)", t):
                return tens_val + ones_val
        if re.search(rf"\bfloor{re.escape(tens_word)}(?:\W|$)", t):
            return tens_val
    for word in sorted(ONES, key=len, reverse=True):
        if re.search(rf"\b{re.escape(word)}floor\b", t):
            return ONES[word]
    for tens_word, tens_val in sorted(TENS.items(), key=lambda x: len(x[0]), reverse=True):
        for ones_word, ones_val in sorted(ONES.items(), key=lambda x: len(x[0]), reverse=True):
            if re.search(rf"\b{re.escape(tens_word)}{re.escape(ones_word)}floor\b", t):
                return tens_val + ones_val
        if re.search(rf"\b{re.escape(tens_word)}floor\b", t):
            return tens_val
    m = re.search(rf"\bfloor\s+([\w\s-]+?)\s+{STOP_WORDS}", t)
    if m:
        candidate = m.group(1).strip()
        val = parse_cardinal(candidate)
        if val:
            return val
    m = re.search(r"([\w\s-]+?)\s+floor\b", t)
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
        desc = item.get("DESCRIPTION", "")
        old_vlan = item.get("VLAN", None)
        base = {k: v for k, v in item.items() if k != "VLAN"}
    else:
        desc = str(item)
        old_vlan = None
        base = {}
    cleaned = desc.strip()
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
class TestExtractFloor(unittest.TestCase):
    def test_numeric_ordinal(self):
        self.assertEqual(extract_floor("3rd floor wifi users"), 3)
        self.assertEqual(extract_floor("12th floor voice users"), 12)
        self.assertEqual(extract_floor("1st floor wireless users"), 1)
        self.assertEqual(extract_floor("2nd floor voip users"), 2)
    def test_plain_floor_number(self):
        self.assertEqual(extract_floor("floor 3 wifi users"), 3)
        self.assertEqual(extract_floor("floor 27 wireless users"), 27)
        self.assertEqual(extract_floor("users on floor 17"), 17)
        self.assertEqual(extract_floor("floor 0 wireless users"), 0)
        self.assertEqual(extract_floor("floor 31 voice users"), 31)
    def test_spelled_out_ordinal(self):
        self.assertEqual(extract_floor("twelfth floor voice users"), 12)
        self.assertEqual(extract_floor("twenty-third floor wifi users"), 23)
        self.assertEqual(extract_floor("thirtieth floor voip users"), 30)
        self.assertEqual(extract_floor("users on eighteenth floor"), 18)
    def test_unhyphenated_ordinal(self):
        self.assertEqual(extract_floor("twenty fifth floor wireless users"), 25)
        self.assertEqual(extract_floor("thirty first floor wifi users"), 31)
        self.assertEqual(extract_floor("twenty third floor voice users"), 23)
    def test_cardinal_after_floor(self):
        self.assertEqual(extract_floor("floor twenty nine wireless users"), 29)
        self.assertEqual(extract_floor("floor twenty seven wi-fi users"), 27)
        self.assertEqual(extract_floor("floor thirty wireless users"), 30)
    def test_cardinal_before_floor(self):
        self.assertEqual(extract_floor("twenty nine floor wireless users"), 29)
    def test_mixed_case(self):
        self.assertEqual(extract_floor("THIRD FLOOR WIRELESS USERS"), 3)
        self.assertEqual(extract_floor("Floor 14 VOIP Users"), 14)
        self.assertEqual(extract_floor("Users On TWENTY-FIRST Floor Voice"), 21)
    def test_extra_whitespace(self):
        self.assertEqual(extract_floor("  floor   7   wifi   users  "), 7)
        self.assertEqual(extract_floor("twelfth   floor   voice   users"), 12)
    def test_typos_missing_space(self):
        self.assertEqual(extract_floor("floor12 wi-fi users"), 12)
        self.assertEqual(extract_floor("floor12th wi-fi users"), 12)
        self.assertEqual(extract_floor("12thfloor wi-fi users"), 12)
        self.assertEqual(extract_floor("floortwelve wi-fi users"), 12)
        self.assertEqual(extract_floor("twelfthfloor wi-fi users"), 12)
    def test_no_floor(self):
        self.assertIsNone(extract_floor("wireless users"))
        self.assertIsNone(extract_floor("voip users"))
        self.assertIsNone(extract_floor(""))
        self.assertIsNone(extract_floor("no floor or device info here"))
    def test_punctuation(self):
        self.assertEqual(extract_floor("floor 4, wireless users"), 4)
        self.assertEqual(extract_floor("floor 11 - voice users"), 11)
        self.assertEqual(extract_floor("floor 18 (wifi) users"), 18)
class TestExtractDevice(unittest.TestCase):
    def test_voice(self):
        self.assertEqual(extract_device("floor 3 voice users"), "voice")
        self.assertEqual(extract_device("floor 3 voip users"), "voice")
        self.assertEqual(extract_device("VOIP users"), "voice")
    def test_wireless(self):
        self.assertEqual(extract_device("floor 3 wireless users"), "wireless")
        self.assertEqual(extract_device("floor 3 wifi users"), "wireless")
        self.assertEqual(extract_device("floor 3 wi-fi users"), "wireless")
        self.assertEqual(extract_device("WIRELESS users"), "wireless")
    def test_ambiguous(self):
        self.assertEqual(extract_device("floor 10 wireless voip users"), "ambiguous")
        self.assertEqual(extract_device("floor 12 voice wifi users"), "ambiguous")
    def test_no_device(self):
        self.assertIsNone(extract_device("floor 5 users"))
        self.assertIsNone(extract_device("third floor users"))
        self.assertIsNone(extract_device(""))
class TestExtractUsers(unittest.TestCase):
    def test_users_present(self):
        self.assertTrue(extract_users("floor 3 wireless users"))
        self.assertTrue(extract_users("USERS on floor 3"))
    def test_users_absent(self):
        self.assertFalse(extract_users("floor 9 wireless"))
        self.assertFalse(extract_users("sixth floor voice"))
        self.assertFalse(extract_users(""))
class TestExtractEntitiesItem(unittest.TestCase):
    def test_full_item(self):
        item = {"VLAN": 731, "DESCRIPTION": "floor twenty nine wireless users"}
        result = extract_entities_item(item)
        self.assertEqual(result["floor-number"], 29)
        self.assertEqual(result["device-type"], "wireless")
        self.assertTrue(result["users"])
        self.assertEqual(result["old_vlan"], 731)
    def test_missing_description(self):
        item = {"VLAN": 4}
        result = extract_entities_item(item)
        self.assertIsNone(result["floor-number"])
        self.assertIsNone(result["device-type"])
        self.assertFalse(result["users"])
    def test_empty_description(self):
        item = {"VLAN": 1, "DESCRIPTION": ""}
        result = extract_entities_item(item)
        self.assertIsNone(result["floor-number"])
        self.assertIsNone(result["device-type"])
        self.assertFalse(result["users"])
    def test_whitespace_description(self):
        item = {"VLAN": 2, "DESCRIPTION": "   "}
        result = extract_entities_item(item)
        self.assertIsNone(result["floor-number"])
        self.assertIsNone(result["device-type"])
        self.assertFalse(result["users"])
        self.assertEqual(result["original-text"], "")
    def test_string_item(self):
        result = extract_entities_item("floor 5 wireless users")
        self.assertEqual(result["floor-number"], 5)
        self.assertEqual(result["device-type"], "wireless")
        self.assertTrue(result["users"])
if __name__ == "__main__":
    unittest.main(verbosity=2)