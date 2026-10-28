def main():
    try:
        n = int(input())
        if n <= 0:
            return

        square_dict = {i: i**2 for i in range(1, n+1)}
        print(square_dict)

    except ValueError:
        pass

if __name__ == "__main__":
    main()