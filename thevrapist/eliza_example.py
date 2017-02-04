import stupid_eliza as eliza
from rules import (
    rules,
    default_responses
)


def main():
    # We need the rules in a list containing elements of the following form:
    # `(input pattern, [output pattern 1, output pattern 2, ...]`
    rules_list = []
    for pattern, transforms in rules.items():
        # Remove the punctuation from the pattern to simplify matching.
        pattern = eliza.remove_punct(str(pattern.upper()))  # kill unicode
        transforms = [str(t).upper() for t in transforms]
        rules_list.append((pattern, transforms))

    audio_interface = eliza.AudioInterface('en', 'en')
    eliza_bot = eliza.Eliza(audio_interface, rules_list, 'en')

    eliza_bot.interact(
        'ELIZA> ',
        list(map(str.upper, default_responses))
    )


if __name__ == '__main__':
    main()

