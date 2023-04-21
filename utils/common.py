
def get_AND_elements(list_a, list_b :list)->list:

    and_elements = set(list_a) & set(list_b)
    return list(and_elements)