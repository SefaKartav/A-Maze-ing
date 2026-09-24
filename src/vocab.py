"""Loading of the vocabulary of the model.

The vocabulary links every token to its id in both directions.
"""

import json
from llm_sdk import Small_LLM_Model


def load_vocab(model: Small_LLM_Model) -> dict[str, int]:
    """Read the vocabulary file of the model.

    It returns a dictionary that maps every token to its id.
    """
    path = model.get_path_to_vocab_file()

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Vocab file could not be read: {e}") from e


def build_id_to_token(token_to_id: dict[str, int]) -> dict[int, str]:
    """Turn the vocabulary around.

    It returns a dictionary that maps every id back to its token.
    """
    t_i: dict[int, str] = {}
    for key, value in token_to_id.items():
        t_i[value] = key
    return t_i
