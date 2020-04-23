import requests
from typing import List

# Would normally store this in a .env / secrets file
API_USER_AGENT = "whieronymus@gmail.com"


def clean_title(arg: str) -> str:
    """
    Returns title replacing spaces with underscores
    """
    # Wikipedia page/article titles are case sensitive
    return "_".join([word for word in arg.split()])


def visit_page_and_get_links(title: str, link_type: str) -> List[str]:
    """
    This is our main function for calling the Wikipedia API. It
    returns a list of all page titles linked from the current
    article.

    Wikipedia link `prop` is paginated and capped at 500 results.
    If a page has more than 500 results the response will include
    a `continue` key which includes the starting point for the
    next call as a value. This funciton will continue to call
    the wiki API collecting links until there is no `continue` key
    and return a combined list of page titles from all calls for
    this particular title.
    """
    next_start = None
    first_attempt = True
    link_titles = []
    while first_attempt or next_start:
        if link_type == "links":
            titles, next_start = call_api_and_get_links(
                title=title,
                next_start=next_start
            )
        else:
            titles, next_start = call_api_and_get_backlinks(
                title=title,
                next_start=next_start
            )
        link_titles.extend(titles)
        first_attempt = False

    print(f"{title} - {len(link_titles)} {link_type}")
    return link_titles


def call_api_and_get_links(title: str,
                           next_start: str = None) -> List[str]:
    """
    This is our API call to Wikipedia, it returns a tuple where the
    first value is a list of titles retrieved and the second value
    is a str representing the starting point (if there are more
    titles to retrieve)
    """
    url = "http://en.wikipedia.org/w/api.php"

    # Wiki API requests we provide contact information when via
    # Api-User-Agent header
    # https://www.mediawiki.org/wiki/REST_API#terms_and_conditions
    headers = {"Api-User-Agent": API_USER_AGENT}

    url_params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "links",
        "pllimit": "max",
        "plcontinue": next_start,
        "plnamespace": 0  # Main/Articles only (namespace)
    }

    print(f"Calling Wiki for {title}-{next_start}-links)")
    page_resp = requests.get(
        url,
        params=url_params,
        headers=headers
    )
    page_resp.raise_for_status()

    json_resp = page_resp.json()
    num_pages = len(json_resp['query']['pages'])
    if num_pages == 0:
        raise Exception("Page does not exist")
    if num_pages > 1:
        raise Exception("Multiple pages were returned for this Title")

    # 'links' value is a dict, so we need to convert it
    # and then we get the value using next
    try:
        links = next(iter(json_resp['query']['pages'].values()))['links']
    except KeyError as e:
        links = []
        print(f"KeyError: {e} on {title}")

    # Check if result is paginated and grab next starting point
    if json_resp.get("continue"):
        next_start = json_resp['continue']['plcontinue']
    else:
        next_start = None

    link_titles = [clean_title(link['title']) for link in links]
    return link_titles, next_start


def call_api_and_get_backlinks(title: str,
                               next_start: str = None) -> List[str]:
    """
    This is our API call to Wikipedia, it returns a tuple where the
    first value is a list of titles retrieved and the second value
    is a str representing the starting point (if there are more
    titles to retrieve)
    """
    url = "http://en.wikipedia.org/w/api.php"

    # Wiki API requests we provide contact information when via
    # Api-User-Agent header
    # https://www.mediawiki.org/wiki/REST_API#terms_and_conditions
    headers = {"Api-User-Agent": API_USER_AGENT}

    url_params = {
        "action": "query",
        "format": "json",
        "bltitle": title,
        "list": "backlinks",
        "bllimit": "max",
        "blcontinue": next_start,
        "blnamespace": 0  # Main Articles only
    }

    print(f"Calling Wiki for {title}-{next_start}-backlinks")
    page_resp = requests.get(
        url,
        params=url_params,
        headers=headers
    )
    page_resp.raise_for_status()
    json_resp = page_resp.json()

    backlinks = json_resp['query']['backlinks']

    # Check if result is paginated and grab next starting point
    if json_resp.get("continue"):
        next_start = json_resp['continue']['blcontinue']
    else:
        next_start = None

    link_titles = [clean_title(bl['title']) for bl in backlinks]
    return link_titles, next_start


