def check_required_params(vars_dict: dict):
    for key, val in vars_dict.items():
        if not val:
            raise ValueError(f"'{key}' is not set")
