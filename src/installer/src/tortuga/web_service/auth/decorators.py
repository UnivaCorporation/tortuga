def authentication_required():
    """
    A decorator that specifies whether or not authentication is required.

    """
    def decorate(f):
        if not hasattr(f, '_cp_config'):
            f._cp_config = dict()
        if 'auth.required' not in f._cp_config:
            f._cp_config['auth.required'] = True
        return f

    return decorate
