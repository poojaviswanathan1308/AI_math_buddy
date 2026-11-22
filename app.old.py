
import streamlit as st
import sympy as sp
import re

st.set_page_config(
    page_title="AI Math Buddy",
    page_icon="📘"
)

st.title("📘 AI Math Buddy")

st.write(
    "Your Personal Mathematics Learning Assistant"
)

st.divider()

st.subheader("Enter Your Maths Problem")

question = st.text_input(
    "Type your equation",
    placeholder="Example: 2*x + 5 = 15"
)

if st.button("✨ Solve My Problem"):

    try:
        x = sp.Symbol("x")

        if question.count("=") != 1:
            raise ValueError("Enter one valid equation.")

        left, right = question.split("=")

        allowed = r"[0-9xX+\-*/().\s]+"

        if not re.fullmatch(allowed, left) or not re.fullmatch(allowed, right):
            raise ValueError("Use numbers, x and basic operators only.")

        lhs = sp.sympify(left, locals={"x": x})
        rhs = sp.sympify(right, locals={"x": x})

        equation = sp.expand(lhs - rhs)
        polynomial = sp.Poly(equation, x)

        if polynomial.degree() != 1:
            raise ValueError("Only linear equations are supported.")

        a = polynomial.coeff_monomial(x)
        b = polynomial.coeff_monomial(1)

        if a == 0:
            raise ValueError("No unique solution.")

        answer = sp.simplify(-b / a)

        st.success("Your problem is solved!")

        st.subheader("Final Answer")

        st.latex("x = " + sp.latex(answer))

        st.subheader("Step-by-Step Explanation")

        st.write("**Step 1: Given equation**")
        st.latex(sp.latex(lhs) + " = " + sp.latex(rhs))

        st.write("**Step 2: Simplify the equation**")
        st.latex(sp.latex(equation) + " = 0")

        st.write("**Step 3: Separate x**")
        st.latex(sp.latex(a*x) + " = " + sp.latex(-b))

        st.write("**Step 4: Calculate x**")
        st.latex("x = " + sp.latex(answer))

        check = sp.simplify(
            lhs.subs(x, answer) - rhs.subs(x, answer)
        )

        if check == 0:
            st.success("Answer verified successfully!")

    except Exception as error:
        st.error(str(error))

st.divider()

st.caption("AI Math Buddy | Learn Maths Step by Step")
