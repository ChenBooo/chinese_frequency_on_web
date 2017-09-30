"""输出出现频率最高的中文字符

输入：频率文件、输出数量
"""
import sys
import json

def print_usage():
    print("USAGE:")
    print("      find_most.py data.file number")
    print()
    print("data.file is the file that store chinese frequency information.")
    print("number is how many frequency chinese char you want to get.")
    sys.exit(0)

def main():
    if len(sys.argv) < 3:
        print_usage()

    file_name = sys.argv[1]
    return_num = int(sys.argv[2])
    
    with open(file_name, 'r') as fp:
        c_dic = json.load(fp)

    tmp = list(c_dic.items())
    tmp.sort(key=lambda x:x[1], reverse=True)

    if return_num > len(tmp):
        return_num = len(tmp)

    for i in range(return_num):
        print(tmp[i])

if __name__ == "__main__":
    main()
