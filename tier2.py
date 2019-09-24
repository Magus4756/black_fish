# coding utf-8
# by CZL
"""URL训练与检测"""

import re
import math
import ssl
import time
from datetime import datetime
import threading
import pandas as pd
from lightgbm.sklearn import LGBMClassifier
from sklearn.externals import joblib
from SuspectedSet import SuspectedSet
from urllib import parse, request
from static import topHostPostfix, postfix_rate, charactor_frequency


class TierTwo:
    HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) "
               "AppleWebKit/600.5.17 (KHTML, like Gecko) Version/8.0.5 Safari/600.5.17"}
    _POSITIVE_THRESHOLD = 0.85
    _NEGATIVE_THRESHOLD = 0.01
    _TIMEOUT = 4
    ISWHITE = 0
    ISBLACK = 1
    UNKNOWN = 0.5
    rtime = None
    alexa_rk = None
    current_url = None

    def __init__(self):
        self.spt_set = SuspectedSet()
        try:
            self.model = joblib.load('model/LightGBM.pkl')
        except FileNotFoundError:
            print('模型不存在，正在生成……')
            self.model = LGBMClassifier(boosting_type='gbdt',
                                        learning_rate=0.1,
                                        n_estimators=100,
                                        subsample=0.9,
                                        colsample_bytree=0.7,
                                        objective='binary',
                                        random_state=10)
            data = pd.read_csv('data/train.csv')
            self.model_fit(data)
            joblib.dump(self.model, 'model.pkl')
            print('成功！')

    def url_predict_prob(self, url):
        """
        对给定的URL进行预测，顶级域名为IP的项将直接判为钓鱼网站
        :param url: 带预测的URL
        :return: 预测结果, 待处理的可疑词
        """
        urlv, other_top = self._get_urlv(url)
        preb = self.model.predict_proba([urlv])

        # 如果顶级域名为IP，视为钓鱼网站
        if urlv[1] == 1:
            preb = [0, 1]
        result = preb[0][1]
        spt_word = set()
        for i in other_top:
            spt_word.add(i[0])
        return result, spt_word

    def url_predict(self, url):
        r, w = self.url_predict_prob(url)
        if r < self._NEGATIVE_THRESHOLD:
            r = self.ISWHITE
        elif r >= self._POSITIVE_THRESHOLD:
            r = self.ISBLACK
        else:
            r = self.UNKNOWN
        return r, w

    def model_fit(self, data):
        """
        用已有参数训练模型
        :param data: 新数据
        :return: 无
        """
        col = data.columns.values.tolist()
        train_col = [x for x in col if x not in ['URL', 'label', 'filename']]
        train_data = data[train_col]
        label = data['label']

        self.model.fit(train_data, label)
        joblib.dump(self.model, 'model.pkl')

    def append_sus(self, word):
        self.spt_set.append(word)

    def _get_regtime(self, url):
        self.current_url = url
        # 得到RDN
        host = url.split('/')[2]
        extract_pattern = r'[^\.]+(?P<postfix>' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')$'
        pattern = re.compile(extract_pattern, re.IGNORECASE)
        rdn = pattern.search(host)
        rdn = rdn.group() if rdn else host

        url = 'http://whois.chinaz.com/' + rdn
        req = request.Request(url=url, headers=self.HEADERS)
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            res = request.urlopen(req, timeout=self._TIMEOUT)
            data = res.read().decode('utf-8')
        except:
            if self.current_url == url or self.current_url is None:
                self.rtime = 0
            return

        prog = re.compile(r'\d{4}年\d{2}月\d{2}日')
        dates = prog.findall(data)
        if not dates:
            self.rtime = 0
            return
        t = [int(dates[0][0:4]), int(dates[0][5:7]), int(dates[0][8:10])]
        regtime = datetime(t[0], t[1], t[2])
        d_regtime = datetime.now() - regtime
        d_regtime = d_regtime.days
        if d_regtime < 0:
            d_regtime = 1
        d_regtime = math.log(d_regtime + 1)
        if self.current_url == url or self.current_url is None:
            self.rtime = d_regtime

    def _alexa_rank(self, url):
        self.current_url = url

        host = url.split('/')[2]
        extract_pattern = r'[^\.]+(?P<postfix>' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')$'
        pattern = re.compile(extract_pattern, re.IGNORECASE)
        rdn = pattern.search(host)
        rdn = rdn.group() if rdn else host

        alexa_url = 'http://alexa.chinaz.com/' + rdn
        try:
            req = request.urlopen(alexa_url, timeout=self._TIMEOUT)
            data = req.read().decode('utf-8')
        except:
            if self.current_url == url or self.current_url is None:
                self.alexa_rk = 9999999999
            return
        rank_prog = re.compile(r'全球综合排名第<em> *(?P<rank>\d+) *</em>位。')
        search = rank_prog.search(data)
        try:
            if self.current_url == url or self.current_url is None:
                self.alexa_rk = int(search['rank'])
        except TypeError:
            if self.current_url == url or self.current_url is None:
                self.alexa_rk = 9999999999

    def get_alexarank(self, url):
        """
        取Alexa排名
        :param url:
        :return:
        """
        rank_thread = threading.Thread(target=self._alexa_rank, args=(url,), name='get_alexa_rank')
        rank_thread.start()

    def get_registtime(self, url):
        """
        取网站注册时间
        :param url:
        :return:
        """
        time_thread = threading.Thread(target=self._get_regtime, args=(url,), name='get_regist_time')
        time_thread.start()

    def _get_urlv(self, url):
        """
        生成URL特征向量
        :param url: 待提取的URL
        :return: URL向量, 其他顶级域名
        """
        url_v = {}
        scheme, netloc, path, params, query, fragment = parse.urlparse(url)

        # 分割netloc
        # 格式 user:password@host:port
        # 可用正则改写
        user = ''
        password = ''
        host = ''
        port = ''
        b_point = 0
        for i in range(len(netloc)):
            if netloc[i] == '@' and user == '':  # 用户名
                user = netloc[: i]
                b_point = i
            elif netloc[i] == ':' and len(netloc) - i > 4:  # 密码
                password = netloc[b_point + 1: i]
                b_point = i
            elif netloc[i] == ':' and len(netloc) - i <= 4:  # 域名&端口
                host = netloc[b_point + 1: i]
                port = netloc[i + 1:]
        if host == '':  # 端口不存在
            port = '80'
            if b_point != 0:
                host = netloc[b_point + 1:]
            else:
                host = netloc[b_point:]

        # 得到顶级域名，无法识别则返回host
        extract_pattern = r'[^\.]+(?P<postfix>' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')$'
        pattern = re.compile(extract_pattern, re.IGNORECASE)
        top = pattern.search(host)
        top_domain = top.group() if top else host
        rdn = top.group('postfix') if top else ''

        # 1. @
        self.at = url_v['@'] = 1 if user != '' else 0

        # 2. ip
        r = re.compile(r'\d+[\.]\d+[\.]\d+[\.]\d+')
        ip = r.findall(host)
        self.ip = url_v['ip'] = 1 if ip else 0

        # 3. unicode
        self.unicode = url_v['unicode'] = (netloc + path).count('%')

        # 4. 路径中的'.'
        self.dot = url_v['.'] = path.count('.')

        # 5. 其他品牌关键词
        url_v['suspect_word'] = 0
        word1 = host.split('.')
        word2 = re.split(r'\W+', path) if path else []
        spt_word = ''
        for w in word1 + word2:
            sim_rate, word = self.spt_set.max_similarity(w)
            if sim_rate > url_v['suspect_word']:
                url_v['suspect_word'] = sim_rate
                spt_word = word
        self.suspect_word = url_v['suspect_word']

        # 6. host & path 中的其他顶级域名个数
        top_domain_pattern = r'([^\.^/^(%\d{2})^?^=]+)(' + '|'.join([h.replace('.', r'\.') for h in topHostPostfix]) + ')\W'
        td_pattern = re.compile(top_domain_pattern, re.IGNORECASE)
        other_top = td_pattern.findall(url)
        url_v['other_top'] = len(other_top) - (1 - url_v['ip'])  # 去除IP
        if url_v['other_top'] < 0:
            url_v['other_top'] = 0
        self.other_top = url_v['other_top']

        other_top = [word[0] for word in other_top]
        try:
            top_domain = top_domain.split('.')[0]
            other_top.remove(top_domain)
        except:
            pass

        # 7. 端口
        self.port = url_v['port'] = 0 if port == '80' else 1

        # 8. 特殊字符
        self.special = url_v['special_ch'] = len(re.split(r'[+=%&#?!$*,;:]', path)) - 1

        # 9. '-'个数
        self.hyphen = url_v['-'] = path.count('-')

        # 10. '_'个数
        self.underline = url_v['_'] = path.count('_')

        # 11~36. 字母分布
        temp = url.lower()
        n = 0
        ch_distribute = [0 for _ in range(26)]
        for i in temp:
            if i.isalpha():
                ch_distribute[ord(i) - ord('a')] += 1
                n += 1
        dist_score = {}
        for i in range(26):
            try:
                value = ch_distribute[i] / n
            except:
                value = 0
            dist_score[chr(i+ord('a'))] = url_v[chr(i+ord('a'))] = abs(value - charactor_frequency[i - 11])
        self.charactor_distribute = dist_score

        # 37. 后缀分布
        if rdn in postfix_rate:
            url_v['postfix'] = postfix_rate[rdn]
        else:
            url_v['postfix'] = 0
        self.postfix = url_v['postfix']

        # 38. 域名长度
        self.netloc_length = url_v['netloc_length'] = len(netloc)

        # 39. 域名级数
        n = len(netloc.split('.'))
        self.netloc_level = url_v['netloc_level'] = n - url_v['ip'] * 3  # 去掉IP地址中的'.'

        # 40. 路径长度
        self.path_length = url_v['path_length'] = len(path)

        # 41. 路径级数
        if path:
            temp = path.split('/')
            if temp[-1] != '':  # path不以'/'结尾时
                url_v['path_level'] = len(temp) - 1
            else:
                url_v['path_level'] = len(temp) - 2
        else:
            url_v['path_level'] = 0
        self.pathlevel = url_v['path_level']

        # 42. 参数长度
        self.query_length = url_v['query_length'] = len(query)

        # 43. 参数个数
        if url_v['query_length'] == 0:
            url_v['query_num'] = 0
        else:
            url_v['query_num'] = len(query.split('&'))
        self.query_num = url_v['query_num']

        # 44. https
        if scheme == 'https':
            url_v['https'] = 1
        elif scheme == 'http':
            url_v['https'] = -1
        else:
            url_v['https'] = 0
        self.https = url_v['https']

        # 45.www
        t = host.split('.')[0]
        url_v['www'] = 1 if t == 'www' else 0
        self.www = url_v['www']

        # 46,47 注册时间，alexa排名
        if url_v['ip']:
            url_v['regtime'] = 0
            start = time.time()
            while self.alexa_rk is None and time.time() - start < self._TIMEOUT:
                pass
            url_v['alexa_rank'] = self.alexa_rk if self.alexa_rk else 9999999999
        else:
            start = time.time()
            while (self.rtime is None or self.alexa_rk is None) and time.time() - start < self._TIMEOUT:
                pass
            url_v['regtime'] = self.rtime if self.rtime else 0
            url_v['alexa_rank'] = self.alexa_rk if self.alexa_rk else 9999999999
        self.regist_time = url_v['regtime']
        self.alexa_rank = url_v['alexa_rank']
        self.rtime = None
        self.alexa_rk = None
        self.current_url = None

        # 输出为向量
        url_vector = []
        for k in url_v:
            url_vector.append(url_v[k])

        return url_vector, other_top


if __name__ == '__main__':
    url = 'http://baidu.jeetkunedo31.com/wp-admin/js/a/s/?kn=39'
    t2 = TierTwo()
    t2.get_registtime(url)
    t2.get_alexarank(url)

    result, other_top = t2.url_predict(url)

    t2.append_sus(other_top)

