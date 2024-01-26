import hashlib
import math
import random
import matplotlib.pyplot as plt


class CountingBloomFilter(object):
    def __init__(self, element_num, false_positive_rate):
        self.element_num = element_num  # n
        self.false_positive_rate = false_positive_rate  # p
        self.generate_parameters()
        self.initialize_bloom_filter()

    def generate_parameters(self):
        # 计算比特数组的长度和哈希函数的数量
        self.length = math.ceil(-(self.element_num * math.log(self.false_positive_rate)) / (math.log(2) ** 2))  # m
        self.hash_num = math.ceil((self.length / self.element_num) * math.log(2))  # k

    def initialize_bloom_filter(self):
        # 每个计数器用4位（半字节）表示
        self.counting_bf = bytearray(b'\x00' * (math.ceil(self.length / 2)))

    def add_to_bloom_filter(self, value):
        for i in range(self.hash_num):
            location = self.short_hash(value, i + 1)
            self.increment_counter(location) # 将计数器加1（4位）
            # print("第",i,"个Hash映射后的计数 Bloom Filter:", list(self.counting_bf))

        # 在添加值后打印当前状态的计数 Bloom Filter
        # print("添加", value, "后的计数 Bloom Filter:", list(self.counting_bf))

    def short_hash(self, value, seed):
        sha1 = hashlib.sha1()
        sha1.update(f"{value}{seed}".encode('utf-8'))
        hashed_value = int(sha1.hexdigest(), 16)  # 获取SHA1哈希对象的十六进制表示的哈希值，转化成整数,与seed相乘增加随机性和分散性
        return hashed_value % self.length

    def increment_counter(self, location):
        # 每个计数器用4位（半字节）表示
        nibble_index = location // 2
        bit_shift = (location % 2) * 4  # 偏移位数
        # print("Index为:",nibble_index,"偏移量为:",bit_shift)
        counter_value = (self.counting_bf[nibble_index] >> bit_shift) & 0xF
        if counter_value < 15:
            # 将计数器加1
            self.counting_bf[nibble_index] += 1 << bit_shift
        else:
            # 计数器溢出，将其固定在15
            self.counting_bf[nibble_index] |= 0xF << bit_shift

    def delete(self, value):
        if self.lookup(value):
            for i in range(self.hash_num):
                location = self.short_hash(value, i + 1)
                # 将计数器减1（4位）
                self.decrement_counter(location)
            # print(">>删除成功")
            return True
        else:
            # print(">>错误：元素不在 Bloom Filter 中")
            return False

    def decrement_counter(self, location):
        # 每个计数器用4位（半字节）表示
        nibble_index = location // 2
        bit_shift = (location % 2) * 4
        counter_value = (self.counting_bf[nibble_index] >> bit_shift) & 0xF
        if counter_value > 1:
            # 将计数器减1
            self.counting_bf[nibble_index] -= 1 << bit_shift
        else:
            # 计数器下溢，将其固定在1
            self.counting_bf[nibble_index] |= (0x1 << bit_shift)

    def lookup(self, value):
        minnum = float('inf')  # 初始值设为正无穷大
        for i in range(self.hash_num):
            location = self.short_hash(value, i + 1)
            counter_value = (self.counting_bf[location // 2] >> ((location % 2) * 4)) & 0xF
            if counter_value > 0:
                minnum = min(counter_value, minnum)
            else:
                # print(">>未找到", str(value))
                return 0
        # print(">>找到", str(value))
        return minnum


def generate_random_data(size):
    return [random.randint(1, 1000000) for _ in range(size)]


# def generate_skewed_data(size, skewed_factor):
#     data = []
#     skewed_elements=[]
#     for _ in range(int(size*0.2)):
#         skewed_elements.append(random.randint(1,1000000))
#     for _ in range(size):
#         if random.random() < skewed_factor:
#             # Add a skewed element
#             data.append(random.choice(skewed_elements))
#         else:
#             # Add a random element
#             data.append(random.randint(1, 1000000))
#     return data

def test_counting_bloom_filter(dataset_size, perror=0.001, insert_dataset_size=50000):
    resultes = []

    counting_bf = CountingBloomFilter(dataset_size, perror)
    # Output Bloom Filter parameters
    print("-----------------------------------")
    print("n=", counting_bf.element_num)
    print("p=", counting_bf.false_positive_rate)
    print("m=", counting_bf.length)
    print("k=", counting_bf.hash_num)

    # Generate random data
    data = generate_random_data(dataset_size)
    # Generate skewed data
    # data = generate_skewed_data(size, 0.8)

    # Insert data 同时插入CBF和字典
    element_count = {}  # 字典，存储插入的数字及其对应的次数

    # 插入更多的数据
    amount_number = 0
    for i in range(0, insert_dataset_size, 100):  # step = 100
        data = generate_random_data(1)
        for element in data:
            counting_bf.add_to_bloom_filter(element)
            if element in element_count:
                element_count[element] += 1
            else:
                element_count[element] = 1

        # Evaluate accuracy
        amount_number += 100  # +=step
        correct_count = 0
        for element in element_count:
            if counting_bf.lookup(element) == element_count[element]:
                correct_count += 1
        accuracy = correct_count / amount_number
        print(amount_number, f"False Positive rate: {(1 - accuracy) * 100:.4f}%\n")
        resultes.append((amount_number, 1 - accuracy))

    return resultes


def if_is_full(CBF):
    n = 0
    for i in range(CBF.length // 2):
        if CBF.counting_bf[i] == 0xFF:
            # print(CBF.counting_bf[i])
            n += 1
            # return False
    if CBF.length % 2 == 1:
        if (CBF.counting_bf[math.ceil(CBF.length / 2)] >> 4) == 0xF:
            # print(CBF.counting_bf[math.ceil(counting_bf.length/2)]>>4)
            # return False
            n += 1
    #     retun True
    print(n)


def main():
    dataset_sizes_to_test = 10000  # 要测试的数据集大小,初始的n值
    acceptable_flase_positive_rate = 0.001  # 可接受的假阳率，p值
    insert_dataset_size = 10783  # 要插入的数据量

    experiment_results = test_counting_bloom_filter(dataset_sizes_to_test, acceptable_flase_positive_rate,
                                                    insert_dataset_size)

    # Plot the results
    sizes, errors = zip(*experiment_results)
    print(sizes, errors)
    plt.plot(sizes, errors, marker='o', linestyle='-', color='r')
    plt.title("Counting Bloom Filter Performance")
    plt.xlabel("Dataset Size")
    plt.ylabel("Fasle Positive Rate")
    # plt.xscale('log')  # Set x-axis to logarithmic scale for better visualization
    plt.grid(True)
    plt.show()


if __name__ == '__main__':
    main()
