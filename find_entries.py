import docx
import re

doc = docx.Document('dict.docx')
lines = [p.text for p in doc.paragraphs]

print(f"Total paragraphs: {len(lines)}")

# Find the entry with lemma "аб"
found = False
for i, line in enumerate(lines):
    if line.startswith("АБ") and "," in line:
        print(f"Found 'АБ' entry at paragraph {i+1}:")
        print(f"Line: {line[:200]}")
        found = True
        break

if not found:
    print("Could not find the exact 'АБ' entry")
    
# Print context around the found entry
if found:
    start_index = max(0, i - 5)
    end_index = min(i + 15, len(lines))
    print("\nContext around 'АБ' entry:")
    for j in range(start_index, end_index):
        print(f"Line {j+1}: {lines[j][:100]}")
    
    # Look for more entries after "аб"
    print("\nNext 10 entries after 'АБ':")
    count = 0
    for j in range(i + 1, len(lines)):
        if re.match(r'^[А-ЯЁ]', lines[j]) and "," in lines[j]:
            print(f"Entry {count+1}: {lines[j][:150]}")
            count += 1
            if count >= 10:
                break

# Pattern to match dictionary entries like "БА̄Х-И́(Й) III (мн. дахи), -и, -ул, -узиб, -и"
entry_pattern = re.compile(r'^[А-ЯЁ].*?[\s,]')

# Print a few example entries
print("\nSample entries:")
count = 0
sample_lines = []
for i in range(i, min(i + 500, len(lines))):
    if lines[i] and re.match(entry_pattern, lines[i]) and "," in lines[i] and ";" in lines[i]:
        sample_lines.append(f"Entry {count+1}: {lines[i][:200]}")
        count += 1
        if count >= 10:
            break

print("\n".join(sample_lines))

# Check paragraph distribution around found entries to understand structure
if count > 0:
    start_index = i - 5
    end_index = i + 20
    print("\nContext around first entry:")
    for j in range(max(0, start_index), min(end_index, len(lines))):
        print(f"Line {j+1}: {lines[j][:100]}") 