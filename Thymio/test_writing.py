import numpy as np

if __name__ == "__main__":
    # a = np.array([[1, 2], [3, 4]])
    # a = np.array([[5, 6], [7, 8]])
    # with open("test.txt", "ab") as file:
    #     np.save(file, a, False)

    with open('test.txt', 'rb') as f:
        a = np.load(f, allow_pickle=True)
        b = np.load(f, allow_pickle=True)
        print(a)
        print(b)