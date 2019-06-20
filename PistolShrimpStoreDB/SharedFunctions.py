import sys
import re

""" Module: Shared Functions 
    Description: SharedFunctions.py contains functions used by multiple other
                 modules.

    Functions: 
    
        spaceMatches - Used to separate out column types and values in commands
                       with commas (Used in Delete.py, Insert.py, Search.py, 
                       Selects.py, Update.py)
                       
        conjMatches - Used to separate out column types and values in commands
                      containing ands and ors (Used in Delete.py, Search.py, Select.py)
        
        printSelectsSearches - Prints out select and search statements to
                               either a terminal or file, depending on user
                               preferences
        
        doesColumnTypeValueMatch - Check that a specific row identified by a key
                                   keys fits the criteria specified by the 
                                   combination of the values, with commas or 
                                   and/ors. (Used by findMatchingKeys, 
                                   selectKeyswithAndOrs, in SharedFunctions.py)
        
        findMatchingKeys - provides the list of keys which match the criteria
                           associated with a specific set of values
        
        selectKeyswithAndOrs - provides the list of keys which match the
                               criteria associated with a specific set of 
                               values with ands/ors
"""


def spaceMatches(index, matches):
    """For commands without ands/ors, spaceMatches is used to separate out
    individual types and values, especially if they contain spaces.

    A regex parser is used to include whitespace but not ',' or '=', so matches
    are separated strictly into their individual types or values. A final pass
    through removes any leading or trailing whitespace, and the list is returned.

    Keyword arguments:
    index -- The index of the first column type/variable of interest
    matches -- The list of column types/variables of interest with a few other
               user-supplied keyword arguments to filter out

    Return:
    listOfItems -- The list of the column type and variables, each
                   as separate elements in the list.
    """

    equalMatches = matches
    # Filter out the other user-supplied arguments, which are at the beginning
    # of the command.
    listOfItems = equalMatches[index:]
    # We specifically designed this function to allow whitespace in our column
    # types and variables, so we include the regular characters and whitespace
    # besides '=', which is a separator. This way, the list is composed of
    # either patterns separated by commas, or alternating column types
    # and values that we use to add, update, select, delete, search, or find.
    parser = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"\s]+', re.IGNORECASE)
    listOfItems = parser.findall(" ".join(listOfItems))
    # Strip leading and trailing whitespaces as they are not part of
    # the original element.
    for i in range(len(listOfItems)):
        listOfItems[i] = listOfItems[i].strip()
    return listOfItems


def conjMatches(index, matches):
    """For commands with ands/ors, conjMatches is used to separate out
    individual types and values, especially if they contain spaces.

    A regex parser is used to include whitespace and splits by ors and then
    ands so matches are separated strictly into their individual types or
    values. A final pass through removes any leading or trailing
    whitespace, and the list is returned.

    Keyword arguments:
    index -- The index of the first column type/variable of interest
    matches -- The list of column types/variables of interest with a few other
               user-supplied keyword arguments to filter out

    Return:
    listOfItems -- The list of the column type and variables, each
                   as separate elements in the list.
    """

    # Filter out the other user-supplied arguments, which are at the beginning
    # of the command.
    equalMatches = " ".join(matches[index:])
    # We specifically designed this function to allow whitespace in our column
    # types and variables, so we include the regular characters and whitespace
    # and split by ors and then ands. This way, the list is composed of
    # patterns separated by ands/ors, or alternating column types and values
    # that we use to select, delete, search, or find.
    parser = re.split(r'\bor\b', equalMatches.lower(), re.IGNORECASE)
    for i in range(len(parser)):
        parser[i] = re.split(r'\band\b', parser[i].lower(), re.IGNORECASE)
        # Strip leading and trailing whitespaces as they are not part of
        # the original element.
        for j in range(len(parser[i])):
            parser[i][j] = parser[i][j].strip()
            par1 = re.compile(r'[a-z-0-9*!@#$%^&~_.+{}:\'"\s]+', re.IGNORECASE)
            parser[i][j] = par1.findall("".join(parser[i][j]))
    return parser


def printSelectsSearches(default_file, toWrite):
    """ printSelectsSearches handles printing of selects and searches to file
    or terminal.

    First, the user is prompted to indicate whether to print the
    output to terminal. Next, if the output is large, and the user
    indicates that they would like the output to be printed to the
    terminal, the user is notified, and is prompted whether they want to
    proceed with printing to terminal. In the case that they want to
    print to file, the user is prompted to indicate if they would like
    to specify a file to store the output. If not, the given default
    filename is used. If so, then the program attempts to open or create
    the file, and if an error is thrown in case the file cannot be created,
    then, the user is prompted to indicate if they would like to specify a
    file to store the output. This repeats until the user types in N, or
    if they specify a valid file path. In any case the user is prompted to
    type Y or N and they do not, they are prompted again to type Y or N.

    Keyword Arguments:
    default_file -- the file that results will be written to if no
                    file is specified by the user
    toWrite -- the string that will be written to the file

    No return values
    """

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
    # is big (should be somewhere between 50 to 100 lines,
    # as each line in the storage file is 1000 bytes).
    if n.lower() == "y" and sys.getsizeof(toWrite) > 50000:
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


def doesColumnTypeValueMatch(key, values, filterItems):
    """ For a given item in the key value store (referenced by its key),
    doesColumnTypeValueMatch checks if that item meets the criteria
    set by the values argument, which contains a set of column type or value
    pairs separated by either commas or ands.

    For each set of value and/or optionally column type pair, the value and
    column type is checked against each row in the given row (referenced by
    the key). Every set and pair must be present in the row for the function
    to return true, as this function looks specifically at ands their
    equivalent commas only (any ors are processed in parent functions in the
    stack).

    Keyword arguments:
    key -- The key of the row/item we want to see fits the criteria the values
           set.
    values -- The criteria provided, column type and value pairs separated by
              commas or ands (ors are handled in a parent function)
    filterItems -- The key value store

    Return values:
    meetsAllAnds - a Boolean flag indicating whether the specific row meets the
                   criteria, indicating whether or not to select that row
    """

    meetsAllAnds = True
    # For each pair, compare their values with each item and if their
    # corresponding column labels and values match, then we continue
    # checking the rest of the pairs.
    for colIndex in range(0, len(values), 2):
        col = values[colIndex]
        val = values[colIndex + 1]
        keys = set(k.lower() for k in filterItems[key]['data'])
        # Checking for a match also includes checking if the
        # column type specified is even in this row.
        if col.lower() not in keys \
                or filterItems[key]['isFree'] != 'false' \
                or filterItems[key]['data'][col].lower() \
                != val.lower():
            meetsAllAnds = False
    # Once we know each pair matches, we know to include them. And
    # if they all do not match, we know not to.
    return meetsAllAnds


def findMatchingKeys(values, dynamicDB):
    """ findMatchingKeys provides the list of keys which match the criteria
    associated with a specific set of values (whether the entire combination
    should match exactly, and if not, which combinations work).

    First, we check that each type is paired up with a value properly (and
    output an error message while quitting if not). Next, for each row/key
    in the key value store, we check if the criteria is met (specified by
    the values) using doesColumnTypeValueMatch. We include the key in the list
    of keys which we return only if the criteria is met.

    Keyword arguments:
    values -- The criteria provided, column type and value pairs separated by
              commas or ands (ors are handled in a parent function)
    dynamicDB -- The key value store

    Return values:
    selectedKeys -- The list of keys which met all criteria the user supplied
    """

    selectedKeys = []
    print(values)
    # If the key-value to delete is simply identifiable by a key, we simply
    # mark that key for deletion.
    if len(values) % 2 == 1:
        print("Column types must be associated with column values!")
        return selectedKeys
    else:
        # Since identification was only specified by rows, we need to filter
        # the rows by each column specified and mark those keys for deletion.
        filterItems = dynamicDB
        for item1 in filterItems:
            # Check that all column types and values are matched correctly
            meetsAllAnds = doesColumnTypeValueMatch(item1, values, filterItems)
            if meetsAllAnds:
                selectedKeys.append(item1)
    if len(selectedKeys) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "column types.")
    return selectedKeys


def selectKeyswithAndOrs(matches, dynamicDB):
    """ selectKeyswithAndOrs collects keys for deletes and selects.

    For every key in the key value store, each associated column
    type and value is verified alongside the required pairs.
    If, for each required pair, there exists a pair (column type and
    value) which is exactly that required pair, then that key
    is included in the list of returned keys.

    Keyword arguments:
    matches -- the list of pairs used to filter the key value store
    dynamicDB -- the key value store

    Return values:
    selectedKeys -- the list of keys selected from the store which contain
                    the pairs
    """

    for orVal in matches:
        for andVal in orVal:
            if len(andVal) % 2 == 1:
                print("Column types must be associated with column values!")
                return []
    filterItems = dynamicDB
    selectedKeys = []
    # We iterate through each element of the key value store exactly once, and
    # include it if it meets the necessary criteria: matching at least one of
    # the or clauses, and all of the inner and clauses.
    for eachKey in filterItems:
        # include indicates whether or not at least one of the inner and
        # clauses meets the criteria.
        include = False
        for orClause in matches:
            meetsAllAnds = True
            # Because of Delete's and Select's usages, we know that columns
            # and their values must be present in pairs.
            for andClause in orClause:
                meetsAllAnds = meetsAllAnds & \
                               doesColumnTypeValueMatch(eachKey, andClause,
                                                        filterItems)
            # Once we know each pair matches, we know to include them.
            if meetsAllAnds:
                include = True
        # We do not need extra checks for ors because they are the union of
        # satisfying keys, and we will not have overlap because we only look
        # at each key once.
        if include:
            selectedKeys.append(eachKey)
    if len(selectedKeys) == 0:
        print("Sorry, nothing in the store matches! Check your input or "
              "column types.")
    return selectedKeys