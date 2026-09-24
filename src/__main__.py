"""Entry point of the project.

It reads the input files, calls the model and writes the results.
"""

import argparse
import json
import os
import sys
from pydantic import ValidationError

from llm_sdk import Small_LLM_Model

from .vocab import load_vocab, build_id_to_token
from .decoding import generate_function_call
from .models import FunctionDefinition, PromptTest, FunctionCallResult

DEFAULT_FUNCTIONS_PATH = "data/input/functions_definition.json"
DEFAULT_INPUT_PATH = "data/input/function_calling_tests.json"
DEFAULT_OUTPUT_PATH = "data/output/function_calling_results.json"


def parse_args() -> argparse.Namespace:
    """Read the options given on the command line.

    Every path has a default value, so all options are optional.
    """
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("--functions_definition",
                        type=str,
                        default=DEFAULT_FUNCTIONS_PATH,
                        help="...")

    parser.add_argument("--input",
                        type=str,
                        default=DEFAULT_INPUT_PATH,
                        help="...")

    parser.add_argument("--output",
                        type=str,
                        default=DEFAULT_OUTPUT_PATH,
                        help="...")

    return parser.parse_args()


def load_json_file(path: str) -> object:
    """Read one JSON file from the disk.

    Every file error becomes a RuntimeError with a clear message.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise RuntimeError(f"File not found: {path}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON in file {path}: {e}") from e
    except OSError as e:
        raise RuntimeError(f"Error reading file {path}: {e}") from e


def load_functions(path: str) -> list[FunctionDefinition]:
    """Read and check the file with the function definitions.

    The file must contain a list, and this list cannot be empty.
    """
    payload = load_json_file(path)
    if not isinstance(payload, list):
        raise RuntimeError(
            f"Expected a list of function definitions in {path}, "
            f"got {type(payload).__name__}"
        )

    if len(payload) == 0:
        raise RuntimeError(f"No function definitions found in {path}")

    functions: list[FunctionDefinition] = []

    for item in payload:
        try:
            functions.append(FunctionDefinition.model_validate(item))
        except ValidationError as e:
            raise RuntimeError(
                f"Invalid function definition in {path}: {e}"
            ) from e

    return functions


def load_prompts(path: str) -> list[PromptTest]:
    """Read and check the file with the prompts.

    The file must contain a list of prompt objects.
    """
    payload = load_json_file(path)
    if not isinstance(payload, list):
        raise RuntimeError(
            f"Expected a list of prompt tests in {path}, "
            f"got {type(payload).__name__}"
        )

    prompts: list[PromptTest] = []

    for item in payload:
        try:
            prompts.append(PromptTest.model_validate(item))
        except ValidationError as e:
            raise RuntimeError(
                f"Invalid prompt test in {path}: {e}"
            ) from e

    return prompts


def write_results(path: str, results: list[FunctionCallResult]) -> None:
    """Write all the results into one JSON file.

    The output directory is created when it does not exist yet.
    """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    data = [result.model_dump() for result in results]

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except OSError as e:
        raise RuntimeError(f"Error writing results to {path}: {e}") from e


def process_prompts(
    model: Small_LLM_Model,
    prompts: list[PromptTest],
    functions: list[FunctionDefinition],
    vocab: dict[str, int],
    id_to_token: dict[int, str],
) -> list[FunctionCallResult]:
    """Build a function call for every prompt.

    When one prompt fails, the program prints a message and continues.
    """
    results: list[FunctionCallResult] = []
    for i, prompt_test in enumerate(prompts, start=1):
        print(
            f"[{i}/{len(prompts)}] Processing prompt: {prompt_test.prompt}",
            file=sys.stderr,
        )
        try:
            result = generate_function_call(model,
                                            prompt_test.prompt,
                                            functions,
                                            vocab,
                                            id_to_token)
            results.append(result)
        except Exception as e:
            print(
                f"Failed to process prompt {prompt_test.prompt!r}: {e}",
                file=sys.stderr,
            )

    return results


def main() -> None:
    """Run the whole program from the command line.

    It stops with an error message and the exit code 1 when something fails.
    """
    try:
        args = parse_args()
        functions = load_functions(args.functions_definition)
        prompts = load_prompts(args.input)
        try:
            model = Small_LLM_Model()
        except Exception as e:
            raise RuntimeError(f"Failed to load the model: {e}") from e
        vocab = load_vocab(model)
        id_to_token = build_id_to_token(vocab)
        results = process_prompts(model,
                                  prompts,
                                  functions,
                                  vocab,
                                  id_to_token)
        write_results(args.output, results)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
