ifmt.py
======
Intelligent text reformatting

Description
-----------
Similar to UNIX's `fmt`, but friendlier to source code, and written in python.

Examples
--------
Presume we have a file with a really long line of text:
```
$ cat lorem_ipsum.txt
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
```

We can easily wrap it to 70 characters:
```
$ ifmt.py -w70 lorem_ipsum.txt
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do
eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
minim veniam, quis nostrud exercitation ullamco laboris nisi ut
aliquip ex ea commodo consequat. Duis aute irure dolor in
reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
```

Or presume we have a source code file with long comments:
```
$ cat src.c
// struct which contains information about a single command-line argument.
struct CAArg {
        // The type of this argument.
        enum CAArgType type;

        // The name of this argument. For keyword arguments, this is the key. For unary arguments, this is the name of the unary argument.
        const char* name;

        // The value of the keyword argument. This field is initially NULL, but is set by calling CAProcessArgs.
        const char* value;
};
```

We can wrap it to 80 characers while preserving indentation and comment structure:
```
$ ifmt.py -w80 src.c
// struct which contains information about a single argument.
struct CAArg {
        // The type of this argument.
        enum CAArgType type;

        // The name of this argument. For keyword arguments, this is the key.
        // For unary arguments, this is the name of the unary argument.
        const char* name;

        // The value of the keyword argument. This field is initially NULL, but
        // is set by calling CAProcessArgs.
        const char* value;
};
```

Or presume we have a file with lines of irregular length:
```
$ cat lorem_ipsum.txt
Lorem ipsum dolor sit amet,
consectetur adipisicing elit,
sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud
exercitation ullamco laboris nisi ut aliquip
ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident,
sunt in culpa qui officia deserunt mollit anim id est laborum.
```
We can cause lines to "flow" together into paragraphs with the `-f` option.
```
$ ifmt.py -f lorem_ipsum.txt
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
culpa qui officia deserunt mollit anim id est laborum.
```

Intelligently handles bulleted lists:
```
$ cat bullets.txt
*   Suppose you have a bulleted list with more than 80 characters on some of the lines. What happens?
*   Or suppose you have a
    bulleted list that's split
    over many short lines, and you want to expand
    it to 80 columns per line.
```
```
$ ifmt.py -f bullets.txt
*   Suppose you have a bulleted list with more than 80 characters on some of the
    lines. What happens?
*   Or suppose you have a bulleted list that's split over many short lines, and
    you want to expand it to 80 columns per line.
```

Right- and left-justify text with `-j`:
```
$ cat lorem_ipsum.txt
Lorem  ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt  ut  labore et  dolore magna  aliqua. Ut  enim ad  minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
$ ifmt.py -j -w40 - < lorem_ipsum.txt
Lorem  ipsum dolor sit amet, consectetur
adipisicing elit, sed do eiusmod  tempor
incididunt ut  labore  et  dolore  magna
aliqua. Ut  enim ad  minim veniam,  quis
nostrud  exercitation   ullamco  laboris
nisi ut aliquip ex ea commodo consequat.
```

Overwrite files in-place with `-O`:
```
$ cat lorem_ipsum.txt
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
$ ifmt.py -j -O -w100 lorem_ipsum.txt
$ cat lorem_ipsum.txt
larskholte ifmt$ cat lorem_ipsum.txt 
Lorem   ipsum    dolor     sit    amet,    consectetur  adipisicing  elit,  sed  do  eiusmod  tempor
incididunt ut labore  et dolore magna  aliqua. Ut enim  ad minim  veniam, quis nostrud  exercitation
ullamco  laboris nisi ut aliquip ex ea commodo consequat.
```

Suppose you have source code where you want the comment lines to flow together into paragraphs, while the code lines remain unchanged.
This can be accomplished with the --code flag:
```
$ cat hello_world.c
// From: http://www.tldp.org/HOWTO/NCURSES-Programming-HOWTO/helloworld.html

#include <ncurses.h>
#include <signal.h>
#include <stdlib.h>

// Function which cleans up after
// this program.
// Registered to be called before the program exits.
void end() {
	endwin();
}

int main() {
	// Register a function to be called when the program terminates. This function is called whether the program terminates normally or not.
	atexit(end);

	// Initialize the ncurses library and the terminal screen.
	initscr();

	// Print a message to the terminal.
	// This is a test
	// to see if comment flow
	// works.
	printw("Hello world!");
	refresh();

	// Wait for user input.
	getch();

	return 0;
}
```
```
$ ifmt.py --code hello_world.c
// From: http://www.tldp.org/HOWTO/NCURSES-Programming-HOWTO/helloworld.html

#include <ncurses.h>
#include <signal.h>
#include <stdlib.h>

// Function which cleans up after this program. Registered to be called before
// the program exits.
void end() {
	endwin();
}

int main() {
	// Register a function to be called when the program terminates. This
	// function is called whether the program terminates normally or not.
	atexit(end);

	// Initialize the ncurses library and the terminal screen.
	initscr();

	// Print a message to the terminal. This is a test to see if comment
	// flow works.
	printw("Hello world!");
	refresh();

	// Wait for user input.
	getch();

	return 0;
}
```

For a complete list of options:

    ifmt.py -h
