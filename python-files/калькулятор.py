while True:

    a = int(input("Введете 1 число"))
    b = int(input("Введете 2 число"))
    c = input("что делать - +")
    if (c == "-"):
        print(a-b)
    elif (c == "+"):
        print(a+b)
    elif (a == "выход"):
        break
    else:
        print("такой команды нет")
