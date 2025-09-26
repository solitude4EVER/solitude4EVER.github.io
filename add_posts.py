import os
import json
from bs4 import BeautifulSoup
from datetime import datetime

# Function to create HTML for a post
def create_post_html(title, datetime_str, tags_str, content):
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    date_attr = dt.strftime("%Y-%m")
    formatted_date = dt.strftime("%Y-%m-%d %H:%M")
    tags = [tag.strip() for tag in tags_str.split(",")]
    tag_attrs = ",".join(tags)
    tag_display = " ".join(f"#{tag}" for tag in tags)

    return f'''
<div class="post" data-date="{date_attr}" data-tags="{tag_attrs}">
<h2>{title}</h2>
<p class="meta">
<img src="./assets/images/clock-three-svgrepo-com.svg" alt="Clock" class="clock-icon">
{formatted_date} &nbsp;&nbsp; {tag_display}</p>
<p class="preview">{content}</p>
</div>
'''

# Load existing index.html
with open("index.html", "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Get existing post titles to avoid duplication
existing_titles = {div.h2.text for div in soup.find_all("div", class_="post") if div.h2}

# Get existing tags from the side-section
existing_tags = [li.text.strip().lstrip('#') for li in soup.select('#tagList li')]

# Scan posts directory for all JSON files
posts_dir = "posts"
new_tags = set()
for filename in sorted(os.listdir(posts_dir)):
    if filename.endswith(".json"):
        filepath = os.path.join(posts_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            posts = json.load(f)
        for post in posts:
            if post["title"] not in existing_titles:
                new_post_html = create_post_html(post["title"], post["datetime"], post["tags"], post["content"])
                first_post = soup.find("div", class_="post")
                if first_post:
                    first_post.insert_before(BeautifulSoup(new_post_html, "html.parser"))
                else:
                    soup.body.insert(0, BeautifulSoup(new_post_html, "html.parser"))
                existing_titles.add(post["title"])

                # Collect new tags
                tags = post["tags"].split(",")
                for tag in tags:
                    if tag not in existing_tags:
                        new_tags.add(tag)

# Add new tags to the side-section
side_section = soup.find(class_="side-section")
if side_section:
    tag_list = soup.find("ul", {"id": "tagList"})
    for tag in sorted(new_tags):        
        new_tag = soup.new_tag("li", onclick=f"filterPosts({{tag: '{tag}'}})")
        new_tag.string = f"#{tag}"
        tag_list.append(new_tag)


# Save updated index.html
with open("index.html", "w", encoding="utf-8") as file:
    file.write(str(soup))

