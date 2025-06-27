# The name of the file where we will store our entries.
FILENAME = "my_log.txt"

def add_to_top_of_file(text):
    """
    Adds a new line of text to the very beginning of the file.
    """
    try:
        with open(FILENAME, 'r') as f:
            original_content = f.read()
    except FileNotFoundError:
        original_content = ""

    new_content = text + "\n" + original_content

    with open(FILENAME, 'w') as f:
        f.write(new_content)
    
    # print(f"✅ Added '{text}' to the top of {FILENAME}")

def main():
    """ The main function that runs the TUI loop. """
    print("--- Simple To-Do TUI ---")
    print("Type what you want to do and press Enter.")
    print("Type 'quit' or 'exit' to stop the program.")
    print("-" * 26)

    while True:
        user_input = input("> ")

        if user_input.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break # This exits the while loop

        if not user_input:
            continue

        add_to_top_of_file(user_input)


if __name__ == "__main__":
    main()

# TODO: commands???