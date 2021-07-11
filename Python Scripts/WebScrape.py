import mechanicalsoup
from mechanicalsoup import form
import re
import pandas as pd
from KeywordSearch import check

browser = mechanicalsoup.Browser()

# login
print("Logging in...")
url = "https://www.linkedin.com"
page = browser.get(url)
html = page.soup
form = html.select("form")[0]
# username
form.select("#session_key")[0]["value"] = ""
# password
form.select("#session_password")[0]["value"] = ""
home_page = browser.submit(form, page.url)
print("Logged in")

# linkedin search query
search_for = "looking for remote"

# number of pages to look for posts
result_pages = 3

search = re.sub("\s", "%20", search_for)
search_url_base = f'https://www.linkedin.com/search/results/content/?datePosted="past-24h"&keywords={search}&origin=FACETED_SEARCH'

result_links = []
print("Searching for posts...")
for i in range(1, result_pages + 1):
    print("Page:", i)
    if i == 1:
        search_page_url = search_url_base
    else:
        search_page_url = search_url_base + f"&page={i}"
    # print(search_page_url)
    search_page = browser.get(search_page_url)
    text = search_page.soup.get_text()
    while True:
        start_index = text.find('"url":"https://www.linkedin.com/feed/update/urn')
        if start_index == -1:
            break
        result_links.append(text[start_index + 7 : start_index + 175])
        text = text[start_index + 100 :]

print("Found", len(result_links), "posts")
print("Filtering posts...")
filtered_posts = []
file1 = open("file.txt", "a", encoding="utf-8")
count = 0
for link in result_links:
    count += 1
    print("Post -", count)
    post_page = browser.get(link)
    post_text = post_page.soup.get_text()
    post_search = re.search(
        'FEED_DETAIL,EMPTY,DEFAULT,false\)","relatedContent"', post_text
    ).start()
    posts = re.search('"text":".*?"', post_text[post_search:]).group()
    posts = posts[8 : len(posts) - 1]
    if check(posts):
        filtered_posts.append(link)
        file1.write(posts + "\n\n")

print("Writing to file...")
data = {"Links": filtered_posts}
df1 = pd.DataFrame(data)
df1.to_excel("output.xlsx")
print("Successful")
