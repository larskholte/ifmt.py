#!/usr/bin/python

"""Program to format text files, intelligently truncating lines at a given number of columns while preserving overall document structure."""

import argparse
import re
import string
import sys

# Returns a guess as to what the prefix of the given line is.
def guess_prefix(line):
    if len(line) == 0: return ''
    # Find the index of the first non-whitespace character.
    i = 0
    while i < len(line):
        if line[i] in string.whitespace: i += 1
        else: break
    # C-style comments.
    if line[i:i+3] == '// ':
        return line[0:i+3]
    if line[i:i+2] == '//':
        return line[0:i+2]
    # Python-style comments.
    if line[i:i+2] == '# ':
        return line[0:i+2]
    if line[i] == '#':
        # Protect preprocessor directives.
        if line[0:7] == '#ifndef': return ''
        if line[0:6] == '#ifdef': return ''
        if line[0:6] == '#endif': return ''
        return line[0:i+1]
    # Bullets with asterisks.
    if line[i] == '*':
        # Find the next non-whitespace character.
        k = i + 1
        while k < len(line):
            if line[k] in string.whitespace: k += 1
            else: break
        return line[:k]
    # Outline form: up to four letters or numbers followed by 
    # A non-whitespace prefix could not be identified. Preserve indentation.
    return line[0:i]

# Returns the prefix that is expected to follow the given prefix. For instance, bulleted list prefixes are followed by indentations.
def next_prefix(prefix):
    # Bulleted lists.
    if '*' in prefix:
        indent = ''
        for char in prefix:
            if char == '*': indent += ' '
            else: indent += char
        return indent
    # No change.
    return prefix

# Returns the index of the column after the last character of the given word if it were to be appended at the given column.
# Essentially, returns the current column plus the number of columns that would be consumed if the given word was appended.
def add_cols(word, current_cols, context):
    for char in word:
        if char == '\t': current_cols += context['tabstop'] - (current_cols % context['tabstop'])
        else: current_cols += 1
    return current_cols

# Removes tabs from the given word, replacing them with spaces as specified by the given tabstop and offset.
# Returns the new word.
def retab(word, offset, tabstop):
    new_word = ''
    for char in word:
        if char == '\t': new_word += ' ' * (tabstop - (offset % tabstop))
        else: new_word += char
    return new_word

# Prints the given words and appends a newline.
# Uses the prefix contained in the context.
def print_words_as_line(words, context):
    global output
    # Print the prefix first.
    output.write(context['prefix'])
    # Create a list of all the words that need to be printed.
    printed_words = []
    # Index of the last non-whitespace word.
    k = 0
    i = 0
    while i < len(words):
        # Only print whitespace words if they are followed by non-whitespace words.
        if not is_whitespace(words[i]):
            while k <= i:
                printed_words.append(words[k])
                k += 1
        i += 1
    # If we want to justify the text, we may need to insert spaces.
    cols = 0
    if context.get('justify') and context.get('flow'):
        # Count the number of columns the text will take up.
        i = 0
        while i < len(printed_words):
            # If we are justifying text, we remove tab characters.
            printed_words[i] = retab(printed_words[i],cols,context['tabstop'])
            cols = add_cols(printed_words[i],cols,context)
            i += 1
        deficit = context['width'] - cols
        # Record the original number of words.
        original_words = len(printed_words)
        # Insert spaces to make up the difference.
        i = 0
        while i < deficit:
            printed_words.insert(int((original_words-1)-(float(i)/deficit)*(original_words-2)),' ')
            i += 1
    # Write all the words that need to be printed.
    for word in printed_words:
        output.write(word)
    output.write('\n')

# Returns true if the given word contains only whitespace characters.
def is_whitespace(word):
    for char in word:
        if char not in string.whitespace: return False
    return True

# Resolves the context left over from the previous line.
def resolve_context(context):
    # If the context has underflow, we must print it.
    if context.get('underflow'):
        context['flow'] = False
        process_words([],context)
        context['flow'] = True

# Processes the given words according to the given context, and returns the resulting context.
def process_words(words, context):
    global output
    # Keep track of the number of columns used.
    cols = 0
    # If there was underflow from the last line, prepend it to the list of words to be printed.
    underflow = context.get('underflow')
    if underflow:
        i = 0
        while i < len(underflow):
            words.insert(i,underflow[i])
            i += 1
        # Delete the underflow context.
        context['underflow'] = None
    word_index = 0
    # If there are no words to print, we print the prefix and return.
    if len(words) == 0:
        print_words_as_line(words, context)
        return context
    # Reserve room for any prefix.
    if context.get('prefix'):
        cols = add_cols(context['prefix'],cols,context)
    # Always reserve space for the first word.
    cols = add_cols(words[0],cols,context)
    while 1:
        word_index += 1
        # If we have run through all the words in the line without running out of room, print them and return.
        if word_index >= len(words):
            if context.get('flow'): 
                # Add a space word to the end of the word list.
                words.append(' ')
                # The current line is treated as underflow for the next one.
                context['underflow'] = words
                return context
            else:
                print_words_as_line(words, context)
                return context
        # Add the next word if there is room for it.
        cols = add_cols(words[word_index],cols,context)
        # Write the line out and make a recursive call to this function for the remaining words if there is no more room.
        if cols > context['width']:
            # There is no room for the next word. Write all the words up to the current word.
            print_words_as_line(words[:word_index], context)
            # Ignore all whitespace words immediately following the last word printed.
            while word_index < len(words):
                if is_whitespace(words[word_index]): word_index += 1
                else: break
            # See if the prefix needs to change.
            context['prefix'] = next_prefix(context['prefix'])
            # If the only words remaining were whitespace words, do not process any more words.
            if word_index >= len(words): return context
            return process_words(words[word_index:], context)

# Processes the given line using the given context. Returns the context for the next line.
def process_line(line, context):
    # Remove trailing whitespace from all lines.
    line = line.rstrip()
    # Guess the prefix.
    prefix = guess_prefix(line)
    # Split line after the prefix up into words and whitespace "words".
    words = re.split(r'(\s+)', line[len(prefix):])
    # See if this line is all whitespace.
    all_whitespace = True # Innocent until proven guilty.
    for word in words:
        if not is_whitespace(word):
            all_whitespace = False
            break
    # If the prefix of this line differs from what is expected to follow the previous line, we must resolve the previous line's context.
    # We should also resolve the context on lines that are empty except for a prefix.
    if prefix != next_prefix(context['prefix']) or all_whitespace:
        resolve_context(context)
        context['prefix'] = prefix
    # If source code processing is specified, we want to flow in comments (which have non-whitespace prefixes)
    # but not in the rest of the code (which has whitespace indents).
    if context['code']:
        if is_whitespace(prefix): context['flow'] = False
        else: context['flow'] = True
    return process_words(words, context)

# If the program is being executed (as opposed to being imported as a module), process command-line arguments.
if __name__ == '__main__':

    # Define arguments this program accepts.
    parser = argparse.ArgumentParser('ifmt.py',description=__doc__)
    parser.add_argument('-w','--width',dest='width',metavar='width',type=int,default=80,help='Maximum number of columns (default: %(default)s)'); # Max columns
    parser.add_argument('-t','--tabstop',dest='tabstop',metavar='tabstop',type=int,default=8,help='Number of columns between tabstops (default: %(default)s)'); # Tabstop
    parser.add_argument('inputs',metavar='input',type=argparse.FileType('r'),nargs='+',help='Input file. If "-", STDIN is read.') # Input file
    parser.add_argument('-o','--output',dest='output',metavar='output',type=argparse.FileType('w'),help='Output file. If unspecified, output is written to STDOUT.') # Output file
    parser.add_argument('-O','--overwrite',dest='overwrite',metavar='overwrite',action='store_const',const=True,help='If specified, input files are overwritten in place. Cannot be specified in tandem with -o (--output).') # Overwrite
    parser.add_argument('-f','--flow',dest='flow',metavar='flow',action='store_const',const=True,help='If specified, consecutive non-empty lines are presumed to be part of the same block of text. Newlines are not preserved.') # Line flow.
    parser.add_argument('-j','--justify',dest='justify',metavar='justify',action='store_const',const=True,help='If specified, output is right- and left-justified. Implies \'-f\'. Neither tabs nor newlines are preserved.') # Justification.
    parser.add_argument('--code',dest='code',metavar='code',action='store_const',const=True,help='If specified, input lines flow together except in lines with whitespace prefixes (indented code). This means that comment blocks flow together while code blocks are wrapped.') # Comment flow.

    # Parse arguments
    args = parser.parse_args()

    # Check for argument conflicts.
    if args.justify and args.flow:
        sys.stderr.write('Warning: Justification (\'-j\' or \'--justify\') implies flow (\'-f\' or \'--flow\'). Both are specified.\n')
    if args.output and args.overwrite:
        raise Exception('Cannot specify an output file (\'-o\' or \'--output\') and overwrite (\'-O\') in tandem.')
    if args.code and (args.flow or args.justify):
        raise Exception('\'--code\' implies \'--flow\', but only for certain parts of the file.')

    # Justification implies flow.
    if args.justify: args.flow = True

    # Process each input file.
    for input in args.inputs:

        # Determine the output file.
        if args.overwrite:
            import tempfile
            output = tempfile.TemporaryFile()
        else:
            if args.output: output = args.output
            else: output = sys.stdout

        # The starting context.
        context = {'flow':args.flow,'justify':args.justify,'width':args.width,'tabstop':args.tabstop,'prefix':'','code':args.code}

        # Process each line of the input file.
        line = input.readline()
        while line:
            context = process_line(line, context)
            line = input.readline()

        # Finally, we must resolve the context of the final line.
        resolve_context(context)

        # Overwrite the input file, if specified.
        if args.overwrite:
            # Reopen the input file in write mode.
            input.close()
            input = open(input.name,'w')
            # Go to the beginning of the temporary file we created, and write each line to the original input file.
            output.seek(0)
            input.writelines(output.readlines())
            # Close the temp file and input file.
            input.close()
            output.close()
