def omit_none(dct: dict) -> dict:
    return {key: value for key, value in dct.items() if value is not None}
