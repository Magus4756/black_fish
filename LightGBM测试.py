# coding utf-8
"""LightGBM系统调试"""

import pandas as pd
from pandas.core.frame import DataFrame
from lightgbm.sklearn import LGBMClassifier
from sklearn.grid_search import GridSearchCV
from sklearn import metrics
from sklearn.externals import joblib
import time

def load_data():
    x_names = ["Is_Txt", "Link_Per", "InnerLink_Num", "OutterLink_Num",
        "Form_Num", "GetForm_Num", "PostForm_Num", "Src_Safe", "Copyright",
        "Img_Safe", "Style_Safe", "Script_Safe", "FormSrc_Safe", "Tagtype",
        "Embed_Num", "Iframe_Num", "Applet_Num", "Frame_Num", "Img_Num",
        "InputBox_Num", "Password_Num", "Submit_Num", "Style_Num", "Script_Num",
        "Script_Len", "PopupWindow", "OnClick", "Function","LinkJudge",
        "HypLink","FormLink","Redirect","CSSLink_Num","Mail",
        "DivLink","CSSLink","InnerCSSLink"]

    white_data = pd.read_csv('before/UN.csv', error_bad_lines=False)
    black_data = pd.read_csv('before/UP.csv', error_bad_lines=False)
    white_x = white_data[x_names]
    white_y = white_data['label']
    black_x = black_data[x_names]
    black_y = black_data['label']

    #x_test = pd.concat([white_x, black_x])
    #y_values = pd.concat([white_y, black_y])
    x_test = pd.concat([white_x, black_x])
    y_values = pd.concat([white_y, black_y])

    return {'feature': x_names,
            'test_data': x_test,
            'test_label': y_values}

#LightGBM测试
def LGBM_judge(vector):
    if vector:
        print("GBDT载入中......")
        time1 = time.time()
        gb = joblib.load('model/LightGBM_model.pkl')
        del vector[0]
        vector_list = [vector]
        test_pre = gb.predict(vector_list)
        test_preb = gb.predict_proba(vector_list)
        time2 = time.time()
        #print("结果:")
        #print(test_pre)
        #print(test_preb)
        print("机器学习时间："+str(time2-time1))
        if test_pre == 1:
            return -1
        else:
            return 1
    else:
        print("向量提取失败")
        return

if __name__ == '__main__':
    data = load_data()
    scoring = 'recall'
    l_r = 0.1

    #"""# 默认参数训练

    """
    time1 = time.time()
    param_test1 = {'n_estimators': list(range(30, 51, 5))}
    gsearch1 = GridSearchCV(estimator=LGBMClassifier(boosting_type='gbdt',
                                                     learning_rate=l_r,
                                                     objective='binary',
                                                     random_state=10),
                            param_grid=param_test1,
                            scoring=scoring,
                            iid=False,
                            cv=3)
    gsearch1.fit(data['train_data'], data['train_label'])
    print(gsearch1.grid_scores_)
    print(gsearch1.best_params_)
    print(gsearch1.best_score_)
    print(time.time() - time1)
    n_e = gsearch1.best_params_['n_estimators']
    """
    n_e = 65
    """
    param_grid2 = {'num_leaves': [i for i in range(20, 51, 5)]}
    gsearch2 = GridSearchCV(estimator=LGBMClassifier(boosting_type='gbdt',
                                                     objective='binary',
                                                     n_estimators=n_e,
                                                     random_state=10),
                            param_grid=param_grid2,
                            scoring=scoring,
                            iid=False,
                            cv=3)
    gsearch2.fit(data['train_data'], data['train_label'])
    print(gsearch2.grid_scores_)
    print(gsearch2.best_params_)
    print(gsearch2.best_score_)
    print(time.time() - time1)
    num_leaves = gsearch2.best_params_['num_leaves']
    """
    num_leaves = 35
    """
    time1 = time.time()
    param_test3 = {'subsample': [i / 10.0 for i in range(6, 11)],
                   'colsample_bytree': [i/10.0 for i in range(6, 11)]}
    gsearch3 = GridSearchCV(estimator=LGBMClassifier(boosting_type='gbdt',
                                                     learning_rate=l_r,
                                                     n_estimators=n_e,
                                                     objective='binary',
                                                     random_state=10),
                            param_grid=param_test3,
                            scoring=scoring,
                            iid=False,
                            cv=3)
    gsearch3.fit(data['train_data'], data['train_label'])
    print(gsearch3.grid_scores_)
    print(gsearch3.best_params_)
    print(gsearch3.best_score_)
    print(time.time() - time1)
    ss = gsearch3.best_params_['subsample']
    c_b = gsearch3.best_params_['colsample_bytree']
    """
    ss = 0.6
    c_b = 0.6
    # """

    #"""# 调参后训练
    time1 = time.time()
    lgb = LGBMClassifier(boosting_type='gbdt',
                         learning_rate=l_r,
                         n_estimators=n_e,
                         num_leaves=num_leaves,
                         subsample=ss,
                         colsample_bytree=c_b,
                         objective='binary',
                         random_state=10)
    lgb = joblib.load('LightGBM_model.pkl')
    dtime1 = time.time() - time1

    # 预测测试集1
    time2 = time.time()
    test_pre = lgb.predict(data['test_data'])
    dtime2 = time.time() - time2
    test_preb = lgb.predict_proba(data['test_data'])
    acc = metrics.accuracy_score(data['test_label'], test_pre)
    t = [i[1] for i in test_preb]
    auc = metrics.roc_auc_score(data['test_label'], t)
    recall = metrics.recall_score(data['test_label'], test_pre)
    prec = metrics.precision_score(data['test_label'], test_pre)
    f1 = metrics.f1_score(data['test_label'], test_pre)
    print(lgb.get_params())
    print(lgb.feature_importances_)
    print('''train time: %d
    predict time: %d
    acc: %f
    auc: %f
    recall: %f
    precision: %f
    f1: %f''' % (dtime1, dtime2, acc, auc, recall, prec, f1))
    joblib.dump(lgb, 'LightGBM_model.pkl')

    pre_list = []
    for p in test_preb:
        if p[1] < 0.5:
            pre_list.append(0)
        else:
            pre_list.append(1)
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    print(len(pre_list))
    # """
    for i in range(0, 2062):
        if pre_list[i] == 1:
            fp += 1
        else:
            tn += 1
    for i in range(2062,len(pre_list)):
        if pre_list[i] == 0:
            fn += 1
        else:
            tp += 1
    print("tp:%d fp:%d tn:%d fn:%d" % (tp, fp, tn, fn))  # """



    # """