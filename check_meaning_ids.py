import csv
from collections import defaultdict

# Check for lemmas with multiple meanings
lemma_counts = defaultdict(int)
lemma_meanings = defaultdict(list)
lemma_rows = defaultdict(list)

with open('kubachi_dictionary.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        lemma = row['lemma']
        meaning_id = row['meaning_id']
        
        lemma_counts[lemma] += 1
        lemma_meanings[lemma].append(meaning_id)
        lemma_rows[lemma].append(row)

# Find lemmas with multiple entries
multiple_meanings = [(lemma, count) for lemma, count in lemma_counts.items() if count > 1]

print(f'Found {len(multiple_meanings)} lemmas with multiple meanings.')
print(f'Total entries: {sum(lemma_counts.values())}')
print(f'Unique lemmas: {len(lemma_counts)}')

print('\nExamples of lemmas with multiple meanings:')
for lemma, count in sorted(multiple_meanings, key=lambda x: x[1], reverse=True)[:10]:
    meanings = sorted(lemma_meanings[lemma], key=int)  # Sort numerically
    print(f'  {lemma}: {count} meanings, IDs: {", ".join(meanings)}')

# Check for incremented meaning IDs
correct_ids = 0
incorrect_ids = 0
incorrect_lemmas = []

for lemma, meanings in lemma_meanings.items():
    if len(meanings) > 1:
        # Check if the meaning IDs are sequential starting from 1
        expected = [str(i) for i in range(1, len(meanings) + 1)]
        
        # Sort the meanings numerically
        sorted_meanings = sorted(meanings, key=int)
        
        if sorted_meanings == expected:
            correct_ids += 1
        else:
            incorrect_ids += 1
            incorrect_lemmas.append((lemma, sorted_meanings))
            
print(f'\nLemmas with correctly incremented meaning IDs: {correct_ids}')
print(f'Lemmas with incorrectly incremented meaning IDs: {incorrect_ids}')

if incorrect_lemmas:
    print('\nLemmas with incorrect meaning IDs:')
    for lemma, meanings in sorted(incorrect_lemmas, key=lambda x: x[0])[:20]:
        print(f'  {lemma}: {", ".join(meanings)}')
        
# Check specific lemma "саба" in detail
print("\nDetailed information about 'саба' entries:")
if 'саба' in lemma_meanings:
    for row in lemma_rows['саба']:
        print(f"  id: {row['id']}, meaning_id: {row['meaning_id']}, lemma: {row['lemma']}, morphology: {row['morphology'][:50]}...")
        
# Let's look at the first few entries in the CSV
print("\nFirst few entries in the CSV:")
with open('kubachi_dictionary.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if i < 5:
            print(f"  {row['id']}, {row['meaning_id']}, {row['lemma']}, {row['morphology'][:30]}...")

# Check for the 'аккват/би' lemma
print("\nChecking the 'аккват/би' lemma:")
if 'аккват/би' in lemma_meanings:
    meanings = sorted(lemma_meanings['аккват/би'], key=int)  # Sort numerically
    print(f"Found {lemma_counts['аккват/би']} entries with meaning IDs: {', '.join(meanings)}")
    
# Let's look at the actual CSV for аккват/би
print("\nSearching CSV for 'аккват/би' entries:")
with open('kubachi_dictionary.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['lemma'] == 'аккват/би':
            print(f"  id: {row['id']}, meaning_id: {row['meaning_id']}, lemma: {row['lemma']}, morphology: {row['morphology'][:30]}...") 