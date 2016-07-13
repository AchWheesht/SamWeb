def list_to_option_string(option_list):
    """Takes a list with tuple elements and returns a string to be used in an html document.
    The format is (option_text, option_value)"""
    string = ""
    for item in option_list:
        name = item[0]
        ident = item[1]
        string +=('<option value="%s">%s</option>' % (ident, name))
    return string
