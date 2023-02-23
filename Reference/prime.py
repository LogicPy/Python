def find_primes(limit):
    # Create a list of booleans, initially set to True
    is_prime = [True] * (limit + 1)

    # Set 0 and 1 to not be prime
    is_prime[0] = False
    is_prime[1] = False

    # Iterate over the range of numbers up to the square root of the limit
    for i in range(2, int(limit ** 0.5) + 1):
        # If i is prime, mark all its multiples as not prime
        if is_prime[i]:
            for j in range(i**2, limit+1, i):
                is_prime[j] = False

    # Return a list of all prime numbers up to the limit
    return [i for i in range(2, limit+1) if is_prime[i]]

def show_if_prime():
    # Program to check if a number is prime or not
    global inp

    inp = input("Enter prime check: ")
    num = int(inp)
    # To take input from the user
    #num = int(input("Enter a number: "))

    # define a flag variable
    flag = False

    if num == 1:
        print(num, "is not a prime number")
    elif num > 1:
        # check for factors
        for i in range(2, num):
            if (num % i) == 0:
                # if factor is found, set flag to True
                flag = True
                # break out of loop
                break

        # check if flag is True
        if flag:
            print(num, "is not a prime number")
        else:
            print(num, "is a prime number")


while(True):
    # Input your command
    Input1 = input("Enter command for prime decision: ")
    # When selecting show list, call here.
    if (Input1 == "showlist.prime"):
        inp = input("Enter limit value: ")
        primes = find_primes(int(inp))
        print(primes)
    # Else if select is it prime, call here
    elif (Input1 == "isitprime"):
        show_if_prime()
    # Help display command
    elif (Input1 == "help"):
        print ("\n script commands are:\n\nshowlist.prime\nisitprime\n")


