#!/usr/bin/env python

"""
**Eliza** is a pattern-matching automated psychiatrist.  Given a set of rules
in the form of input/output patterns, Eliza will attempt to recognize user input
phrases and generate relevant psychobabble responses.

Each rule is specified by an input pattern and a list of output patterns.  A
pattern is a sentence consisting of space-separated words and variables.  Input
pattern variables come in two forms: single variables and segment variables;
single variables (which take the form `?x`) match a single word, while segment
variables (which take the form `?*x`) can match a phrase.  Output pattern
variables are only single variables.  The variable names contained in an input
pattern should be the same as those in the corresponding output pattern, and
each segment variable `?*x` in an input pattern corresponds to the single
variable `?x` in the output pattern.

The conversation proceeds by reading a sentence from the user, searching through
the rules to find an input pattern that matches, replacing variables in the
output pattern, and printing the results to the user.

For examples of using this scheme, see the following programs:

- [Eliza](examples/eliza/eliza.html)
- [Automated technical support system](examples/eliza/support.html)

This implementation is inspired by Chapter 5 of "Paradigms of Artificial
Intelligence Programming" by Peter Norvig.
"""
from gtts import gTTS
import os
import random
import string
import speech_recognition as sr

r = sr.Recognizer()


class Eliza:

    def __init__(self, interface, rules, language):
        self.interface = interface
        self.rules = rules
        self.language = language

    def interact(self, prompt, default_responses):
        """Have a conversation with a user."""
        # Read a line, process it, and print the results until no input remains.
        while True:
            # Remove the punctuation from the input and convert to upper-case
            # to simplify matching.
            try:
                user_input = self.interface.get_user_input()
                print(user_input)
                #user_input = translate(user_input, to_lang=self.language)
                #print(user_input)
            except:
                break
            response_en = self.respond(user_input, default_responses)
            self.interface.get_user_output(response_en)
            #response = translate(response_en, to_lang='pl')
            #self.interface.get_user_output(response)

    def respond(self, user_input, default_responses):
        """Respond to an input sentence according to the given rules."""

        inp = user_input.split()  # match_pattern expects a list of tokens

        # Look through rules and find input patterns that matches the input.
        matching_rules = []
        for pattern, transforms in self.rules:
            pattern = pattern.split()
            replacements = match_pattern(pattern, inp)
            if replacements:
                matching_rules.append((transforms, replacements))

        # When rules are found, choose one and one of its responses at random.
        # If no rule applies, we use the default rule.
        if matching_rules:
            responses, replacements = random.choice(matching_rules)
            response = random.choice(responses)
        else:
            replacements = {}
            response = random.choice(default_responses)

        # Replace the variables in the output pattern with the values matched from
        # the input string.
        for variable, replacement in replacements.items():
            replacement = ' '.join(switch_viewpoint(replacement))
            if replacement:
                response = response.replace('?' + variable, replacement)

        return response


class TerminalInterface:

    def get_user_input(self):
        text = input()
        return text

    def user_output(self, response):
        print(response)


class AudioInterface:

    def __init__(self, input_lang, output_lang):
        self.input_lang = input_lang
        self.output_lang = output_lang

    def get_user_input(self):
        audio = self._get_audio()
        print('got audio')
        text = self._transcribe(audio)
        print(text if text else 'No text')
        return text

    def get_user_output(self, response):
        print(response)
        self._read_text(response)

    def _get_audio(self):
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
        return audio

    def _transcribe(self, audio):
        """Turn audio into text"""
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            user_input = remove_punct(
                r.recognize_google(audio, language=self.input_lang).upper()
            )
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except:
            print('Exception occurred')
        return user_input

    def _read_text(self, text):
        tts = gTTS(text=text, lang=self.output_lang)
        tts.save("response.mp3")
        os.system("mpg321 response.mp3 --quiet")
        os.system('rm response.mp3')


def translate(text, to_lang='pl'):
    from yandex_translate import YandexTranslate
    api_key = ''
    translator = YandexTranslate(api_key)
    response = translator.translate(text, to_lang)
    return response.get('text')[0]




## Pattern matching

def match_pattern(pattern, user_input, bindings=None):
    """
    Determine if the input string matches the given pattern.

    Expects pattern and input to be lists of tokens, where each token is a word
    or a variable.

    Returns a dictionary containing the bindings of variables in the input
    pattern to values in the input string, or False when the input doesn't match
    the pattern.
    """

    # Check to see if matching failed before we got here.
    if bindings is False:
        return False
    
    # When the pattern and the input are identical, we have a match, and
    # no more bindings need to be found.
    if pattern == user_input:
        return bindings

    bindings = bindings or {}

    # Match input and pattern according to their types.
    if is_segment(pattern):
        token = pattern[0] # segment variable is the first token
        var = token[2:] # segment variable is of the form ?*x
        return match_segment(var, pattern[1:], user_input, bindings)
    elif is_variable(pattern):
        var = pattern[1:] # single variables are of the form ?foo
        return match_variable(var, [user_input], bindings)
    elif contains_tokens(pattern) and contains_tokens(user_input):
        # Recurse:
        # try to match the first tokens of both pattern and input.  The bindings
        # that result are used to match the remainder of both lists.
        return match_pattern(pattern[1:],
                             user_input[1:],
                             match_pattern(pattern[0], user_input[0], bindings))
    else:
        return False


def match_segment(var, pattern, user_input, bindings, start=0):
    """
    Match the segment variable against the input.

    pattern and input should be lists of tokens.

    Looks for a substring of input that begins at start and is immediately
    followed by the first word in pattern.  If such a substring exists,
    matching continues recursively and the resulting bindings are returned;
    otherwise returns False.
    """

    # If there are no words in pattern following var, we can just match var
    # to the remainder of the input.
    if not pattern:
        return match_variable(var, user_input, bindings)

    # Get the segment boundary word and look for the first occurrence in
    # the input starting from index start.
    word = pattern[0]
    try:
        pos = start + user_input[start:].index(word)
    except ValueError:
        # When the boundary word doesn't appear in the input, no match.
        return False

    # Match the located substring to the segment variable and recursively
    # pattern match using the resulting bindings.
    var_match = match_variable(var, user_input[:pos], dict(bindings))
    match = match_pattern(pattern, user_input[pos:], var_match)

    # If pattern matching fails with this substring, try a longer one.
    if not match:
        return match_segment(var, pattern, user_input, bindings, start + 1)
    
    return match


def match_variable(var, replacement, bindings):
    """Bind the input to the variable and update the bindings."""
    binding = bindings.get(var)
    if not binding:
        # The variable isn't yet bound.
        bindings.update({var: replacement})
        return bindings
    if replacement == bindings[var]:
        # The variable is already bound to that input.
        return bindings

    # The variable is already bound, but not to that input--fail.
    return False


## Pattern matching utilities

def contains_tokens(pattern):
    """Test if pattern is a list of subpatterns."""
    return type(pattern) is list and len(pattern) > 0


def is_variable(pattern):
    """Test if pattern is a single variable."""
    return (type(pattern) is str
            and pattern[0] == '?'
            and len(pattern) > 1
            and pattern[1] != '*'
            and pattern[1] in string.ascii_letters
            and ' ' not in pattern)


def is_segment(pattern):
    """Test if pattern begins with a segment variable."""
    return (type(pattern) is list
            and pattern
            and len(pattern[0]) > 2
            and pattern[0][0] == '?'
            and pattern[0][1] == '*'
            and pattern[0][2] in string.ascii_letters
            and ' ' not in pattern[0])


## Translating user input

def replace(word, replacements):
    """Replace word with rep if (word, rep) occurs in replacements."""
    for old, new in replacements:
        if word == old:
            return new
    return word


def switch_viewpoint(words):
    """Swap some common pronouns for interacting with a robot."""
    replacements = [('I', 'YOU'),
                    ('YOU', 'I'),
                    ('ME', 'YOU'),
                    ('MY', 'YOUR'),
                    ('AM', 'ARE'),
                    ('ARE', 'AM')]
    return [replace(word, replacements) for word in words]


def remove_punct(string):
    """Remove common punctuation marks."""
    if string.endswith('?'):
        string = string[:-1]
    return (string.replace(',', '')
            .replace('.', '')
            .replace(';', '')
            .replace('!', ''))
