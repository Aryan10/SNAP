def reddit_parser(post):
    if post["content"] == "":
        print("No content found, check if url is news article")
        print(post["url"])
        return None

    formatted = {}

    formatted["title"] = post.get("title", "Unknown")
    formatted["publication_date"] = post.get("created_utc", "Unknown")
    formatted["content"] = post.get("content", post.get("selftext", "No content found, not a news article"))

    return formatted, post