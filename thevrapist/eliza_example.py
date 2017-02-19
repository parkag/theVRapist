from thevrapist.stupid_eliza import Eliza
from thevrapist.io import AudioInterface, remove_punct
from thevrapist.rules import (
    rules,
    default_responses
)


def load_rules():
    rules_list = []
    for pattern, transforms in rules.items():
        # Remove the punctuation from the pattern to simplify matching.
        pattern = remove_punct(str(pattern.upper()))  # kill unicode
        transforms = [str(t).upper() for t in transforms]
        rules_list.append((pattern, transforms))
    return rules_list



def main():
    rules_list = load_rules()

    audio_interface = AudioInterface('pl', 'pl')
    eliza_bot = Eliza(
        interface=audio_interface,
        rules=rules_list,
        default_responses=list(map(str.upper, default_responses)),
        language='en'
    )

    eliza_bot.interact()


if __name__ == '__main__':
    main()
