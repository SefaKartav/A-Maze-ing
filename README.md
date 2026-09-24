*This project has been created as part of the 42 curriculum by sekartav.*

# call me maybe

## Description

This project turns natural language questions into structured function
calls. Given a prompt such as `"What is the sum of 2 and 3?"`, the program
does not answer `5`. Instead it produces the name of the function to call
and the arguments it needs:

```json
{
  "prompt": "What is the sum of 2 and 3?",
  "name": "fn_add_numbers",
  "parameters": {"a": 2.0, "b": 3.0}
}
```

The goal is to make a small language model (Qwen3-0.6B, 0.6 billion
parameters) produce output that is always valid JSON and always matches the
schema given in the function definitions. A model of this size is normally
unreliable at this task when it is only asked politely through a prompt.
The reliability here comes from **constrained decoding**: at every single
step of the generation, the tokens that would break the structure are
removed before the model is allowed to choose.

## Instructions

### Installation

The project uses `uv` for dependency management. The `llm_sdk` package is
included in the repository and is installed as a local editable
dependency.

```bash
make install     # or: uv sync
```

The first run downloads the Qwen3-0.6B model from Hugging Face. This takes
a few minutes and needs roughly 1.5 GB of disk space.

### Running

```bash
make run         # or: uv run python -m src
```

All three paths are optional and have defaults:

```bash
uv run python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

### Other commands

| Command            | What it does                                        |
| ------------------ | --------------------------------------------------- |
| `make install`     | Install the dependencies with `uv sync`              |
| `make run`         | Run the program with the default paths               |
| `make debug`       | Run the program under the `pdb` debugger             |
| `make clean`       | Remove `__pycache__`, `.mypy_cache` and other caches |
| `make lint`        | Run `flake8` and `mypy` with the required flags      |
| `make lint-strict` | Run `flake8` and `mypy --strict`                     |

## Algorithm explanation

### The idea

A language model generates text one token at a time. At each step it
produces a **logit** (a score) for every token in its vocabulary, and the
token with the highest score is normally chosen. Constrained decoding
inserts one extra step in the middle: before choosing, the scores of all
the tokens that would break the required structure are set to negative
infinity. The model then physically cannot pick an invalid token, no
matter what it would have preferred.

This is why the output is valid 100% of the time rather than most of the
time. Validity is not something the model is asked for, it is something
the decoder enforces.

### The pipeline

The program builds each function call in two stages.

**Stage 1 — choosing the function.** The list of allowed function names is
turned into a list of candidate strings, each wrapped in quotes, for
example `"fn_add_numbers"` and `"fn_greet"`. The prompt is sent to the
model followed by `function name: `. At every step, `get_valid_tokens_for_candidates`
walks through the whole vocabulary and keeps only the tokens that, when
appended to what has been generated so far, still form the beginning of at
least one candidate. Once a token is chosen, `filter_candidates` drops the
candidates that no longer match. The loop stops when exactly one candidate
remains and it has been fully generated.

This approach means the function is chosen **by the model**, not by keyword
matching or any other heuristic. The model expresses its preference through
the logits; the constraint only limits which options are on the table.

**Stage 2 — filling the arguments.** The parameters of the chosen function
are read from the definition file, in order. For each one, a new prompt is
built that ends with an ordinal hint, for example `second argument value: `.
The generation strategy then depends on the declared type:

- **number** — `is_valid_number_fragment` accepts digits, a single dot, and
  a minus sign in the first position only. `is_complete_number` stops the
  loop once there are digits on both sides of the dot. The result is
  converted with `float()`.
- **string** — an opening quote is placed manually, then any token is
  allowed until a closing quote appears. `is_valid_string_fragment` makes
  sure a quote can only arrive at the very end, since that quote closes the
  string.
- **boolean** — the same candidate mechanism as the function name, with
  `true` and `false` as the only two candidates.

Every loop is capped at `MAX_ITERATIONS` (100) so that a model which never
reaches a stopping condition raises a clear error instead of hanging.

### Module layout

| File           | Responsibility                                             |
| -------------- | ---------------------------------------------------------- |
| `__main__.py`  | Command line, file loading, orchestration, error handling  |
| `models.py`    | Pydantic models for the input files and the output         |
| `vocab.py`     | Loading the vocabulary and building the reverse mapping    |
| `grammar.py`   | Pure rules: which tokens are valid, when is a value done   |
| `decoding.py`  | The generation loops that talk to the model                |

## Design decisions

**Grammar rules are separated from the model.** Every function in
`grammar.py` is pure: it takes text and a vocabulary and returns token ids,
without ever touching the model. This makes the validity rules readable on
their own and testable without loading a 0.6B parameter network.

**The vocabulary is reversed once at startup.** `build_id_to_token` builds
the id-to-token dictionary a single time in `main` and passes it down. The
alternative, searching the vocabulary for each generated token, would turn
a dictionary lookup into a linear scan repeated thousands of times.

**Pydantic validates at the boundary.** The input files are validated into
`FunctionDefinition` and `PromptTest` objects the moment they are read.
Everything after that point works with typed objects, so a malformed input
file is caught immediately with a precise message rather than causing a
confusing failure deep inside the generation loop.

**Errors are converted to `RuntimeError` at the edges.** Each loading
function catches the exceptions it can expect, such as `FileNotFoundError`,
`json.JSONDecodeError`, `OSError` and `ValidationError`, and re-raises them
as a `RuntimeError` carrying a readable message. `main` then needs only a
single `except RuntimeError` to present any startup failure to the user
cleanly.

**One broken prompt does not stop the run.** `process_prompts` wraps each
prompt in its own `try`. A prompt that fails is reported on standard error
and the remaining prompts are still processed. This matters because a run
processes a whole batch and losing all of it to one bad case would be
wasteful.

**Progress goes to standard error.** Progress messages and per-prompt
failures are printed to `stderr`, never to `stdout`, so the machine
readable output stays separate from the human readable log.

## Performance analysis

**Reliability.** The structural guarantee is absolute. A number is always
parseable as a float, a string always has matching quotes, a function name
is always one of the declared names, and the resulting file is always valid
JSON. This holds by construction, not by measurement, because an invalid
token is never selectable.

**Accuracy** — meaning whether the *right* function and the *right* values
are chosen — is a separate matter and depends on the model. Constrained
decoding narrows the options to the valid ones; picking the best of those
is still the model's judgement.

**Speed.** The cost is dominated by the number of forward passes, and there
is exactly one per generated token. The validity check itself walks the
entire vocabulary at every step, which is a noticeable but much smaller
cost next to a neural network forward pass. The subject asks for all test
prompts to finish in under five minutes on standard hardware.

**Memory.** The model is loaded once in `main` and the same instance is
passed to every prompt, so the memory cost does not grow with the number of
prompts.

## Challenges faced

**Tokens are not characters.** The first instinct is to think of generation
as producing one character at a time, but a single token can be several
characters, such as `_numbers`, and tokens often carry a leading space. All
the validity rules therefore have to ask "is text-so-far plus this whole
token still acceptable?" rather than looking at one character. This is why
every rule is written as a prefix test.

**Knowing when a value is finished.** Validity and completeness are two
different questions. `12` is a valid number fragment but not a finished
number; `12.5` is both. Each type needed its own pair of functions, one
asking "can this continue?" and one asking "can this stop?".

**The quote that both opens and closes.** In a string, the `"` character
means two opposite things depending on position. The solution was to place
the opening quote manually rather than let the model generate it, and then
treat any quote the model produces as the closing one, ending the loop.

**Mapping ids back to tokens.** The vocabulary file maps tokens to ids, but
after choosing the highest-scoring logit the program has an id and needs
the token. Building the reverse dictionary once at startup solved this.

## Testing strategy

**Structural validation.** After a run, the output file is checked for the
properties the subject requires: it parses as JSON, every object has
exactly the keys `prompt`, `name` and `parameters`, every function name
appears in the definition file, and every argument type matches the
declared type.

**Error path testing.** The failure modes are exercised deliberately, since
the subject states that an unhandled crash makes the project
non-functional:

- a missing input file
- a file containing malformed JSON
- a file containing valid JSON of the wrong shape, such as an object where
  a list is expected
- an empty list of function definitions
- an unreadable output directory

Each of these must produce a readable message on `stderr` and exit code 1,
never a traceback.

**Edge cases in the prompts.** The subject asks for testing with empty
strings, large numbers, special characters, ambiguous prompts and functions
with several parameters.

**Static checks.** `make lint` runs `flake8` for style and `mypy` with the
flags required by the subject for type checking.

## Example usage

Input file `data/input/function_calling_tests.json`:

```json
[
  {"prompt": "What is the sum of 2 and 3?"},
  {"prompt": "Greet john"},
  {"prompt": "Reverse the string 'hello'"}
]
```

Run:

```bash
uv run python -m src
```

Output written to `data/output/function_calling_results.json`:

```json
[
  {
    "prompt": "What is the sum of 2 and 3?",
    "name": "fn_add_numbers",
    "parameters": {"a": 2.0, "b": 3.0}
  },
  {
    "prompt": "Greet john",
    "name": "fn_greet",
    "parameters": {"name": "john"}
  },
  {
    "prompt": "Reverse the string 'hello'",
    "name": "fn_reverse_string",
    "parameters": {"s": "hello"}
  }
]
```

With custom paths:

```bash
uv run python -m src \
  --functions_definition my_functions.json \
  --input my_prompts.json \
  --output my_results.json
```

When something goes wrong, the program explains the problem and exits with
code 1:

```
$ uv run python -m src --input missing.json
Error: File not found: missing.json
```

## Resources

### Documentation

- [Hugging Face — Text generation strategies](https://huggingface.co/docs/transformers/generation_strategies)
- [Hugging Face — Summary of the tokenizers](https://huggingface.co/docs/transformers/tokenizer_summary)
- [Qwen3 model card](https://huggingface.co/Qwen/Qwen3-0.6B)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [PEP 257 — Docstring conventions](https://peps.python.org/pep-0257/)
- [JSON specification](https://www.json.org/)

### Articles on constrained decoding

- [Efficient Guided Generation for Large Language Models](https://arxiv.org/abs/2307.09702)
  — the paper behind the `outlines` library, describing finite state machine
  guided decoding
- [Grammar based sampling in llama.cpp (GBNF)](https://github.com/ggerganov/llama.cpp/blob/master/grammars/README.md)
- [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909)
  — the BPE tokenization algorithm

### Use of AI

AI was used as a study and review aid during this project, not as a code
generator. Specifically:

- **Understanding the concepts.** Explanations of how tokenization,
  logits and constrained decoding work, before any code was written.
- **Reviewing the control flow.** Reading through the finished functions to
  point out gaps, for example a missing `try`/`except` in `main` and a
  class that was referenced without being instantiated.
- **Documentation.** Drafting the docstrings and this README from the
  existing implementation.

The implementation itself — the grammar rules, the generation loops, the
module structure and the error handling — was written and is understood by
the author.
