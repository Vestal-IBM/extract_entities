# extract_entities — Ansible Filter Plugin

A robust Ansible filter plugin that extracts structured data from free-text VLAN description strings, including floor number, device type, and users flag.

> Written with the assistance of [Claude](https://www.anthropic.com) by Anthropic (Claude 4.6)

---

## Features

- Extracts **floor number** from a wide variety of formats
- Extracts **device type** (`wireless`, `voice`, `ambiguous`)
- Extracts **users flag** (true/false)
- Handles **numeric**, **ordinal**, and **cardinal** floor formats
- Handles **mixed case** and **extra whitespace**
- Handles **typos** such as missing spaces between words and numbers
- Handles **punctuation** such as commas, dashes, and parentheses
- Handles **missing or empty** descriptions gracefully

---

## Supported Floor Formats

| Format | Example |
|---|---|
| Numeric ordinal | `3rd floor`, `12th floor` |
| Plain floor number | `floor 3`, `floor 27` |
| Spelled-out ordinal | `twelfth floor`, `twenty-third floor` |
| Unhyphenated ordinal | `twenty fifth floor`, `thirty first floor` |
| Cardinal after floor | `floor twenty nine`, `floor twenty seven` |
| Cardinal before floor | `twenty nine floor` |
| Joined number | `floor12`, `floor12th`, `12thfloor` |
| Joined spelled-out | `floortwelve`, `twelfthfloor`, `fifthfloor` |
| Users prefix | `users on floor 17`, `users on twelfth floor` |

---

## Supported Device Types

| Keyword | Output |
|---|---|
| `wireless`, `wifi`, `wi-fi` | `wireless` |
| `voice`, `voip` | `voice` |
| both present | `ambiguous` |
| neither present | `null` |

---

## Installation

1. Create a `filter_plugins` directory in your Ansible project root if it does not already exist:
```bash
mkdir filter_plugins
```

2. Copy `extract_entities.py` into the `filter_plugins` directory:
```bash
cp extract_entities.py filter_plugins/
```

---

## Usage

### Playbook
```yaml
---
- name: Extract floor/device/user from dict list
  hosts: localhost
  gather_facts: no
  vars:
    input_file: "input.yaml"
    output_file: "output_{{ now().strftime('%Y%m%d%H%M') }}.json"
  tasks:
    - name: Load YAML input dictionary
      ansible.builtin.include_vars:
        file: "{{ input_file }}"
        name: load_data
    - name: Extract entities using filter plugin
      ansible.builtin.set_fact:
        extracted: "{{ load_data.input_data | extract_entities }}"
    - name: Save JSON output
      ansible.builtin.copy:
        dest: "{{ output_file }}"
        content: "{{ extracted | to_nice_json }}"
    - name: Show output
      ansible.builtin.debug:
        var: extracted
```

### Input YAML (`input.yaml`)
```yaml
input_
  - { VLAN: 731, DESCRIPTION: "floor twenty nine wireless users" }
  - { VLAN: 845, DESCRIPTION: "twelfth floor voice users" }
  - { VLAN: 502, DESCRIPTION: "3rd floor wifi users" }
  - { VLAN: 668, DESCRIPTION: "users on eighteenth floor" }
  - { VLAN: 417, DESCRIPTION: "floor 27 wi-fi users" }
```

### Output JSON
```json
[
    {
        "DESCRIPTION": "floor twenty nine wireless users",
        "device-type": "wireless",
        "floor-number": 29,
        "old_vlan": 731,
        "original-text": "floor twenty nine wireless users",
        "users": true
    },
    {
        "DESCRIPTION": "twelfth floor voice users",
        "device-type": "voice",
        "floor-number": 12,
        "old_vlan": 845,
        "original-text": "twelfth floor voice users",
        "users": true
    }
]
```

---

## Output Fields

| Field | Type | Description |
|---|---|---|
| `original-text` | string | The original description string, whitespace trimmed |
| `floor-number` | int or null | The extracted floor number |
| `device-type` | string or null | `wireless`, `voice`, `ambiguous`, or `null` |
| `users` | boolean | `true` if the word `users` appears in the description |
| `old_vlan` | int | The original VLAN number from the input |
| `DESCRIPTION` | string | The original description field passed through |

---

## Running Tests

A standalone test suite is included:

```bash
python3 -m pytest test_extract_entities.py -v
```

Or with unittest directly:

```bash
python3 test_extract_entities.py
```

Expected output:
```
Ran 22 tests in 0.013s

OK
```

---

## Project Structure

```
.
├── filter_plugins/
│   └── extract_entities.py
├── input.yaml
├── extract.yaml
├── test_extract_entities.py
└── README.md
```

---

## Requirements

- Python 3.6+
- Ansible 2.9+

---

## License

GNU General Public License v3.0
---

*Written with the assistance of Claude 4.6 by Anthropic — https://www.anthropic.com*