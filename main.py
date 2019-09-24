# coding: utf-8
# phish detecting system

import time
import pandas as pd
from tier1 import TierOne
from tier2 import TierTwo
from page_detect import page_detect


def main():
    # 读取黑白名单
    whitelist = pd.read_csv('data/whitelist.csv')[:1000000]
    blacklist = pd.read_csv('data/blacklist.csv')

    # 初始化黑白名单层和URL检测层
    tier1 = TierOne(whitelist=whitelist['RDN'], blacklist=blacklist['URL'])
    tier2 = TierTwo()

    # 读取测试数据
    test = pd.read_csv('data/test.csv')

    tier1time = []
    tier2time = []
    tier3time = []
    result = []
    i = 0
    for url in test['URL']:
        i += 1
        print('\n', i, url, end=' ')

        t = time.time()
        # 黑白名单检测
        result1 = tier1.matchall(url)
        print(result1, end=' ')
        tier1time.append(time.time() - t)
        if result1 != tier1.UNKNOWN:
            tier2time.append(0)
            tier3time.append(0)
            result.append(result1)
            continue

        t = time.time()
        # URL检测
        tier2.get_registtime(url)
        tier2.get_alexarank(url)
        result2, other_top = tier2.url_predict(url)
        print(result2, end=' ')
        tier2time.append(time.time() - t)

        if result2 != tier2.UNKNOWN:
            if result2 == 1:
                tier2.append_sus(other_top)

            tier3time.append(0)
            result.append(result2)
            continue

        t = time.time()
        # 页面检测
        result3 = page_detect(url)
        if result3 == 1:
            tier2.append_sus(other_top)

        tier3time.append(time.time() - t)
        result.append(result3)
        print(result3, end=' ')

    test.insert(1, 'result', result)
    test.insert(2, 'tier1time', tier1time)
    test.insert(3, 'tier2time', tier2time)
    test.insert(4, 'tier3time', tier3time)
    test.to_csv('result.csv', index=False)


if __name__ == '__main__':
    main()
