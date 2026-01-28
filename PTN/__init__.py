from .parse import PTN


def parse(name: str, standardise: bool = True, coherent_types: bool = False) -> dict:
    return PTN().parse(name, standardise, coherent_types)
