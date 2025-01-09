def flatten(nested_list: list) -> list:
    """将一个嵌套的列表展开为一个单一列表。"""

    return [item for sublist in nested_list for item in sublist]
