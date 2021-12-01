import pandas as pd

result = pd.read_csv("notebooks/result2.csv")



for i in range(0, len(result)):
    print("Reste" + str(len(result) - i))
    if (pd.isna(result["pertinence"][i])):
        print("-------")
        print("-------")
        print(result["review_clean"][i])
        print(" ")
        print(result["review_sentences"][i])
        print(" ")
        print(result["alias"][i])
        print("-------")
        print(result["sentence"][i])
        result["pertinence"][i] = input()
        result.to_csv("notebooks/result2.csv")
