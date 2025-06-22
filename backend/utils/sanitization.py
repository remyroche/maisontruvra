    import bleach

    def sanitize_input(data):
        """
        Sanitizes a string or a dictionary of strings using bleach.
        """
        if isinstance(data, str):
            return bleach.clean(data)
        if isinstance(data, dict):
            return {k: sanitize_input(v) for k, v in data.items()}
        # For other types, return as is.
        return data

