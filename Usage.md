# Usage
This is a list of all commands you need (so far) to operate this key-value store. There is also a list of commands I hope to implement in the coming weeks :)

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
	- Selects the row meeting all the criteria given by the columns and values. If nothing matches the criteria, the program will say so!
	- For example: SELECT WHERE measureId=84, stateId=1, countyId=1101, year=1999, measurement=3353220
	- You can subtract variables to yield more results!
3. Deletes:
- DELETE [key]
	- Deletes the row corresponding to the given key. If the key is not in the store, the program will say so!
- DELETE VALUES (col=val, col2=val2, col3=val3...)
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

## Coming soon! By 6/7/19 hopefully :)
1. SELECTS:
- Instead of SELECT WHERE (col=val, col2=val2,...):
	- SELECT WHERE (col=val AND col2=val2 AND...) (which is the equivalent of the current implementation)
	- SELECT WHERE (col=val OR col2=val2 OR ...)
2. SEARCHES:
	- All searches will be of the form:
		- SEARCH VALUES (col=pattern1 AND col2=pattern2 AND col3=pattern3...)
		- SEARCH VALUES (col=pattern1 OR col2=pattern2 OR col3=pattern3...)
		- SEARCH VALUES (pattern1 AND pattern2 AND pattern3...)
		- SEARCH VALUES (pattern1 OR pattern2 OR pattern3...)
		- SEARCH KEY AND VALUES (pattern1 AND pattern2 AND pattern3...)
		- SEARCH KEY AND VALUES (pattern1 OR pattern2 OR pattern3...)
		- SEARCH KEY (pattern1 AND pattern2...)
		- SEARCH KEY (pattern1 OR pattern2...)
3. Instead of DELETE VALUES (col=val, col2=val2, col3=val3...):
	- DELETE VALUES (col=val AND col2=val2 AND col3=val3...)
	- DELETE VALUES (col=val OR col2=val2 OR col3=val3...)

- These new options will allow the options we select for match exactly 1 criteria instead of every single one that we specify.
