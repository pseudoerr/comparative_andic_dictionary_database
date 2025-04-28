import re
import csv
import docx
from typing import List, Dict, Any
from collections import defaultdict

def extract_dictionary_entries(file_path: str) -> List[str]:
    """Extract dictionary entries from a Word document."""
    doc = docx.Document(file_path)
    lines = [p.text for p in doc.paragraphs]
    
    # Find where the actual dictionary entries start
    # Based on our analysis, the first entry is "АБ // АБДИКIНЕ"
    start_index = 0
    for i, line in enumerate(lines):
        if line.startswith("АБ //") or line.startswith("АБ//"):
            start_index = i
            break
    
    print(f"Starting extraction from line {start_index+1}")
    
    entries = []
    current_entry = ""
    
    # Process the document from the identified starting point
    for i, line in enumerate(lines[start_index:], start=start_index):
        # If line starts with uppercase Cyrillic letter, it might be a new entry
        if re.match(r'^[А-ЯЁ]', line) and (',' in line):
            # Skip any explanatory lines that might match our pattern
            if any(marker in line for marker in ["Слова, начинающиеся с", "Омонимы даются"]):
                continue
                
            # If we have a previous entry, save it
            if current_entry:
                entries.append(current_entry)
            current_entry = line
        elif current_entry and not re.match(r'^\d+\.', line):  # Skip lines that start with numbering (explanatory text)
            # Continue with the current entry
            current_entry += " " + line
    
    # Add the last entry
    if current_entry:
        entries.append(current_entry)
    
    # Clean entries to remove explanatory sections
    cleaned_entries = []
    for entry in entries:
        # If the entry contains explanatory text markers, cut it off
        markers = ["У многозначного слова", "В словарь в качестве", "Что касается слов-синонимов", 
                   "Слова, различающиеся", "Слова, начинающиеся", "Омонимы даются"]
        
        for marker in markers:
            if marker in entry:
                entry = entry.split(marker)[0]
        
        cleaned_entries.append(entry)
    
    return cleaned_entries

def parse_entry(entry: str) -> Dict[str, Any]:
    """Parse a dictionary entry into its components."""
    # For entries with alternative forms (indicated by //)
    if "//" in entry and entry.index("//") < 20:
        lemma_parts = entry.split("//", 1)
        lemma = lemma_parts[0].strip()
        # If there's more text after //, update entry to include it for further parsing
        if lemma_parts[1].strip():
            # Extract the alternative form (everything up to first comma after //)
            alt_form_match = re.match(r'([^,]+)', lemma_parts[1].strip())
            if alt_form_match:
                lemma += " // " + alt_form_match.group(1).strip()
            entry = lemma_parts[1].strip()
    else:
        # Extract lemma and meaning ID
        lemma_match = re.match(r'^([А-ЯЁ][А-ЯЁ/\-\s]+)(\d*)', entry)
        lemma = ""
        if lemma_match:
            lemma = lemma_match.group(1).strip()
        
    # Detect meaning ID (either in the form of superscript number or after lemma)
    meaning_id = "1"  # Default meaning ID
    meaning_match = re.search(r'(\d+)(?:\s|$)', lemma)
    if meaning_match:
        meaning_id = meaning_match.group(1)
        lemma = re.sub(r'\d+(?:\s|$)', '', lemma).strip()
    
    # Extract morphological information
    morph_info = ""
    morph_match = re.search(r',(.*?);', entry)
    if morph_match:
        morph_info = morph_match.group(1).strip()
    
    # Extract definition
    definition = ""
    definition_match = re.search(r';(.*?)(?:$)', entry, re.DOTALL)
    if definition_match:
        definition = definition_match.group(1).strip()
    
    # Create IPA transcription
    ipa = create_ipa_transcription(lemma.lower())
    
    return {
        "lemma": lemma.lower(),
        "meaning_id": meaning_id,
        "morphology": morph_info,
        "ipa": ipa,
        "definition": definition
    }

def create_ipa_transcription(term: str) -> str:
    """
    Create an IPA transcription from the Kubachi term.
    This is a simplified mapping and should be replaced with actual Kubachi to IPA rules.
    """
    # Basic mapping of Cyrillic to IPA
    ipa_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'jo',
        'ж': 'ʒ', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'x', 'ц': 'ts', 'ч': 'tʃ', 'ш': 'ʃ', 'щ': 'ʃtʃ', 'ъ': 'ʔ',
        'ы': 'ɨ', 'ь': 'ʲ', 'э': 'e', 'ю': 'ju', 'я': 'ja', '/': '/',
        'гІ': 'ɢ', 'гъ': 'ʁ', 'гь': 'h', 'хъ': 'q', 'хь': 'x', 'кь': 'ƛ', 'кІ': 'kʼ',
        'пІ': 'pʼ', 'тІ': 'tʼ', 'цІ': 'tsʼ', 'чІ': 'tʃʼ', 'къ': 'qʼ'
    }
    
    # Handle Kubachi-specific character combinations first
    term = re.sub(r'гІ', 'ɢ', term.lower())
    term = re.sub(r'гъ', 'ʁ', term)
    term = re.sub(r'гь', 'h', term)
    term = re.sub(r'хъ', 'q', term)
    term = re.sub(r'хь', 'x', term)
    term = re.sub(r'кь', 'ƛ', term)
    term = re.sub(r'кІ', 'kʼ', term)
    term = re.sub(r'пІ', 'pʼ', term)
    term = re.sub(r'тІ', 'tʼ', term)
    term = re.sub(r'цІ', 'tsʼ', term)
    term = re.sub(r'чІ', 'tʃʼ', term)
    term = re.sub(r'къ', 'qʼ', term)
    
    # Handle special characters and diacritics
    term = term.replace('̄', 'ː')  # Convert macron to IPA long vowel
    term = term.replace('́', 'ˈ')  # Convert acute accent to IPA primary stress
    
    ipa = ""
    for char in term.lower():
        if char in ipa_map:
            ipa += ipa_map[char]
        elif char in ['-', ' ', '(', ')', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            ipa += char
        else:
            ipa += char  # Keep any unmapped characters
    
    return ipa

def main():
    # Extract dictionary entries from the Word document
    entries = extract_dictionary_entries("dict.docx")
    
    print(f"Found {len(entries)} dictionary entries")
    
    # Parse each entry
    parsed_entries = []
    entry_id = 1
    
    # First pass: Parse all entries
    for entry in entries:
        parsed_entry = parse_entry(entry)
        if parsed_entry["lemma"] and len(parsed_entry["lemma"]) > 1:  # Only include entries with a valid lemma
            parsed_entry["id"] = entry_id
            parsed_entries.append(parsed_entry)
            entry_id += 1
    
    # Second pass: Assign correct meaning_id values
    # Group entries by lemma
    lemma_to_entries = defaultdict(list)
    for entry in parsed_entries:
        normalized_lemma = re.sub(r'\s+//.*', '', entry["lemma"])
        lemma_to_entries[normalized_lemma].append(entry)
    
    # Assign sequential meaning_ids for each lemma
    for lemma, entries_list in lemma_to_entries.items():
        # Sort by the original meaning_id (if it matters for ordering)
        entries_list.sort(key=lambda e: int(e["meaning_id"]))
        
        # Special case for the problematic entry "саба"
        if lemma == 'саба':
            # For саба entries, manually assign IDs based on the morphology field
            for entry in entries_list:
                if 'саяти' in entry["morphology"]:
                    entry["meaning_id"] = "1"
                elif '-аддил, -алла' in entry["morphology"]:
                    entry["meaning_id"] = "2"
        else:
            # Regular case: assign sequential meaning_ids starting from 1
            for i, entry in enumerate(entries_list, 1):
                entry["meaning_id"] = str(i)
    
    # Write to CSV
    with open("kubachi_dictionary.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["id", "meaning_id", "lemma", "morphology", "ipa", "definition"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Write entries sorted by id
        for entry in sorted(parsed_entries, key=lambda e: int(e["id"])):
            writer.writerow({
                "id": entry["id"],
                "meaning_id": entry["meaning_id"],
                "lemma": entry["lemma"],
                "morphology": entry["morphology"],
                "ipa": entry["ipa"],
                "definition": entry["definition"]
            })
    
    print(f"Processed {len(parsed_entries)} entries. Output saved to kubachi_dictionary.csv")
    
    # Print a few examples for verification
    if parsed_entries:
        print("\nExample entries:")
        for i in range(min(5, len(parsed_entries))):
            print(f"Entry {i+1}:")
            for key, value in parsed_entries[i].items():
                if key == "id" or key == "meaning_id":
                    print(f"  {key}: {value}")
                else:
                    print(f"  {key}: {str(value)[:100]}" + ("..." if len(str(value)) > 100 else ""))

if __name__ == "__main__":
    main() 