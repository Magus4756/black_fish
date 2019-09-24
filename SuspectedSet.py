# coding utf-8
# by CZL
"""可疑词库"""
from datetime import datetime


class Sptword:
    pass


class SuspectedSet:
    """
    关键词集
    """

    _unchangeable_set = []
    _spctset = []
    _capacity = 0
    _blacklist = ['www']

    # 初始化
    def __init__(self, capacity=1000, file_path='data'):
        """
        初始化
        :param capacity: 词库容量
        :return: 无
        """
        # print('正在读取……\n读取路径：%s\n动态词库最大容量：%d' % (file_path, capacity))

        self._capacity = capacity
        self.file_path = file_path
        n = 0
        f = open(file_path + '/unchangeable.csv', 'r')
        f.readline()
        for w in f.readlines():
            if n == self._capacity:
                f.close()
                break
            w = w.split(',')
            word = Sptword()
            word.data = w[0]
            t = w[1].split('-')
            word.time = datetime(int(t[0]), int(t[1]), int(t[2]))
            word.matched_times = int(w[2])
            self._unchangeable_set.append(word)
            n += 1
        f.close()

        f = open(file_path + '/spctset.csv', 'r')
        f.readline()
        for w in f.readlines():
            if n == self._capacity:
                f.close()
                break
            word = Sptword()
            w = w.split(',')
            word.data = w[0]
            t = w[1].split('-')
            word.time = datetime(int(t[0]), int(t[1]), int(t[2]))
            word.matched_times = int(w[2])
            self._spctset.append(word)
            n += 1
        f.close()

        # print('读取完成！\n静态词库容量：%d\n动态词库容量：%d\n动态词库最大容量：%d''' %
              # (len(self._unchangeable_set), len(self._spctset), self._capacity))


    def save_set(self):
        """
        保存数据
        :return:无
        """
        file_path = self.file_path
        # print('正在保存……\n保存路径：%s\n静态词库容量：%d\n动态词库容量：%d\n动态词库最大容量：%d''' %
              # (file_path, len(self._unchangeable_set), len(self._spctset), self._capacity))

        file1 = open(file_path + '/unchangeable.csv', 'w')
        file1.write('word,add_time,matched_times')
        for i in self._unchangeable_set:
            time = str(i.time).split(' ')[0]
            string = '\n' + i.data + ',' + time + ',' + str(i.matched_times)
            file1.write(string)
        file1.close()

        file2 = open(file_path + '/spctset.csv', 'w')
        file2.write('word,add_time,matched_times')
        for i in self._spctset:
            time = str(i.time).split(' ')[0]
            string = '\n' + i.data + ',' + time + ',' + str(i.matched_times)
            file2.write(string)
        file2.close()

        # print('\n保存完成！')

    @staticmethod
    def _editlength(x, y):
        """
        计算x与y的编辑距离
        :param x: 字符串A
        :param y: 字符串B
        :return: 编辑距离
        """
        edit = [[-1 for i in range(len(y) + 1)] for j in range(3)]
        for j in range(len(y) + 1):
            edit[0][j] = j
        for i in range(1, len(x) + 1):
            edit[i % 3][0] = edit[(i - 1) % 3][0] + 1
            for j in range(1, len(y) + 1):
                if x[i - 1] == y[j - 1]:
                    edit[i % 3][j] = min(min(edit[i % 3][j - 1] + 1, edit[(i - 1) % 3][j] + 1),
                                         edit[(i - 1) % 3][j - 1])
                else:
                    if i >= 2 and j >= 2 and x[i - 2] == y[j - 1] and x[i - 1] == y[j - 2]:
                        edit[i % 3][j] = min(min(edit[i % 3][j - 1] + 1, edit[(i - 1) % 3][j] + 1),
                                             min(edit[(i - 1) % 3][j - 1] + 1, edit[(i - 2) % 3][j - 2] + 1))
                    else:
                        edit[i % 3][j] = min(min(edit[i % 3][j - 1] + 1, edit[(i - 1) % 3][j] + 1),
                                             edit[(i - 1) % 3][j - 1] + 1)
        return edit[len(x) % 3][len(y)]

    def _findlast(self):
        """
        找到词库中最不活跃的词
        :return: 词的位置
        """
        # 返回最后一项
        return len(self._spctset) - 1

    def append(self, word_list):
        """
        添加新项
        :param word_list: 添加项列表
        :return: 无
        """
        if isinstance(word_list, list) or isinstance(word_list, set):
            for word in word_list:
                self.append(word)

        elif isinstance(word_list, str) is True:
            word = word_list
            # 若在黑名单
            if word in self._blacklist:
                return
            # 查重
            for i in range(len(self._spctset)):
                # 若已经包含该词
                if self._spctset[i].data == word:
                    temp = self._spctset[i]
                    temp.matched_times += 1
                    del self._spctset[i]
                    self._spctset.insert(0, temp)
                    return

            for i in self._unchangeable_set:
                if i.data == word:
                    temp = self._unchangeable_set[i]
                    temp.matched_times += 1
                    del self._unchangeable_set[i]
                    self._unchangeable_set.insert(0, temp)
                    return

            # 如果词库满,则删除一项
            if len(self._spctset) == self._capacity:
                i = self._findlast()
                del self._spctset[i]

            # 添加新项
            w = Sptword()
            w.data = word
            w.time = datetime.now()
            w.matched_times = 1
            self._spctset.insert(0, w)

            self.save_set()

    def _match(self, string):
        """
        匹配str与词库中每个词的相似度
        :param string: 待匹配的字符串
        :return: 相似度列表
        """

        similarity_list = []

        # 匹配静态词库
        for i in self._unchangeable_set:
            editlen = self._editlength(string, i.data)
            similarity = len(string) / (len(string) + editlen)
            w = [similarity, i.data]
            similarity_list.append(w)

        # 匹配动态词库
        for i in self._spctset:
            editlen = self._editlength(string, i.data)
            similarity = len(string) / (len(string) + editlen)
            w = [similarity, i.data]
            similarity_list.append(w)
        return similarity_list

    def max_similarity(self, string):
        """
        统计词库中所有词与string的相似度的最大值
        :param string: 待匹配词
        :return: [相似度, 最相似的词]
        """
        similarity_list = self._match(string)
        w = similarity_list[0]
        for i in similarity_list:
            if i[0] > w[0]:
                w = i
        return w

    def morethan(self, string, threshold=0, num=0):
        """
        找到与str相似度大于等于threshold的所有词
        :param string: 待匹配字符串
        :param threshold: 相似度阈值
        :param num: 所需个数
        :return: 相似度大于等于f的关键词列表
        """
        similarity = self._match(string)
        similarity_list = []
        for i in similarity:
            if i[0] >= threshold:
                similarity_list.append(i)
        if num == 0:
            return similarity_list
        else:
            similarity_list.sort(reverse=True)
            return similarity_list[:num]


if __name__ == '__main__':
    s = SuspectedSet()
