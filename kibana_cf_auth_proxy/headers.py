def list_to_ext_header(strings):
    """
    turns a list of strings into a string suitable for a header
    """

    # opensearch expects the header to be a comma-delimited list of strings,
    # each string quoted
    quoted = [f'"{string}"' for string in strings]
    header = ", ".join(quoted)
    return header
