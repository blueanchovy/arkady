import os, argparse, re, time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from arkady.prompts import system_prompt_v3
from arkady.functions.genai.call_function import available_functions, call_function

load_dotenv()

SUPPORTED_PROVIDERS = ["google"]


def run_agent(client, messages, working_dir, verbose=False):
    max_iterations = 20
    iteration = 0

    while iteration < max_iterations:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions],
                    system_instruction=system_prompt_v3,
                    temperature=0,
                ),
            )
        except Exception as e:
            if "429" in str(e):
                match = re.search(r'retryDelay.*?(\d+)s', str(e))
                wait = int(match.group(1)) + 5 if match else 60
                print(f"Rate limit hit, waiting {wait} seconds...")
                time.sleep(wait)
                continue
            raise
        iteration += 1

        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)

        if response.usage_metadata is None:
            raise RuntimeError("Could not find usage metadata in response.")

        if verbose:
            print(f"[tokens] prompt={response.usage_metadata.prompt_token_count} response={response.usage_metadata.candidates_token_count}")

        if response.function_calls is not None:
            function_results = []
            for function_call in response.function_calls:
                print(f"  > {function_call.name}({function_call.args})")
                result = call_function(function_call, working_dir=working_dir)

                if not result.parts or result.parts[0].function_response is None:
                    raise RuntimeError(f"Invalid response from function {function_call.name}")

                function_results.append(result.parts[0])
                if verbose:
                    print(f"    {result.parts[0].function_response.response}")

            messages.append(types.Content(role="user", parts=function_results))
        else:
            print(f"\nArkady: {response.text}")
            return

    print(f"[Arkady hit the {max_iterations}-iteration limit without a final answer.]")


def main():
    parser = argparse.ArgumentParser(description="Arkady - AI coding agent")
    parser.add_argument("--provider", type=str, default="google", choices=SUPPORTED_PROVIDERS, help="LLM provider (default: google)")
    parser.add_argument("--api-key", type=str, help="API key for the provider (overrides env var)")
    parser.add_argument("--verbose", action="store_true", help="Print token usage and function results")
    args = parser.parse_args()

    resolved_api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_api_key:
        raise RuntimeError("No API key provided. Pass --api-key or set GEMINI_API_KEY in your .env file.")

    working_dir = os.getcwd()
    print(f"Arkady wants to access:\n  {working_dir}\n")
    permission = input("Allow? [y/N]: ").strip().lower()
    if permission != "y":
        print("Permission denied. Exiting.")
        return

    client = genai.Client(api_key=resolved_api_key)

    print("\nArkady is ready. Type your request, or 'exit' to quit.\n")

    messages = []

    while True:
        try:
            user_input = input("you: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Exiting.")
            break

        messages.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
        run_agent(client, messages, working_dir, verbose=args.verbose)
