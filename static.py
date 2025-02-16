"""顶级域名和字母分布频率"""
topHostPostfix = ('.com', '.cn', '.la', '.io', '.co', '.info', '.net', '.org', '.me', '.mobi', '.us', '.biz',
                  '.xxx', '.ca', '.co.jp', '.com.cn', '.net.cn', '.org.cn', '.mx', '.tv', '.ws', '.ag', '.com.ag',
                  '.net.ag', '.org.ag', '.am', '.asia', '.at', '.be', '.com.br', '.net.br', '.bz', '.com.bz',
                  '.net.bz', '.cc', '.com.co', '.net.co', '.nom.co', '.de', '.es', '.com.es', '.nom.es', '.org.es',
                  '.eu', '.fm', '.fr', '.gs', '.in', '.co.in', '.firm.in', '.gen.in', '.ind.in', '.net.in',
                  '.org.in', '.it', '.jobs', '.jp', '.ms', '.com.mx', '.nl', '.nu', '.co.nz', '.net.nz', '.org.nz',
                  '.se', '.tc', '.tk', '.tw', '.com.tw', '.idv.tw', '.org.tw', '.hk', '.me.uk', '.org.uk', '.vg',
                  '.pl', '.fi', '.hu', '.ie', '.im', '.lv', '.cz', '.pro', '.bd', '.ru', '.ro', '.bm', '.hr',
                  '.global', '.kz', '.gen.tr', '.ch', '.edu.cn', '.edu', '.au', '.ac', '.app')

postfix_rate = {'.fm': -1.69897000433602, '.gen.tr': -1.69897000433602, '.xxx': -1.69897000433602, '.tw': -1.69897000433602,
           '.hr': -1.69897000433602, '.at': -1.69897000433602, '.edu.cn': -1.69897000433602, '.tv': -1.69897000433602,
           '.org.cn': -1.69897000433602, '.ch': -1.69897000433602, '.org.uk': -1.69897000433602, '.co.nz': -1.69897000433602,
           '.edu': -1.69897000433602, '.hk': -1.69897000433602, '.jp': -1.69897000433602, '.co.jp': -1.69897000433602,
           '.com.cn': -1.69897000433602, '.nl': -1.69897000433602, '.io': -1.02118929906994, '.de': -0.802974834108676,
           '.cn': -0.799340549453582, '.cz': -0.611014833980889, '.biz': -0.439332693830263, '.org': -0.408988677371077,
           '.se': -0.397940008672038, '.com.tw': -0.383216751851331, '.it': -0.37466866625905, '.net.cn': -0.367976785294594,
           '.fi': -0.342422680822206, '.ca': -0.310789832953137, '.be': -0.230448921378274, '.net': -0.133441142006115,
           '.fr': -0.0818213422138332, '.kz': -0.0669467896306132, '.pl': -0.0155121661782476,'.com': 0.0134237185707183,
           '.co.in': 0.0377885608893998, '.us': 0.0791812460476248, '.eu': 0.164810248645992,'.in': 0.211806811322216,
           '.info': 0.243734591709549, '.es': 0.24885198399891, '': 0.250272722723608, '.cc': 0.255272505103306,
           '.au': 0.269872013673594, '.hu': 0.301029995663981, '.ru': 0.335244096195083, '.pro': 0.359021942641668,
           '.ie': 0.394451680826216, '.co': 0.404570587571051, '.ro': 0.766412847112399, '.com.br': 0.768224087150632,
           '.me': 1.34242268082221, '.mobi': 1.69897000433602, '.lv': 1.69897000433602, '.ws': 1.69897000433602,
           '.com.mx': 1.69897000433602, '.bd': 1.69897000433602, '.tk': 1.69897000433602, '.mx': 1.69897000433602}

charactor_frequency = [0.056000441, 0.015464376, 0.055164668, 0.02347492, 0.06431696, 0.011197714, 0.020533441,
                       0.063697493, 0.047101794, 0.004412319, 0.011677628, 0.033032183, 0.04783763, 0.043844423,
                       0.073347494, 0.063634679, 0.001504562, 0.043476747, 0.048190911, 0.127590106, 0.022251679,
                       0.008497633, 0.093751538, 0.005021962, 0.010226673, 0.004789747]
