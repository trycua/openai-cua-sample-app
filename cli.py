import argparse
from agent.agent import Agent
from computers import (
    BrowserbaseBrowser,
    ScrapybaraBrowser,
    ScrapybaraUbuntu,
    LocalPlaywrightComputer,
    DockerComputer,
    CuaMacOSComputer,
)

def acknowledge_safety_check_callback(message: str) -> bool:
    response = input(
        f"Safety Check Warning: {message}\nDo you want to acknowledge and proceed? (y/n): "
    ).lower()
    return response.lower().strip() == "y"


def main():
    parser = argparse.ArgumentParser(
        description="Select a computer environment from the available options."
    )
    parser.add_argument(
        "--computer",
        choices=[
            "local-playwright",
            "docker",
            "browserbase",
            "scrapybara-browser",
            "scrapybara-ubuntu",
            "cua-macos",
        ],
        help="Choose the computer environment to use.",
        default="local-playwright",
    )
    parser.add_argument(
        "--input",
        type=str,
        help="Initial input to use instead of asking the user.",
        default=None,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode for detailed output.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show images during the execution.",
    )
    parser.add_argument(
        "--start-url",
        type=str,
        help="Start the browsing session with a specific URL (only for browser environments).",
        default="https://bing.com",
    )
    # Add cua-specific arguments
    parser.add_argument(
        "--display",
        type=str,
        help="Display resolution for VM (e.g., 1024x768)",
        default="1024x768",
    )
    parser.add_argument(
        "--memory",
        type=str,
        help="Memory allocation for VM (e.g., 4GB)",
        default="4GB",
    )
    parser.add_argument(
        "--cpu",
        type=str,
        help="CPU cores for VM",
        default="2",
    )
    args = parser.parse_args()

    computer_mapping = {
        "local-playwright": LocalPlaywrightComputer,
        "docker": DockerComputer,
        "browserbase": BrowserbaseBrowser,
        "scrapybara-browser": ScrapybaraBrowser,
        "scrapybara-ubuntu": ScrapybaraUbuntu,
        "cua-macos": CuaMacOSComputer,
    }

    ComputerClass = computer_mapping[args.computer]

    if args.computer == "cua-macos":
        computer = ComputerClass(
            display=args.display,
            memory=args.memory,
            cpu=args.cpu,
        )
    else:
        computer = ComputerClass()

    with computer:
        agent = Agent(
            computer=computer,
            acknowledge_safety_check_callback=acknowledge_safety_check_callback,
        )
        items = []


        if args.computer in ["browserbase", "local-playwright"]:
            if not args.start_url.startswith("http"):
                args.start_url = "https://" + args.start_url
            agent.computer.goto(args.start_url)

        while True:
            try:
                user_input = args.input or input("> ")
                if user_input == 'exit':
                    break
            except EOFError as e:
                print(f"An error occurred: {e}")
                break
            items.append({"role": "user", "content": user_input})
            output_items = agent.run_full_turn(
                items,
                print_steps=True,
                show_images=args.show,
                debug=args.debug,
            )
            items += output_items
            args.input = None


if __name__ == "__main__":
    main()
