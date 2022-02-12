from gradescope_api.errors import GradescopeAPIError


def get_url_id(url: str, kind: str) -> str:
    try:
        return url.split(f"/{kind}/")[1].split("/")[0]
    except Exception:
        raise GradescopeAPIError(f"Gradescope URL is not properly formatted: {url}")
