# Here's what I've completed so far:
(As a sidenote, I've moved a little faster than expected, and some of my implementations are in a slightly different order than I planned)

##	Week 3:
- The initial set up of the key value store has been implemented!
- The program allows for loading the initial data from the JSON
file (from https://data.cdc.gov/api/views/cjae-szjv/rows.json?accessType=DOWNLOAD) and loading the initial data (along with any modifications) to the storage file.
- The user can now:
	- Insert data and expect it to be saved upon entering "exit" or "quit"
		- As a note, the following forms are accepted: 
			1. "INSERT [key] WITH VALUES (col=val, col2=val2, col3=val3….)""
			2. "INSERT VALUES (col=val, col2=val2, col3=val3…)"
	- Have "SELECT \*" and "SELECT \* FROM KEYS" save all keys to a default file
	- Have "SELECT \* FROM VALUES" save all values to a default file
	- Have "SELECT \* FROM ALL" save all keys and values to a default file
	- Have "SELECT [key]" or "SELECT [key] FROM ALL" print the row corresponding to that key



## Week 4:
- Annoying metadata necessary for the maintenance of the program is now hidden, so you will now longer see it when inserting, deleting, selecting, etc
- The user can now:
	- Delete data and expect it to be removed from the storage file upon entering "exit" or "quit"
	- As a note, the following forms are accepted: 
		1. DELETE [key]
		2. DELETE VALUES (col=val, col2=val2, col3=val3….)
	- Update data and expect it to be removed from the storage file upon entering "exit" or "quit"
		- As a note, only UPDATE [key] VALUES (….) is an acceptable format.
	- Select for specific criteria, such as SELECT WHERE col = val, col2 = val2,...


##   Week 5:
The user can now:
- Search for rows in the key value store based on keys and values matching patterns with their substrings! In other words, if you know there is a key or value that starts with, ends with, or contains some combination of characters, but you don't know the whole pattern, you can now search for it!
- As a note, the following forms are accepted:
	1. VALUES (col=pattern1, col2=pattern2, col3=pattern3...)
	2. VALUES (pattern1, pattern2, pattern3)
	3. KEY AND VALUES (pattern1, pattern2, pattern3)
	4. KEY (pattern1, pattern2,...)
- Save or abandon changes made to the key value store in the running program without restarting the program (just type "save" or "abort"!)
- Specify if they want to print the results of Select statements to an output, and if so, whether they want to use the terminal, a default file, or a specified file (given as a path) (notes on how this works is in Usage.md, which is coming soon!)

##   Week 6:
- The user can now print search results to a file!
- When updating and deleting, only necessary lines of the file are read!

## Week 7:
The user can now:
- Find rows in the key value store based on keys and values matching patterns that are similar in terms of edit distance! In other words, if you know there is a key or value that starts with, ends with, or contains some combination of characters, but you don't know the whole pattern, you can know to find it (using Find)!
- As a note, the following forms are accepted:
	1. VALUES (col=pattern1, col2=pattern2, col3=pattern3...)
	2. VALUES (pattern1, pattern2, pattern3)
	3. KEY AND VALUES (pattern1, pattern2, pattern3)
	4. KEY (pattern1, pattern2,...)
- Search through column types (now part of the Search option)
- Specify to OR criteria (such as SELECT WHERE col=val OR col2=val2 OR col3=val3…)

## Week 8:
The user now:
-Can input most JSON files which have tags meta and data at the top hierarchal level of the document.
-Can trivially project items (such as SELECT col1, even if the column type itself is nested somewhere in the values)
-Specify to AND/OR criteria (such as SELECT WHERE col=val AND/OR col2=val2 AND/OR col3=val3…)


## Weeks 9+:
The user now:
-Can input most JSON files
-rename columns
-More efficiently select/delete/search/find items due to the way the keys are selected for while iterating through them
-And restructuring makes the code easier to maintain!