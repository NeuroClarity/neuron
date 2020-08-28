import json
import csv

# read and load data
with open("sample_eye_data_2.txt") as f:
    data = json.load(f)

print(len(data))

results = []
count = 0
gap = (60 * 1000) / len(data) 
for index in range(len(data)):
    x = data[index]["X"]
    y = data[index]["Y"]
    if index != len(data) - 1:
        xn = data[index + 1]["X"]
        yn = data[index + 1]["Y"]
        func_x = lambda coord: ((xn - x) / gap) * coord + x
        func_y = lambda coord: ((yn - y) / gap) * coord + y
        for i in range(int(gap)):
            results.append([func_x(i), func_y(i), i + count])
    else:
        results.append([x, y, count])
    count += int(gap)

with open("interpolated_data_2.csv", "w+") as my_csv:
    csvWriter = csv.writer(my_csv,delimiter=' ')
    csvWriter.writerows(results)

print("finished writing results to csv")
