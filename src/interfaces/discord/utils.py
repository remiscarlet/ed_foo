def split_comma_delimited_string(s: str) -> list[str]:
    return list(map(lambda s: s.strip(), s.split(",")))
