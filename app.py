import streamlit as st
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import ast
import math
import random
import re

st.set_page_config(
    page_title="AI Math Buddy",
    page_icon="📘",
    layout="wide"
)

# ---------- SAFE MATH FUNCTIONS ----------

FUNCTIONS = {
    "sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos,
    "tan": sp.tan, "log": sp.log, "exp": sp.exp,
    "abs": sp.Abs
}

NUMPY_FUNCTIONS = {
    "sqrt": np.sqrt, "sin": np.sin, "cos": np.cos,
    "tan": np.tan, "log": np.log, "exp": np.exp,
    "abs": np.abs
}

def convert_math(node, symbols):
    if isinstance(node, ast.Expression):
        return convert_math(node.body, symbols)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return sp.sympify(node.value)
    if isinstance(node, ast.Name):
        if node.id in symbols:
            return symbols[node.id]
        if node.id == "pi":
            return sp.pi
        if node.id == "e":
            return sp.E
        raise ValueError("Unknown variable: " + node.id)
    if isinstance(node, ast.BinOp):
        a = convert_math(node.left, symbols)
        b = convert_math(node.right, symbols)
        if isinstance(node.op, ast.Add): return a + b
        if isinstance(node.op, ast.Sub): return a - b
        if isinstance(node.op, ast.Mult): return a * b
        if isinstance(node.op, ast.Div): return a / b
        if isinstance(node.op, ast.Pow): return a ** b
    if isinstance(node, ast.UnaryOp):
        a = convert_math(node.operand, symbols)
        if isinstance(node.op, ast.USub): return -a
        if isinstance(node.op, ast.UAdd): return a
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        name = node.func.id
        if name in FUNCTIONS and len(node.args) == 1:
            return FUNCTIONS[name](convert_math(node.args[0], symbols))
    raise ValueError("Please enter a valid maths expression.")

def symbolic_expression(value, symbols):
    value = value.strip()
    tree = ast.parse(value.replace("^", "**"), mode="eval")
    return convert_math(tree, symbols)

def equation_expression(value, symbols):
    value = value.strip().replace("^", "**")

    value = re.sub(r'(\d)\s*([xy(])', r'\1*\2', value)
    value = re.sub(r'([xy])\s*\(', r'\1*(', value)
    value = re.sub(r'\)\s*([xy(])', r')*\1', value)

    tree = ast.parse(value, mode="eval")
    return convert_math(tree, symbols)
    
def numeric_expression(value):
    symbols = {"x": sp.Symbol("x")}
    result = symbolic_expression(value, symbols)
    if result.free_symbols:
        raise ValueError("Enter numbers only.")
    return float(result)

def graph_expression(node, x):
    if isinstance(node, ast.Expression):
        return graph_expression(node.body, x)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id == "x": return x
        if node.id == "pi": return np.pi
        if node.id == "e": return np.e
        raise ValueError("Use x, pi or e.")
    if isinstance(node, ast.BinOp):
        a = graph_expression(node.left, x)
        b = graph_expression(node.right, x)
        if isinstance(node.op, ast.Add): return a + b
        if isinstance(node.op, ast.Sub): return a - b
        if isinstance(node.op, ast.Mult): return a * b
        if isinstance(node.op, ast.Div): return a / b
        if isinstance(node.op, ast.Pow): return a ** b
    if isinstance(node, ast.UnaryOp):
        a = graph_expression(node.operand, x)
        if isinstance(node.op, ast.USub): return -a
        if isinstance(node.op, ast.UAdd): return a
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        name = node.func.id
        if name in NUMPY_FUNCTIONS and len(node.args) == 1:
            return NUMPY_FUNCTIONS[name](graph_expression(node.args[0], x))
    raise ValueError("Invalid graph expression.")

# ---------- SESSION PROGRESS ----------

if "solved" not in st.session_state:
    st.session_state.solved = 0
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = 0
if "quiz_done" not in st.session_state:
    st.session_state.quiz_done = 0

# ---------- SIDEBAR NAVIGATION ----------

st.sidebar.title("📘 AI Math Buddy")
page = st.sidebar.radio(
    "Choose a Page",
    [
        "🏠 Home Dashboard",
        "🧮 Maths Calculator",
        "✏️ Equation Solver",
        "📈 Graph Plotter",
        "🔢 Fractions & Percentage",
        "🎯 Daily Maths Quiz",
        "📝 Practice Zone",
        "📚 Formula Library",
        "📊 My Progress"
    ]
)

st.sidebar.caption("Learn Maths Step by Step")

# ---------- HOME DASHBOARD ----------

if page == "🏠 Home Dashboard":
    st.title("📘 Welcome to AI Math Buddy!")
    st.subheader("Your Personal Mathematics Learning Assistant")
    st.write("Learn, calculate, practise and improve your maths skills.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Problems solved", st.session_state.solved)
    c2.metric("Quiz attempts", st.session_state.quiz_done)
    c3.metric("Quiz score", st.session_state.quiz_score)

    st.divider()
    st.subheader("Explore Your Learning Tools")

    cards = [
        ("🧮 Calculator", "Solve basic calculations."),
        ("✏️ Equation Solver", "Solve algebra equations."),
        ("📈 Graph Plotter", "Visualise maths functions."),
        ("🔢 Fractions", "Calculate fractions and percentages."),
        ("🎯 Daily Quiz", "Test your maths knowledge."),
        ("📚 Formula Library", "Revise important formulas.")
    ]

    cols = st.columns(3)
    for i, (name, description) in enumerate(cards):
        with cols[i % 3]:
            st.info("**" + name + "**\n\n" + description)

    st.write("Choose any learning tool from the menu on the left.")

# ---------- CALCULATOR ----------

elif page == "🧮 Maths Calculator":
    st.title("🧮 Maths Calculator")
    st.write("Use +, -, *, /, brackets and powers.")
    question = st.text_input("Enter your calculation", "25 + 15 * 2")

    if st.button("Calculate"):
        try:
            answer = numeric_expression(question)
            st.success(f"Answer: {answer:g}")
        except Exception as error:
            st.error(str(error))

# ---------- EQUATION SOLVER ----------

elif page == "✏️ Equation Solver":
    st.title("✏️ Equation Solver")
    st.write("Examples: 2*x + 5 = 15 or x^2 - 5*x + 6 = 0")
    equation = st.text_input("Enter an equation", "2*x + 5 = 15")

    if st.button("Solve Equation"):
        try:
            if equation.count("=") != 1:
                raise ValueError("Enter one equation with one = sign.")
            left, right = equation.split("=")
            x, y = sp.symbols("x y")
            symbols = {"x": x, "y": y}
            lhs = equation_expression(left, symbols)
            rhs = equation_expression(right,symbols)
            result = sp.expand(lhs - rhs)
            variables = sorted(result.free_symbols, key=str)

            if not variables:
                st.write("This is a numerical statement.")
            elif len(variables) == 1:
                variable = variables[0]
                answer = sp.solve(result, variable)
                st.success("Solution")
                st.latex(sp.latex(variable) + " = " + sp.latex(answer))
                st.write("Simplified equation:")
                st.latex(sp.latex(result) + " = 0")
                st.write("Factorised form:")
                st.latex(sp.latex(sp.factor(result)) + " = 0")
                st.session_state.solved += 1
            elif len(variables) == 2:
                st.info("For simultaneous equations, enter both equations below.")
            else:
                st.error("This solver supports x and y only.")
        except Exception as error:
            st.error(str(error))

    st.divider()
    st.subheader("Simultaneous Equations")
    eq1 = st.text_input("First equation", "x + y = 10")
    eq2 = st.text_input("Second equation", "x - y = 2")

    if st.button("Solve Both Equations"):
        try:
            x, y = sp.symbols("x y")
            symbols = {"x": x, "y": y}
            answers = []
            for eq in [eq1, eq2]:
                if eq.count("=") != 1:
                    raise ValueError("Each equation needs one = sign.")
                a, b = eq.split("=")
                answers.append(
                    symbolic_expression(a, symbols) -
                    symbolic_expression(b, symbols)
                )
            result = sp.solve(answers, (x, y))
            st.success("Solution found")
            st.write(result)
            st.session_state.solved += 1
        except Exception as error:
            st.error(str(error))

# ---------- GRAPH PLOTTER ----------

elif page == "📈 Graph Plotter":
    st.title("📈 Graph Plotter")
    st.write("Enter a function using x. Example: x^2 or 2*x + 3")
    function = st.text_input("Function y =", "x**2")
    low = st.number_input("Minimum x", value=-10)
    high = st.number_input("Maximum x", value=10)

    if st.button("Draw Graph"):
        try:
            if low >= high:
                raise ValueError("Maximum x must be greater than minimum x.")
            x = np.linspace(low, high, 400)
            tree = ast.parse(function.replace("^", "**"), mode="eval")
            y = graph_expression(tree, x)
            y = np.broadcast_to(y, x.shape)
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.axhline(0)
            ax.axvline(0)
            ax.set_xlabel("x")
            ax.set_ylabel("y")
            ax.grid(True)
            st.pyplot(fig)
        except Exception as error:
            st.error(str(error))

# ---------- FRACTIONS AND PERCENTAGE ----------

elif page == "🔢 Fractions & Percentage":
    st.title("🔢 Fractions & Percentage")

    st.subheader("Fraction Calculator")
    a = st.text_input("First fraction", "1/2")
    b = st.text_input("Second fraction", "1/4")
    operation = st.selectbox("Operation", ["Add", "Subtract", "Multiply", "Divide"])

    if st.button("Calculate Fractions"):
        try:
            f1, f2 = sp.Rational(a), sp.Rational(b)
            if operation == "Add": answer = f1 + f2
            elif operation == "Subtract": answer = f1 - f2
            elif operation == "Multiply": answer = f1 * f2
            else: answer = f1 / f2
            st.success("Answer: " + str(answer))
        except Exception as error:
            st.error("Please enter valid fractions. " + str(error))

    st.divider()
    st.subheader("Percentage Calculator")
    number = st.number_input("Enter a number", value=200.0)
    percent = st.number_input("Enter percentage", value=10.0)

    if st.button("Find Percentage"):
        st.success(f"{percent}% of {number} = {number * percent / 100}")

    st.subheader("Ratio")
    r1 = st.number_input("First value", value=2, min_value=0)
    r2 = st.number_input("Second value", value=3, min_value=0)
    if st.button("Simplify Ratio"):
        if r1 == 0 and r2 == 0:
            st.error("Both values cannot be zero.")
        else:
            from math import gcd
            g = gcd(int(r1), int(r2))
            st.success(f"Simplified ratio: {int(r1)//g} : {int(r2)//g}")

# ---------- DAILY QUIZ ----------

elif page == "🎯 Daily Maths Quiz":
    st.title("🎯 Daily Maths Quiz")
    questions = [
        ("5 + 7 = ?", ["10", "12", "14", "15"], "12"),
        ("9 × 3 = ?", ["18", "21", "27", "30"], "27"),
        ("Square of 6?", ["12", "24", "36", "42"], "36"),
        ("50% of 80?", ["20", "30", "40", "50"], "40"),
        ("12 ÷ 4 = ?", ["2", "3", "4", "6"], "3")
    ]

    if "quiz_question" not in st.session_state:
        st.session_state.quiz_question = random.choice(questions)

    q = st.session_state.quiz_question
    st.subheader(q[0])
    choice = st.radio("Choose your answer", q[1], key="quiz_choice")

    if st.button("Check Answer"):
        if choice == q[2]:
            st.success("Correct! Well done.")
            st.session_state.quiz_score += 1
        else:
            st.info("Correct answer: " + q[2])
        st.session_state.quiz_done += 1

    if st.button("Next Question"):
        st.session_state.quiz_question = random.choice(questions)
        st.rerun()

# ---------- PRACTICE ZONE ----------

elif page == "📝 Practice Zone":
    st.title("📝 Practice Zone")
    topic = st.selectbox("Choose a topic", ["Addition", "Subtraction", "Multiplication", "Division"])
    if topic == "Addition":
        a, b, answer = 25, 15, 40
    elif topic == "Subtraction":
        a, b, answer = 50, 20, 30
    elif topic == "Multiplication":
        a, b, answer = 8, 7, 56
    else:
        a, b, answer = 48, 6, 8

    st.write(f"Solve: **{a} { {'Addition':'+','Subtraction':'-','Multiplication':'×','Division':'÷'}[topic] } {b}**")
    user_answer = st.number_input("Your answer", value=0)

    if st.button("Check My Answer"):
        if user_answer == answer:
            st.success("Correct! Great work.")
            st.session_state.solved += 1
        else:
            st.error("Not quite. Try again!")
            st.caption(f"Hint: Think about the {topic.lower()} operation.")

# ---------- FORMULA LIBRARY ----------

elif page == "📚 Formula Library":
    st.title("📚 Formula Library")
    topic = st.selectbox(
        "Choose a formula topic",
        ["Algebra", "Geometry", "Trigonometry", "Statistics", "Calculus"]
    )

    formulas = {
        "Algebra": [
            "a + b = b + a",
            "(a + b)² = a² + 2ab + b²",
            "a² - b² = (a-b)(a+b)"
        ],
        "Geometry": [
            "Rectangle Area = length × breadth",
            "Triangle Area = ½ × base × height",
            "Circle Area = πr²",
            "Circle Circumference = 2πr"
        ],
        "Trigonometry": [
            "sin²θ + cos²θ = 1",
            "tan θ = sin θ / cos θ",
            "sin 30° = 1/2"
        ],
        "Statistics": [
            "Mean = Sum of values / Number of values",
            "Range = Highest value - Lowest value"
        ],
        "Calculus": [
            "d(xⁿ)/dx = nxⁿ⁻¹",
            "∫xⁿ dx = xⁿ⁺¹/(n+1) + C (n ≠ -1)"
        ]
    }

    for formula in formulas[topic]:
        st.info(formula)

# ---------- MY PROGRESS ----------

elif page == "📊 My Progress":
    st.title("📊 My Learning Progress")
    st.metric("Problems solved", st.session_state.solved)
    st.metric("Quiz attempts", st.session_state.quiz_done)
    st.metric("Correct quiz answers", st.session_state.quiz_score)
    st.write("Keep practising to improve your maths skills!")

st.divider()
st.caption("AI Math Buddy | Learn Maths Step by Step")
