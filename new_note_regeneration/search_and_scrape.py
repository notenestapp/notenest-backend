import re
import requests
from bs4 import BeautifulSoup
import os

#Building the search payload and search engine
def build_payload(google_search_api_key, search_engine_id, one_search_question, start=1, num=1, **params):
    payload = {
        "key":google_search_api_key,
        "q":one_search_question,
        "cx":search_engine_id,
        "start": start,
        "num":num
    }
    payload.update(params)
    return payload

#Searching google
def make_requests(url, payload):
    response = requests.get(url, params=payload)
    if response.status_code != 200:
        raise Exception("Request failed!")
    else:
        data = response.json()
        links = []
        for item in data.get("items", []):
            links.append(item.get("link"))
        return links
  
#Web scrapper
def scraped_content(link):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
}

    html_text = requests.get(link, headers=headers).text
    soup = BeautifulSoup(html_text, "html.parser") #Using Beautiful soup to parse the html
    content_list = ""

    # Get the <title> tag
    title_tag = soup.title
    title_tag = title_tag.get_text(strip=True)
    try:    
        if title_tag:
            content_list += f"Title: {title_tag}"

        #Go through the body elements in order
        for element in soup.body.descendants:
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
                if element is None:
                    return None
              
                h_text = element.get_text(strip=True)
                content_list += f"\n{(h_text)}"
                if content_list == None:
                    raise Exception("Couldn't scrape body content.")
                
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text:  #Avoid empty paragraphs
                    content_list += f"\n{text}"

    except Exception as e:
        print(f"Error: {e}")

    return content_list, title_tag

#A list of good sites to cross reference sites that were scraped
primary_domains = [ 
        "khanacademy.org",
        "wikipedia.org",
        "britannica.com",
        "geeksforgeeks.org",
        "tutorialspoint.com",
        "mit.edu",
        "stanford.edu",
        "nasa.gov"
    ]


secondary_domains = [
    "reddit.com",
    "quora.com",
    "medium.com",
    "stackexchange.com",
    "stackoverflow.com"
]

bad_domains = [
    "pinterest.com",
    "facebook.com",
    "tiktok.com",
    "instagram.com",
    "randomspam.xyz"
]

#New list for the sorted list of links that google CSE gave back
primary_list = [] #Main source of information.
secondary_list = [] #Might not need this. Secondary source of information to give the LLM a touch of humanness 
bad_list = []#Will not use the bad sites.

def categorize_link(domain, link):
    if domain in primary_domains:
        primary_list.append(link)
    elif domain in secondary_domains:
        secondary_list.append(link)
    elif domain in bad_domains:
        bad_list.append(link)
    else:
        primary_list.append(link) 
    return primary_list, secondary_list


def clean_scraped_text(raw_text):
    #Normalize line breaks
    raw_text = raw_text.replace("\r\n", "\n")

    # Split into individual lines
    lines = raw_text.split("\n")
    cleaned_lines = []

    # UI word patterns or errors
    ui_words = [
        "Search", "Error", "Text Size", "Font", 
        "Margin", "template", "selected",
        "This action is not available"
    ]

    # LaTeX formatting commands to skip (but keep math expressions)
    latex_trash_patterns = [
        r"\\newcommand",
        r"\\unicode",
        r"\\mathrm",
        r"\\textbf",
        r"\\vec",
        r"\\overset",
        r"\\smash",
        r"\\scriptstyle"
    ]

    # Pattern for non-English letters
    non_english_pattern = re.compile(r"[^\x00-\x7F]")

    # Helper to detect math expressions
    def contains_math(line):
        return "$" in line or "\\" in line or "{" in line or "}" in line

    # Main cleaning loop
    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Skip non-English lines
        if non_english_pattern.search(line):
            continue

        # Skip LaTeX formatting commands (but keep equations)
        if any(re.search(pattern, line) for pattern in latex_trash_patterns):
            continue

        # Skip UI / boilerplate text
        if any(word.lower() in line.lower() for word in ui_words):
            continue

        # Skip very short noise unless it is math
        if len(line) < 20 and not contains_math(line):
            continue

        cleaned_lines.append(line)

    # Join into a final cleaned string
    cleaned_text = "\n".join(cleaned_lines)
    return cleaned_text