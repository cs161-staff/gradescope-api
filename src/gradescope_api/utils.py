def get_url_id(url: str, kind: str) -> str:
    return url.split(f"/{kind}/")[1].split("/")[0]
