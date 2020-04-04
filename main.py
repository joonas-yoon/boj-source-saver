import time
import os
import meta

from bs4 import BeautifulSoup
from os.path import isfile, join
from random import random
from util import Chrome, get_text

SOURCE_DIR = os.path.join('sources')
source_files = [f for f in os.listdir(SOURCE_DIR) if isfile(join(SOURCE_DIR, f))]
saved_pids = set([os.path.splitext(f)[0] for f in source_files])

driver = Chrome().get_driver()
driver.implicitly_wait(3)

driver.get('https://www.acmicpc.net/login')

username = None
while not username:
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    loginbar = soup.find('', class_='loginbar').find_all('li')
    if len(loginbar) > 4:
        username = get_text(loginbar[0])
        break
    print("Waiting for login to BOJ...")
    time.sleep(5)

print("Logined!")


driver.get(f'https://www.acmicpc.net/user/{username}')
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
solved_problems = soup.find_all('span', class_='problem_number')
solved_pids = [get_text(pid) for pid in solved_problems]

for problem_id in solved_pids:
    if problem_id in saved_pids:
        print(f'Skipped Problem {problem_id} (reason: already saved)')
    
    # List of accepted submissions
    driver.get(f'https://www.acmicpc.net/status?problem_id={problem_id}&user_id={username}&result_id=4&from_mine=1')

    # Get latest submission id
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    submissions = soup.find(id='status-table').find_all('tr')
    sub_id = None
    for sub in submissions:
        sub_id = sub.get('id')
        if sub_id:
            sub_id = sub_id.replace('solution-', '')
            break

    if sub_id is None:
        continue

    # Get page of latest source
    driver.get(f'https://www.acmicpc.net/source/{sub_id}')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    source = get_text(soup.find('textarea', {'name': 'source'}))

    # Detect file extension
    language_name = get_text(soup.find('table', class_='table').find_all('tr')[1].find_all('td')[7])
    extension = meta.LANGUAGE[language_name]['ext']
    if not extension:
        print(f'[Warn] Can not detected ext of {language_name}. it saved as .txt')
        extension = 'txt'

    # Save as file
    source_file = f'{problem_id}.{extension}'
    with open(os.path.join(SOURCE_DIR, source_file), 'w') as f:
        f.write(source)
    print(f'Problem {problem_id}, Submission #{sub_id} ({language_name}) saved')

    time.sleep(random() * 5 + 1)
print(' '.join(solved_pids))


time.sleep(10)
driver.quit()
