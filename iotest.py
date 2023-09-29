import sys
from subprocess import Popen, PIPE
import re

def parse_copilot(filepath: str) -> tuple[list[list], list]:
    """
    Parses a text file that has Copilot generated tests. The file is of the following format:
    ```
    Test Case 1: Enter number: 5 Enter number 3: 6 Expected Output: stdout

    Test Case 2: Enter number 1: 10 Enter number 2: 2 Expected Output: stdout
    ```

    Args:
        filepath (str): The path to the file with Copilot generated tests.

    Returns:
        tuple[list[list], list]: A tuple containing a list of test cases, where each test case is a list of input values, and a list of expected outputs.
    """
    # Read the file and split it into lines
    with open(filepath, 'r') as f:
        lines = f.read().splitlines()

    inps: list = []
    outs: list = []
    for line in lines:
        # Find the input part of the line and add them to the inps list
        x = re.findall(r".*?(?=Output:)", line)
        if (len(x) != 0): inps.append(x[0])
        # Find the output part of the line and add them to the outs list
        y = re.findall(r"(?<=Output: ).*", line)
        if (len(y) != 0): outs.append(y[0])

    tests: list[list] = []
    for inp in inps:
        # Find all the test cases and add them to the tests list
        test = re.findall(r"(?<=: ).*?(?= )", inp)
        if (len(test) != 0): 
            test.pop(0)
            tests.append(test)

    return tests, outs


def run_program(program_path: str, input_data: list) -> str:
    """
    Runs the program being tested with the input values from a single test case and returns the output.

    Args:
        program_path (str): The path to the program to be executed.
        input_data (list): A list of input data to be passed to the program.

    Returns:
        str: A string representing the output of the program.
    """
    prog = Popen([program_path], stdin=PIPE, stdout=PIPE)
    
    inputs = '\n'.join(str(data) for data in input_data)
    stdout, stderr = prog.communicate(inputs.encode('utf-8'))

    out = stdout.decode('ascii').splitlines()
    return ' '.join(out)


def run_tests(program_path: str, tests: list[list], expected_outs: list,) -> None:
    """
    Runs all the tests using run_program() and compares the output of the program with the expected output for each test case.

    Args:
        program_path (str): The path to the program to be tested.
        tests (list[list]): A list of test cases, where each test case is a list of input values.
        expected_outs (list): A list of expected outputs.

    Returns:
        None
    """
    # Run the tests
    for i in range(len(tests)):
        # Get the output from the program
        out = run_program(program_path, tests[i])
        # Compare the output with the expected output
        if (expected_outs[i] in out):
            print(f'Test {i+1} passed')
        else:
            print(f'Test {i+1} failed')
            print(f'Expected: {expected_outs[i]}')
            print(f'Actual: {out}\n')

def main():
    """
    Reads command line arguments and calles other functions to run the tests.
    """

    # Parse the command line arguments
    if len(sys.argv) != 3:
        print("Usage: python iotest.py <program_path> <tests_path>")
        return
    program_path = sys.argv[1]
    tests_path = sys.argv[2]

    # Parse the Copilot generated tests
    tests, expected_outs = parse_copilot(tests_path)
    
    # Run the tests
    run_tests(program_path, tests, expected_outs)

main()