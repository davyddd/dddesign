def convert_camel_case_to_snake_case(string: str) -> str:
    return ''.join(f'_{char.lower()}' if char.isupper() else char for char in string).lstrip('_')
