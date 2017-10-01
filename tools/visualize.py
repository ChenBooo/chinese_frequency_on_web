"""输出出现频率最高的中文字符柱形图

输入：频率文件、输出数量
"""

import sys
import json
import matplotlib.pyplot as plt

#this is to fix the chinese display problem
plt.rcParams['font.sans-serif']=['SimHei']

def print_usage():
    print("visulize the chinese frequency information by histgram")
    print("USAGE:")
    print("      python visualize.py data.file number")
    print()
    print("data.file is the file that store chinese frequency information.")
    print("number is how many frequency chinese char you want to get.")
    sys.exit(0)

def main():
    if len(sys.argv) < 3:
        print_usage()

    file_name = sys.argv[1]
    number = int(sys.argv[2])
    
    with open(file_name, 'r') as fp:
        c_dic = json.load(fp)

    tmp = list(c_dic.items())
    tmp.sort(key=lambda x:x[1], reverse=True)

    if number > len(tmp):
        number = len(tmp)

    need = tmp[:number]
    value = [x[1] for x in need]
    label = [x[0] for x in need]

    plt.hist(range(number), bins=2*number-1, weights=value)
    plt.xticks(range(number), label)
    plt.show()

if __name__ == "__main__":
    main()
