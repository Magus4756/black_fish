
from local_feature_extration import get_pagevector
#from GBDT调参 import GBDT_judge
from LightGBM测试 import LGBM_judge
import time


# 页面检测
def page_detect(url):
    vector = None
    for i in range(2):
        try:
            vector = get_pagevector(url)
        except:
            pass
        else:
            break
    if vector:
        result = LGBM_judge(vector)
        return result
    else:
        return 1


if __name__ == '__main__':
    url_test = 'http://info-help.hol.es/help/aktivation-user-info.html'
    page_detect(url_test)