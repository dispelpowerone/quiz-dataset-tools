def is_ok_response(response: str) -> bool:
    clean_respone = response.strip().upper().strip("\n\t '`\"«».")
    return (
        clean_respone == "OK"
        or clean_respone.endswith(" OK")
        or clean_respone.endswith("\nOK")
    )
