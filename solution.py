import sys
import collections

assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'
cl = list(cols)
rl = list(rows)

def cross(A, B):
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag_units = [[x + y for x, y in zip(rl,cl)]] + [[x + y for x, y in zip(rl, reversed(cl))]]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def remove_digits(values, l, vs):
    """
    Go through all the list and
    remove the value v from peers of c for given sudoku
    Input: A sudoku in dictionary form, l from where value v need to
           removed
    Output: The resulting sudoku in dictionary form.
    """
    for v in vs:
        for k in l:
            if v in values[k]:
                val = values[k].replace(v,"")
                assign_value(values, k, val)
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in unitlist:
        duo = {k:values[k] for k in unit if len(values[k]) == 2}
        # reversing duo to find twin
        rev = collections.defaultdict(list)
        for k, v in duo.items():
            rev[v].append(k)
        # Finding twins
        twins = {k : v for k, v in rev.items() if len(v) == 2}
        for v in twins.keys():
            plist = [val for val in unit if len(values[val]) > 2]
            remove_digits(values, plist, v)
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    return dict(zip(boxes, ['123456789' if x=='.' else x for x in list(grid)]))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    # Write a function that will take as an input, the sudoku in dictionary form,
    # run through all the boxes, applying the eliminate technique,
    # and return the resulting sudoku in dictionary form.
    for c in (c for c in values.keys() if len(values[c]) == 1):
        v = values[c]
        remove_digits(values, peers[c], v)
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values,dplaces[0],digit)
    return values

def reduce_puzzle(values):
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Using the Eliminate Strategy
        eliminate(values)
        # Using the Only Choice Strategy
        only_choice(values)
        # Using the naked twins strategy
        naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values
    # Chose one of the unfilled square s with the fewest possibilities
    m = min({k: v for k, v in values.items() if len(v) > 1}.items(), key=lambda x: x[1])[0]
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for v in values[m]:
        t = values.copy()
        t[m] = v
        t = search(t)
        if t:
            return t

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # You can specify a puzzle as cmd line arg.
    # By default we assume, it's non diagonal.
    # Specify --diag as second arg if it's diagonal.
    if len(sys.argv) > 1:
        diag_sudoku_grid = str(sys.argv[1])
        assert(len(diag_sudoku_grid) == 81)
        unitlist = row_units + column_units + square_units

    vals = solve(diag_sudoku_grid)
    if vals == False:
        print("Puzzle can't be solved")
        sys.exit()

    display(vals)
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
