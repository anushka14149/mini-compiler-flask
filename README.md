# Mini Compiler + Garbage Collector Simulator

A simple web-based mini compiler and garbage collector simulator built with **Flask**.  
This app lets you enter multiple code expressions, tokenize them, build a parse tree, evaluate expressions, and simulate garbage collection with reference counting.

## Features

- Input multiple expressions separated by semicolons (`;`).
- Tokenizes numbers, identifiers, operators, and assignments.
- Builds and displays a basic parse tree for assignment statements.
- Evaluates arithmetic expressions involving variables and numbers.
- Maintains a symbol table showing variable values and reference counts.
- Simulates garbage collection by removing variables with zero references.
- Displays garbage collection logs for transparency.

## Getting Started

### Prerequisites

- Python 3.x
- Flask (`pip install flask`)

### Running the Application

1. Save the code into a file named `app.py`.
2. Open a terminal or command prompt in the directory containing `app.py`.
3. Run the Flask app:

   ```bash
   python app.py
