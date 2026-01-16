from search_and_scrape import scraped_content
import time
import asyncio

import aiohttp


#Web scrapper
async def scraped_content(link):
    async with aiohttp.ClientSession() as session:
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


async def main():
    link = ["https://realpython.com/python-concurrency/#speeding-up-an-io-bound-program", "https://realpython.com/python-concurrency/#speeding-up-an-io-bound-program"]

    for id, url in enumerate(link):
        start_time = time.perf_counter()
        
        content = scraped_content(url)
        time.sleep(5)

        duration = time.perf_counter() - start_time

        print(f"✅------The scraped content of the {id} : {content[0]}\n The title {content[1]}")

    print(f"It took {duration} time")
