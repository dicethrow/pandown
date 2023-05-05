- 5may23
	- I've just noticed that at the moment, a backslash in markdown will result in a backslash character in the latex file, which the latex interpreter can't handle.
		- The recommended latex way to use backslashes is to substitute them for `\textbackslash{}`, so if this test fails, then it indicates that this substitution does not occur.
		
	- note - currently unsolved!
		- although perhaps if a backslash followed by a space, `\ `, could be avoided, as they seem to be turned into `~` for some reason, so backslashes are always up against something,