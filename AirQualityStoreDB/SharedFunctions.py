import sys
import re

def spaceMatches(index, matches):
    equalMatches = matches
    matches = equalMatches[index:]
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"\s]+', re.IGNORECASE)
    matches = parser.findall(" ".join(matches))
    for i in range(len(matches)):
        matches[i] = matches[i].strip()
    return matches

def conjMatches(index, matches):
    equalMatches = " ".join(matches[index:])
    parser = re.split(r'\bor\b', equalMatches.lower(), re.IGNORECASE)
    for i in range(len(parser)):
        parser[i] = re.split(r'\band\b', parser[i].lower(), re.IGNORECASE)
        for j in range(len(parser[i])):
            parser[i][j] = parser[i][j].strip()
            par1 = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"\s]+', re.IGNORECASE)
            parser[i][j] = par1.findall("".join(parser[i][j]))
    return parser


""" This handles the printing of selects to a file or output. """
""" First, the user is prompted to indicate whether to print the """
""" output to terminal. Next, if the output is large, and the user """
""" indicates that they would like the output to be printed to the """
""" terminal, the user is notified, and is prompted whether they want to """
""" proceed with printing to terminal. In the case that they want to """
""" print to file, the user is prompted to indicate if they would like """
""" to specify a file to store the output. If not, the given default """
""" filename is used. If so, then the program attempts to open or create """
""" the file, and if an error is thrown in case the file cannot be created, """
""" then, the user is prompted to indicate if they would like to specify a """
""" file to store the output. This repeats until the user types in N, or """
""" if they specify a valid file path. In any case the user is prompted to """
""" type Y or N and they do not, they are prompted again to type Y or N. """
""" @:param: default_file, the file that results will be written to if no """
"""          file is specified by the user"""
""" @:param: toWrite, the string that will be written to the file """
""" @:return: None """
def printSelectsSearches(default_file, toWrite):
    written = False
    # Does the user want to print output to the terminal?
    n = input("Would you like to print the output to the terminal?"
              " Type Y or N only. \n")
    # In case of invalid output
    while n.lower() != "y" and n.lower() != "n":
        n = input("Sorry, we did not quite understand. Please type "
                  "Y only if you want to print to output or N"
                  "if you don't and want to print to a file.\n")
    # The user must confirm if the size of the output
    # is big.
    if n.lower() == "y" and sys.getsizeof(toWrite) > 2000:
        n = input("The size of the output is pretty big. "
                  "Are you sure? Again, type Y or N.\n ")
        while n.lower() != "y" and n.lower() != "n":
            n = input("Sorry, we did not quite understand. Please type "
                      "Y only if you want to print to output or N"
                      "if you don't and want to print to a file,"
                      "given that the file size is big.\n")
    # Print to terminal here.
    if n.lower() == "y":
        print(toWrite)
    else:
        # The user is prompted to indicate if they want to use a custom file.
        n = input("Would you like to create a custom file with the output?"
                  " Type Y or N only. \n")
        # TODO n = n.lower()
        while not written:
            try:
                new_input = default_file
                # If the input is invalid
                while n.lower() != "y" and n.lower() != "n":
                    n = input("Sorry, we did not quite understand. Please type"
                          " Y only if you want to create a custom file or N"
                        "if you don't and want to use our custom file.\n")
                # The user types in the desired file path.
                if n.lower() == "y":
                    new_input = input("Please type in the file name, which can"
                                  " include the path if it's not being stored"
                                  " in the location of this program:\n")
                # The file is opened or created for writing.
                with open(new_input, 'w') as file:
                    file.write(toWrite)
                    written = True
            except IOError:
                # In the case the file cannot be created, the user is
                # asked if they changed their mind and want to use the
                # default file instead.
                n = input("Sorry, this path seems to be invalid."
                              " Would you still like to create a custom file? "
                              " Again, type Y or N.\n")



""" findMatchingKeys removes the values or values assicated with the key """
""" from the dictionary holding the database, and keep track of what might """
""" be removed from the storage file upon exiting or quitting. """
""" @:param: key, an argument which when provided is returned """
""" @:param: values, the list of values """
""" @:param: dynamicDB, the key value store maintained in the program """
""" @:return: selectedKeys, the list of keys to be displayed or deleted """
"""           from the store """
"""def findMatchingKeys(key, values, dynamicDB):
    selectedKeys = []
    # If the key-value to delete is simply
    # identifiable by a key, we simply
    # mark that key for deletion.
    print(values)
    if len(values) == 1:
        selectedKeys.append(key)
    else:
        # Since identification was only specified by
        # rows, we need to filter the rows by each column specified
        # and mark these keys for deletion.
        filterItems = dynamicDB
        # Check that all tags/columns are matched correctly
        if len(values) % 2 == 1:
            print("Column types must be associated with column values!")
            return []

        selected = {}
        for item1 in filterItems:
            include = True
            newVal = {}
            for colIndex in range(0, len(values), 2):
                found = False
                col = values[colIndex]
                val = values[colIndex + 1]
                #print(col)
                #print(val)
                #print(filterItems[item1]['data'])
                #print(filterItems[item1]['isFree'])
                if col in filterItems[item1]['data'] \
                        and filterItems[item1]['isFree'] == 'false':
                    #print(filterItems[item1]['data'] )
                    if filterItems[item1]['data'][col] != val:
                        include = False
                        #print("SLKFJ")
                #if not found:
                #    include = False
                #else:
                #    include = False
            if include:
                #print("Reached")
                newVal[item1] = filterItems[item1]
                selected.update(newVal)
        if len(selected) == 0:
            print("Sorry, nothing in the store matches! Check your input or "
                  "column types.")
            return []
        for item in selected:
            selectedKeys.append(item)"""

"""for colIndex in range(0, len(values), 2):
    col = values[colIndex]
    val = values[colIndex + 1]
    selected = {}
    for item1 in filterItems:
        if col in filterItems[item1]['data'] \
                and filterItems[item1]['isFree'] == 'false':
            if filterItems[item1]['data'][col] == val:
                newVal = {}
                newVal[item1] = filterItems[item1]
                selected.update(newVal)
    filterItems = selected
if len(filterItems) == 0:
    print("Sorry, nothing in the store matches! Check your input or "
          "column types.")
    return []
for item in filterItems:
    selectedKeys.append(item)
return selectedKeys"""

def findMatchingKeys(key, values, dynamicDB):
    selectedKeys = []
    print(values)
    # If the key-value to delete is simply
    # identifiable by a key, we simply
    # mark that key for deletion.
    if len(values) == 1:
        selectedKeys.append(key)
    else:
        # Since identification was only specified by
        # rows, we need to filter the rows by each column specified
        # and mark these keys for deletion.
        filterItems = dynamicDB
        # Check that all tags/columns are matched correctly
        if len(values) % 2 == 1:
            print("Column types must be associated with column values!")
            return []
        for colIndex in range(0, len(values), 2):
            col = values[colIndex]
            val = values[colIndex + 1]
            selected = {}
            for item1 in filterItems:
                if col in filterItems[item1]['data'] \
                        and filterItems[item1]['isFree'] == 'false':
                    if filterItems[item1]['data'][col] == val:
                        newVal = {}
                        newVal[item1] = filterItems[item1]
                        selected.update(newVal)
            filterItems = selected
        if len(filterItems) == 0:
            print("Sorry, nothing in the store matches! Check your input or "
                  "column types.")
            return []
        for item in filterItems:
            selectedKeys.append(item)
    return selectedKeys

