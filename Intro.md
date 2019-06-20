
# About Me and this project

Hi! I'm Vibha Vijayakumar, currently a rising senior at Caltech majoring in Computer Science. 


This project is for my CS 123 class, Projects in Database Systems. I'm implementing a pretty simple key-value store to understand and show off some awesome things that can be done with a simple understanding of Python and lots (I'm not kidding, **LOTS**) of data!

PistolShrimpDB is a Python executable implemented as a key value store, a type of NoSQL database! Here's more information about this key value store, and how it works, usually in order of execution:

- You can pick a JSON file to load in, and as long as it is in the proper format it should work. If you do not identify a JSON file (you simply press enter), the default should be PistolShrimpStoreDB.bin. If this has not been set up yet, you will receive an error message and be prompted to type in a file name again.
- You can also specify what the data and column types (a way to label data such that each element within the entry (or row, as it will be called in this program) is assigned a label, making key value store commands such as selects easier – they are basically keys assigned to each of the items in each entry) are before loading the data
-  Next, you can specify which storage file to store to. We check to make sure the output file can be created before accepting it, and if you do not want to specify a file, you can press Enter and the default file, PistolShrimpStoreDB.bin, will be used.
- Upon initialization, upon a message: "Now we can do awesome stuff! You can exit the program with exit or quit if you want your changes saved, or with abort if you don't. You can also save your changes with save and undo them with undo!,” you can do the following:
		- save all changes so far without exiting the program since starting the program or the last save or undo (save)
		- undo all changes so far without exiting the program since starting the program or the last save or undo (undo)
		- save all changes so far while exiting the program since starting the program or the last save or undo (exit), (quit)
		- exit the program without making any changes specified since starting the program or the last save or undo (abort)
		- insert any values (insert)
		- delete any values in the key value store (delete)
		- update any existing values in the store (update), rename columns (rename), 
		- select for all keys, values, keys and values, a row matching a specific key, or for rows meeting specific criteria, 
		- search through values and/or keys using the keyword for rows containing certain substrings (search), 
		- search through values and/or keys using the keyword for rows containing certain strings with a ratioDistance less than a limit (see diffllib for more details) (find), and 
		- rename columns (rename)