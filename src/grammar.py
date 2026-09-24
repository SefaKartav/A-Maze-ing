"""Rules that say which tokens are valid at each step.

These functions do not use the model, they only look at the text.
"""

NUMBER_STOP_TOKEN = "Ċ"


def get_valid_tokens_for_target(
        target: str,
        generated_so_far: str,
        vocab: dict[str, int]
) -> list[int]:
    """Find the tokens that can continue the target text.

    A token is valid when the text plus this token is still a start
    of the target.
    """
    id_list: list[int] = []
    for token_str, token_id in vocab.items():
        unified = generated_so_far + token_str
        if target.startswith(unified):
            id_list.append(token_id)
    return id_list


def get_valid_tokens_for_candidates(
    candidates: list[str],
    generated_so_far: str,
    vocab: dict[str, int],
) -> list[int]:
    """Find the tokens that can continue any of the candidates.

    It collects the valid tokens of every candidate and removes
    the duplicates.
    """
    ids_set: set[int] = set()
    for candidate in candidates:
        ids_for_candidates = get_valid_tokens_for_target(
            candidate, generated_so_far, vocab
        )
        ids_set.update(ids_for_candidates)
    return list(ids_set)


def filter_candidates(
    candidates: list[str],
    generated_so_far: str,
) -> list[str]:
    """Keep only the candidates that still match the generated text.

    The other candidates are dropped because they became impossible.
    """
    remaining_candidates: list[str] = []
    for candidate in candidates:
        if candidate.startswith(generated_so_far):
            remaining_candidates.append(candidate)
    return remaining_candidates


def is_valid_number_fragment(fragment: str) -> bool:
    """Check if the text can still become a valid number.

    It allows digits, one dot and a minus sign at the first place only.
    """
    if fragment == "":
        return True
    allowed = "0123456789.-"
    for index, part in enumerate(fragment):
        if part not in allowed:
            return False
        if part == "-" and index != 0:
            return False
    if fragment.count(".") > 1:
        return False
    return True


def get_valid_tokens_for_number(
    generated_so_far: str,
    vocab: dict[str, int],
) -> list[int]:
    """Find the tokens that keep the number valid.

    When the number is already finished, the stop token is added so
    that the model can decide to end it.
    """
    id_list: list[int] = []
    if is_complete_number(generated_so_far):
        stop_id = vocab.get(NUMBER_STOP_TOKEN)
        if stop_id is not None:
            id_list.append(stop_id)
    for token_str, token_id in vocab.items():
        unified = generated_so_far + token_str
        if is_valid_number_fragment(unified):
            id_list.append(token_id)
    return id_list


def is_valid_string_fragment(fragment: str) -> bool:
    """Check if the text can still become a valid string.

    A quote is only allowed at the end because it closes the string.
    """
    for index, control in enumerate(fragment):
        if control == '"':
            return index == len(fragment) - 1
    return True


def get_valid_tokens_for_string(
    generated_so_far: str,
    vocab: dict[str, int],
) -> list[int]:
    """Find the tokens that keep the string valid.

    It tests every token of the vocabulary one by one.
    """
    id_list: list[int] = []
    for token_str, token_id in vocab.items():
        unified = generated_so_far + token_str
        if is_valid_string_fragment(unified):
            id_list.append(token_id)
    return id_list


def is_complete_number(fragment: str) -> bool:
    """Check whether the fragment is a finished number.

    Integers ("345", "-5") and decimals with digits on both sides
    of the dot ("3.14", "-0.5") count as finished.
    """
    if fragment.startswith("-"):
        fragment = fragment[1:]

    if "." not in fragment:
        return fragment.isdigit()

    if fragment.count(".") > 1:
        return False

    first, second = fragment.split(".")
    return first.isdigit() and second.isdigit()


def is_complete_string(fragment: str) -> bool:
    """Check if the string is finished.

    A string is finished when the last character is a closing quote.
    """
    if len(fragment) == 0:
        return False
    return fragment[-1] == '"'


def build_byte_decoder() -> dict[str, int]:
    """Map the tokenizer's display characters back to byte values."""
    byte_values = (
        list(range(ord("!"), ord("~") + 1))
        + list(range(ord("¡"), ord("¬") + 1))
        + list(range(ord("®"), ord("ÿ") + 1))
    )
    char_codes = byte_values[:]

    offset = 0
    for byte in range(256):
        if byte not in byte_values:
            byte_values.append(byte)
            char_codes.append(256 + offset)
            offset += 1

    return {chr(code): byte for code, byte in zip(char_codes, byte_values)}


BYTE_DECODER = build_byte_decoder()


