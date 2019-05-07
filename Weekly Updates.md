## Here's what I've completed so far:
(As a sidenote, I've moved a little faster than expected, and some of my implementations are in a slightly different order than I planned)

-	Week 3:
-- The initial set up of the key value store has been implemented!
--- The program allows for loading the initial data from the JSON
file (from https://data.cdc.gov/api/views/cjae-szjv/rows.json?accessType=DOWNLOAD) and loading the initial data (along with any modifications) to the storage file.
-- The user can now:
--- Insert data and expect it to be saved upon entering "exit" or "quit"
---- As a note, the following forms are accepted: 
----- 1. "INSERT [key] WITH VALUES (col=val, col2=val2, col3=val3….)""
----- 2. "INSERT VALUES (col=val, col2=val2, col3=val3…)"
--- Have "SELECT \*" and "SELECT \* FROM KEYS" save all keys to a default file
--- Have "SELECT \* FROM VALUES" save all values to a default file
--- Have "SELECT \* FROM ALL" save all keys and values to a default file
--- Have "SELECT [key]" or "SELECT [key] FROM ALL" print the row corresponding to that key



-   Week 4:
-- Annoying metadata necessary for the maintenance of the program is now hidden, so you will now longer see it when inserting, deleting, selecting, etc
-- The user can now:
--- Delete data and expect it to be removed from the storage file upon entering "exit" or "quit"
---- As a note, the following forms are accepted: 
----- 1. DELETE [key]
----- 2. DELETE VALUES (col=val, col2=val2, col3=val3….)
-- Update data and expect it to be removed from the storage file upon entering "exit" or "quit"
---- As a note, only UPDATE [key] VALUES (….) is an acceptable format.
---- Select for specific criteria, such as SELECT WHERE col = val, col2 = val2,...


-   Week 5:
-- The user can now:
--- Search for rows in the key value store based on keys and values matching patterns that their substrings! In other words, if you know there is a key or value that starts with, ends with, or contains some combination of characters, but you don't know the whole pattern, you can know search for it!
---- As a note, the following forms are accepted:
----- 1. VALUES (col=pattern1, col2=pattern2, col3=pattern3….),
----- 2. VALUES (pattern1, pattern2, pattern3),
----- 3. KEY AND VALUES (pattern1, pattern2, pattern3),
----- and 4. KEY (pattern1, pattern2,…)
--- Save or abandon changes made to the key value store in the running program without restarting the program (just type "save" or "abort"!)
--- Specify if they want to print the results of Select statements to an output, and if so, whether they want to use the terminal, a default file, or a specified file (given as a path) (notes on how this works is in Usage.md, which is coming soon!)

