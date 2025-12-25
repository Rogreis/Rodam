import glob
import os
from bs4 import BeautifulSoup

files = glob.glob(os.path.join('.', 'content', 'Doc*.html'))
print(f"Found {len(files)} files.")

if len(files) > 1:
    target = files[1] # Doc001 or Doc002
    print(f"Checking {target}...")
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        print(content[:500])
        
    soup = BeautifulSoup(content, 'lxml')
    rows = soup.find_all('tr')
    count = 0
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 2:
            div_en = cols[0].find('div')
            if div_en and div_en.get('id'):
                count += 1
                if count < 5:
                    print(f"Found ID: {div_en.get('id')}")
    print(f"Found {count} items in {target}")
