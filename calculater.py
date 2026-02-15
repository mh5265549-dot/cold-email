for i in range(5):
    print("Welcome to the calculator")
    a = (int(input("enter the first number")))
    b = (int(input("enter the second number")))
    operator = input("enter the operation (+,/,*,-):")
    if operator == "+":
        print ("the sum is a + b =", a + b) 
    elif operator == "-":
        print ("the difference is a - b =", a - b)
    elif operator == "*":
        print ("the product is a * b =", a * b)
    elif operator == "/":
        if b != 0:
            print ("the quotient is a/b =", a / b)
