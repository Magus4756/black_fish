import csv
from io import StringIO
from urllib import request
import pandas as pd
from pandas.core.frame import DataFrame


class TierOne(object):
    ISBLACK = 1
    ISWHITE = 0
    UNKNOWN = -1
    NOTWHITE = -2
    NOTBLACK = 2

    def __init__(self, whitelist, blacklist):
        self.whitelist = whitelist
        self.blacklist = blacklist

    @staticmethod
    def _rabin_karp_matcher(T, P):
        n = len(T)
        m = len(P)
        h1 = hash(P)
        for s in range(0, n-m+1):
            h2 = hash(T[s:s+m])
            if h1 != h2:
                continue
            else:
                k = 0
                for i in range(0, m):
                    if T[s+i] != P[i]:
                        break
                    else:
                        k += 1
                if k == m:
                    return s
        return -1

    def white_match(self, url):
        """
        匹配白名单
        :param url: 匹配的URL
        :return: 返回ISWHITE或NOTWHITE
        """
        for w in self.whitelist:
            if self._rabin_karp_matcher(url, w) > 0:
                return self.ISWHITE
        return self.NOTWHITE

    def black_match(self, url):
        """
        匹配黑名单
        :param url: 匹配的URL
        :return: 返回ISBLACK或NOTBLACK
        """
        for b in self.blacklist:
            if self._rabin_karp_matcher(url, b) > 0:
                return self.ISBLACK
        return self.NOTBLACK

    def matchall(self, url, blackfirst=True):
        """
        匹配黑白名单
        :param url: 匹配的URL
        :param blackfirst: True:黑名单优先
                           False:白名单优先
        :return: 返回下列值之一：ISWHITE, ISBLACK, UNKNOWN
        """
        if blackfirst:
            res = self.black_match(url)
            if res == self.ISBLACK:
                return res
            res = self.white_match(url)
            if res == self.ISWHITE:
                return res
            else:
                return self.UNKNOWN
        else:
            res = self.white_match(url)
            if res == self.ISWHITE:
                return res
            res = self.black_match(url)
            if res == self.ISBLACK:
                return res
            else:
                return self.UNKNOWN

    @staticmethod
    def update_blacklist(
            url='http://data.phishtank.com/data/6dca0873b95d9009eb9abdc66cc576e24e69237ac5c70b532b2b3b62b5237a9b'
                '/online-valid.csv',
            save_path='data/blacklist.csv'):
        """
        从Phishtank上下载最新的黑名单
        :param url: Phishtank的csv文件
        :param save_path: 保存路径和文件名
        :return: 无
        """
        # 申请数据,连接即可返回黑名单的csv
        data = request.urlopen(url).read().decode('ascii', 'ignore')
        data_file = StringIO(data)
        blacklist = DataFrame(data_file)
        blacklist.to_csv(save_path, index=False)


if __name__ == '__main__':
    white = pd.read_csv('data/whitelist.csv')
    black = pd.read_csv('data/blacklist.csv')
    t1 = TierOne(whitelist=white['RDN'][:1000000], blacklist=black['URL'])
    print(t1.matchall(''))
