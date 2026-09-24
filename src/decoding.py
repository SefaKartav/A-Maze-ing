"""Constrained decoding of the function calls.

It asks the model for one token at a time and keeps only the valid ones.
"""

from typing import Any

from llm_sdk import Small_LLM_Model

from .grammar import (
    get_valid_tokens_for_candidates,
    filter_candidates,
    get_valid_tokens_for_number,
    get_valid_tokens_for_string,
    is_complete_string,
    NUMBER_STOP_TOKEN,
    decode_bpe_string,
    BYTE_DECODER
)
from .models import FunctionDefinition, FunctionCallResult

MAX_ITERATIONS = 100
ORDINAL_WORDS = ["first", "second", "third", "fourth", "fifth", "sixth"]


def generate_constrained_string(
    model: Small_LLM_Model,
    input_ids: list[int],
    candidates: list[str],
    vocab: dict[str, int],
    id_to_token: dict[int, str],
) -> str:
    """Generate one text from a fixed list of candidates.

    The model can only choose tokens that lead to one of the candidates.
    """
    generated_so_far = ""
    input_ids = input_ids.copy()
    candidates = candidates.copy()

    for _ in range(MAX_ITERATIONS):
        candidates_list = get_valid_tokens_for_candidates(
            candidates, generated_so_far, vocab
        )

        chosen_id, chosen_token = _select_next_token(
            model, input_ids, candidates_list, id_to_token
        )

        generated_so_far += chosen_token
        input_ids.append(chosen_id)
        candidates = filter_candidates(candidates, generated_so_far)

        if len(candidates) == 1 and generated_so_far == candidates[0]:
            return candidates[0]

    raise RuntimeError(
        "Maximum number of iterations reached; "
        "production could not be completed"
    )


def _select_next_token(
    model: Small_LLM_Model,
    input_ids: list[int],
    valid_token_ids: list[int],
    id_to_token: dict[int, str],
) -> tuple[int, str]:
    """Ask the model for the best token among the valid ones.

    The logits of the invalid tokens are set to minus infinity.
    """
    if not valid_token_ids:
        raise ValueError("No valid tokens left")

    valid_token_ids_set = set(valid_token_ids)
    raw_logits = model.get_logits_from_input_ids(input_ids)
    masked_raw_logits = raw_logits.copy()

    for token_id in range(len(masked_raw_logits)):
        if token_id not in valid_token_ids_set:
            masked_raw_logits[token_id] = float('-inf')

    max_id = max(masked_raw_logits)
    max_id_index = masked_raw_logits.index(max_id)
    token_str = id_to_token[max_id_index]
    return max_id_index, token_str


def generate_number(
    model: Small_LLM_Model,
    input_ids: list[int],
    vocab: dict[str, int],
    id_to_token: dict[int, str],
) -> str:
    """Generate a number token by token.

    The model itself decides where the number ends by choosing the
    stop token.
    """
    generated_so_far = ""
    input_ids = input_ids.copy()
    for _ in range(MAX_ITERATIONS):
        valid_ids = get_valid_tokens_for_number(generated_so_far, vocab)
        chosen_id, chosen_token = _select_next_token(
            model, input_ids, valid_ids, id_to_token
        )
        if chosen_token == NUMBER_STOP_TOKEN:
            return generated_so_far
        generated_so_far += chosen_token
        input_ids.append(chosen_id)

    raise RuntimeError(
        "Maximum number of iterations reached; "
        "production could not be completed"
    )


def generate_string(
    model: Small_LLM_Model,
    input_ids: list[int],
    vocab: dict[str, int],
    id_to_token: dict[int, str],
) -> str:
    """Generate a string token by token.

    It starts with an opening quote and stops at the closing quote.
    """
    input_ids = input_ids.copy()
    opening_id = vocab['"']
    opening_str = id_to_token[opening_id]
    generated_so_far = opening_str
    input_ids.append(opening_id)
    for _ in range(MAX_ITERATIONS):
        valid_ids = get_valid_tokens_for_string(generated_so_far[1:], vocab)
        chosen_id, chosen_token = _select_next_token(
            model, input_ids, valid_ids, id_to_token
        )
        generated_so_far += chosen_token
        input_ids.append(chosen_id)
        complete = is_complete_string(generated_so_far[1:])
        if complete:
            return decode_bpe_string(generated_so_far, BYTE_DECODER)

    raise RuntimeError(
        "Maximum number of iterations reached; "
        "production could not be completed"
    )


def generate_function_call(
    model: Small_LLM_Model,
    prompt: str,
    functions: list[FunctionDefinition],
    vocab: dict[str, int],
    id_to_token: dict[int, str],
) -> FunctionCallResult:
    """Build the complete function call for one prompt.

    The model first chooses the function name, then every argument value.
    """
    name_candidate = ['"' + fn.name + '"' for fn in functions]
    catalog = "Available functions:\n"
    for fn in functions:
        catalog += f"- {fn.name}: {fn.description}\n"
    name_prompt = catalog + "\n" + prompt + "\nfunction name: "
    input_ids = model.encode(name_prompt)[0].tolist()
    name_result = generate_constrained_string(
        model=model,
        input_ids=input_ids,
        candidates=name_candidate,
        vocab=vocab,
        id_to_token=id_to_token
    )
    function_name = name_result.strip('"')
    selected_functions = None

    for fn in functions:
        if fn.name == function_name:
            selected_functions = fn
            break

    if selected_functions is None:
        raise ValueError(
            f"Function '{function_name}' not found in definitions"
        )

    context: str = ""
    parameters: dict[str, Any] = {}
    for index, (param_name, param_spec) in enumerate(
        selected_functions.parameters.items()
    ):
        oridinal = ORDINAL_WORDS[index]
        param_prompt = (
            f"Function: {selected_functions.name}\n"
            f"Description: {selected_functions.description}\n"
            f"{prompt}"
            f"{context}"
            f"\n{oridinal} argument ({param_name}) value: "
        )
        param_input_ids = model.encode(param_prompt)[0].tolist()

        if param_spec.type == "number":
            raw_value = generate_number(
                model, param_input_ids, vocab, id_to_token
            )
            parameters[param_name] = float(raw_value)

        elif param_spec.type == "string":
            raw_value = generate_string(
                model, param_input_ids, vocab, id_to_token
            )
            parameters[param_name] = raw_value.strip('"')

        elif param_spec.type == "boolean":
            raw_value = generate_constrained_string(
                model, param_input_ids, ["true", "false"], vocab, id_to_token
            )
            parameters[param_name] = (raw_value == "true")

        else:
            raise ValueError(
                f"Unsupported type '{param_spec.type}' for parameter "
                f"'{param_name}' in function '{function_name}'"
            )

        context += f"\n{param_name}: {parameters[param_name]}"

    return FunctionCallResult(
        prompt=prompt,
        name=function_name,
        parameters=parameters
    )
