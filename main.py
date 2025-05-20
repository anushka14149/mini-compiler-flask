from flask import Flask, request, render_template_string
import re

app = Flask(__name__)

# HTML Template
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mini Compiler + GC Simulator</title>
</head>
<body style="font-family: Arial; background-color: #f4f4f4; padding: 20px;">
    <h2>Mini Compiler + Garbage Collector Simulator</h2>
    <form method="post">
        <label>Enter Code (multiple expressions separated by ;):</label><br>
        <input type="text" name="code" style="width: 600px;" value="{{code}}"/>
        <button type="submit">Run</button>
    </form>

    {% if tokens %}
        <h3>Token Stream:</h3>
        <pre>{{ tokens }}</pre>
    {% endif %}

    {% if parse_tree %}
        <h3>Parse Tree:</h3>
        <pre>{{ parse_tree }}</pre>
    {% endif %}

    {% if symbol_table %}
        <h3>Symbol Table:</h3>
        <table border="1" cellpadding="5">
            <tr><th>Variable</th><th>Value</th><th>Reference Count</th></tr>
            {% for var, info in symbol_table.items() %}
                <tr>
                    <td>{{ var }}</td>
                    <td>{{ info.value }}</td>
                    <td>{{ info.ref }}</td>
                </tr>
            {% endfor %}
        </table>
    {% endif %}

    {% if gc_log %}
        <h3>Garbage Collection Log:</h3>
        <pre>{{ gc_log }}</pre>
    {% endif %}
</body>
</html>
'''

# Global State
symbol_table = {}
ref_count = {}

# Tokenizer
def tokenize(code):
    token_spec = [
        ('NUMBER',     r'\d+'),
        ('IDENTIFIER', r'[a-zA-Z_]\w*'),
        ('ASSIGN',     r'='),
        ('OP',         r'[+\-*/]'),
        ('SEMI',       r';'),
        ('SKIP',       r'[ \t]+'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
    return [(m.lastgroup, m.group()) for m in re.finditer(tok_regex, code) if m.lastgroup != 'SKIP']

# Garbage Collector
def simulate_gc(var):
    logs = []
    if var in ref_count:
        ref_count[var] -= 1
        if ref_count[var] <= 0:
            logs.append(f"GC: Collected variable '{var}'")
            symbol_table.pop(var, None)
            ref_count.pop(var, None)
    return logs

# Parse statements
def split_statements(tokens):
    stmts = []
    curr = []
    for token in tokens:
        if token[0] == 'SEMI':
            if curr:
                stmts.append(curr)
                curr = []
        else:
            curr.append(token)
    if curr:
        stmts.append(curr)
    return stmts

# Parse tree generator
def build_parse_tree(stmts):
    tree = "PROGRAM\n"
    for stmt in stmts:
        if len(stmt) >= 5 and stmt[1][0] == 'ASSIGN':
            var = stmt[0][1]
            left = stmt[2][1]
            op = stmt[3][1]
            right = stmt[4][1]
            tree += f"""
  ASSIGN: {var} = {left} {op} {right}
           =
         /   \\
     {var}    {op}
           /     \\
        {left}   {right}
"""
        else:
            tree += "  Invalid or incomplete statement\n"
    return tree

# Evaluator
def evaluate_statement(stmt):
    if len(stmt) < 5:
        return None, []

    var = stmt[0][1]
    val1_token = stmt[2]
    op = stmt[3][1]
    val2_token = stmt[4]

    val1 = int(val1_token[1]) if val1_token[0] == 'NUMBER' else symbol_table.get(val1_token[1], 0)
    val2 = int(val2_token[1]) if val2_token[0] == 'NUMBER' else symbol_table.get(val2_token[1], 0)

    try:
        result = eval(f"{val1} {op} {val2}")
    except Exception as e:
        result = None

    gc_logs = []
    if var in symbol_table:
        gc_logs += simulate_gc(var)

    symbol_table[var] = result
    ref_count[var] = ref_count.get(var, 0) + 1

    return result, gc_logs

@app.route("/", methods=["GET", "POST"])
def index():
    tokens = []
    parse_tree = ""
    symbol_display = {}
    gc_log = []
    code = ""

    if request.method == "POST":
        code = request.form["code"]
        try:
            tokens = tokenize(code)
            stmts = split_statements(tokens)

            for stmt in stmts:
                _, logs = evaluate_statement(stmt)
                gc_log.extend(logs)

            parse_tree = build_parse_tree(stmts)

            symbol_display = {
                k: {"value": v, "ref": ref_count.get(k, 0)}
                for k, v in symbol_table.items()
            }

        except Exception as e:
            tokens = [("ERROR", str(e))]

    return render_template_string(HTML,
                                  code=code,
                                  tokens=tokens,
                                  parse_tree=parse_tree,
                                  symbol_table=symbol_display,
                                  gc_log="\n".join(gc_log) if gc_log else "No GC events.")


if __name__ == "__main__":
    app.run(debug=True)