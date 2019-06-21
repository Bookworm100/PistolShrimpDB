# Usage
This is a list of all commands you need (so far) to operate this key-value store. Note: for the operations allowing ands/ors, ands have precedence over ors.
Also, the parentheses are optional in the commands below and are shown for readibility.
And commands are case-insensitive (mostly lower case enforced).

## Basic commands:
1. save
- save all changes made so far without exiting the program since starting the program or the last save or undo
2. undo
- undoing all changes made so far without exiting the program since starting the program or the last save or undo
3. exit
- save all changes made so far while exiting the program since starting the program or the last save or undo
4. quit
- same as #3.
5. abort
- exit the program without making any changes specified since starting the program or the last save or undo

## Key-value store specific commands:
(Note: The parentheses are not exactly necessary at the moment)
If the format does not match as specified, you will be shown the usage of the specific command and you will have to retype it.
1.  Inserts:
- INSERT [key] WITH VALUES (col=val, col2=val2, col3=val3...)
	- Inserts a row with a specified key with the corresponding columns and values. 
	- Note: if a key already exists in the store, a random one is selected instead. It will be returned to you so you can use it for further modifications and viewing.
- INSERT VALUES (col=val, col2=val2, col3=val3…)
	- Inserts a row with the corresponding columns and values. a random key is selected and returned to you so you can use it for further modifications and viewing.
2. Selects (all selects will be printed to the terminal or saved to a file, depending on your preference):
- SELECT \* 
	- Selects all the keys
- SELECT \* FROM KEYS
	- Selects all the keys
- SELECT \* FROM VALUES
	- Selects all the values
- SELECT \* FROM ALL
	- Selects all the keys and values
- SELECT [key] 
	- Selects the row corresponding to the given key. If the key is not in the store, the program will say so!
- SELECT [key] FROM ALL
	- Selects the row corresponding to the given key. If the key is not in the store, the program will say so!
- SELECT WHERE (col=val, col2=val2,...)
	- Selects the rows meeting all the criteria given by the columns and values. If nothing matches the criteria, the program will say so!
	- For example: SELECT WHERE measureId=84, stateId=1, countyId=1101, year=1999, measurement=3353220
	- You can subtract variables to yield more results!
- SELECT WHERE (col=val AND/OR col2=val2 AND/OR...)
	- Selects the rows meeting all the criteria given by the columns and values. If nothing matches the criteria, the program will say so!
3. Deletes:
- DELETE [key]
	- Deletes the row corresponding to the given key. If the key is not in the store, the program will say so!
- DELETE VALUES (col=val, col2=val2, col3=val3...)
	- Deletes the row meeting all the criteria given by the columns and values. If nothing matches the criteria, the program will say so!
- DELETE VALUES (col=val AND/OR col2=val2 AND/OR col3=val3...)
	- Deletes the row meeting all the criteria given by the columns and values. If nothing matches the criteria, the program will say so!
4. Updates: UPDATE [key] VALUES (col=val, col2=val2, col3=val3...) 
	- Updates the row corresponding to the given key with the new values in the columns. If the key is not in the store, the program will say so!
	- For example: UPDATE row-tmj3.7qu6.ckbc WITH VALUES (measureId=100, year=2050)

5. Searches:
- SEARCH VALUES (col=pattern1, col2=pattern2, col3=pattern3...)
	- Searches the store's values corresponding to each column type for those which are superstrings of the corresponding given pattern
- SEARCH VALUES (pattern1, pattern2, pattern3...)
	- Searches the store's values (per row) corresponding for those which are superstrings of the corresponding given pattern
- SEARCH KEY AND VALUES (pattern1, pattern2, pattern3...)
	- Searches the store's rows (keys and values) for those which contain all the patterns
- SEARCH KEY (pattern1, pattern2...)
	- Searches the store's keys corresponding for those which contain all the patterns
- SEARCH VALUES (col=pattern1 AND/OR col2=pattern2 AND/OR col3=pattern3...)
	- Searches the store's values corresponding to each column type for those which are superstrings of the corresponding given pattern
- SEARCH VALUES (pattern1 AND/OR pattern2 AND/OR pattern3...)
	- Searches the store's values (per row) corresponding for those which are superstrings of the corresponding given pattern
- SEARCH KEY AND VALUES (pattern1 AND/OR pattern2 AND/OR pattern3...)
	- Searches the store's rows (keys and values) for those which contain all the patterns
- SEARCH KEY (pattern1 AND/OR pattern2...)
	- Searches the store's keys corresponding for those which contain all the patterns

6. Find:
- FIND [opt: limit] VALUES (col=pattern1, col2=pattern2, col3=pattern3...)
	- Searches the store's values corresponding to each column type for those values which, with the corresponding given pattern, compute to a difflib.SequenceMatcher.ratio() value less than a given limit
- FIND [opt: limit] VALUES (pattern1, pattern2, pattern3...)
	- Searches the store's values (per row) corresponding for those values which, with the corresponding given pattern, compute to a difflib.SequenceMatcher.ratio() value less than a given limit
- FIND [opt: limit] KEY AND VALUES (pattern1, pattern2, pattern3...)
	- Searches the store's rows (keys and values) for those those values which, with the corresponding given pattern, compute to a difflib.SequenceMatcher.ratio() value less than a given limit
- FIND [opt: limit] KEY (pattern1, pattern2...)
	- Searches the store's keys corresponding for those values which, with the corresponding given pattern, compute to a difflib.SequenceMatcher.ratio() value less than a given limit
- FIND [opt: limit] VALUES (col=pattern1 AND/OR col2=pattern2 AND/OR col3=pattern3...)
	- Searches the store's values corresponding to each column type for those which are superstrings of the corresponding given pattern
- FIND [opt: limit] VALUES (pattern1 AND/OR pattern2 AND/OR pattern3...)
	- Searches the store's values (per row) corresponding for those values which, with the corresponding given pattern, compute to a difflib.SequenceMatcher.ratio() value less than a given limit
- FIND [opt: limit] KEY AND VALUES (pattern1 AND/OR pattern2 AND/OR pattern3...)
	- Searches the store's rows (keys and values) for those values which, with the corresponding given pattern, compute to a difflib.SequenceMatcher.ratio() value less than a given limit
- FIND [opt: limit] KEY (pattern1 AND/OR pattern2...)
	- Searches the store's keys corresponding for those values which, with the corresponding given pattern, compute to a difflib.SequenceMatcher.ratio() value less than a given limit

7. RENAME 'col1' 'col2'
	- Allows col1 to be renamed col2. This works for columns where col1 is in at least one entry in the key value store.
	- Single quotes are only for the rename option.