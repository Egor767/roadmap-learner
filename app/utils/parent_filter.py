def is_single_parent_filter(filters: dict, parent: str) -> bool:
    return set(filters.keys()) == {parent}
