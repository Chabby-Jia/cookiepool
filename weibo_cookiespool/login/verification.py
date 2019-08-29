from login.chaojiying_Python.chaojiying import Chaojiying_Client

USERNAME = ''
PASSWD = ''
UID = ''

chaojiying = Chaojiying_Client(USERNAME,PASSWD,UID,)

def Verification(im):
    """
    发送验证码坐标
    :return:
    """


    dic  = chaojiying.PostPic(im, '9004')
    print('dic')
    #判断返回是否报错
    if dic['err_no'] == 0 :
        coordinate = return_coordinate(dic['pic_str'])
        #[('276', '222'), ('275', '104'), ('220', '158'), ('552', '265')]
        return coordinate
    else:
        reporterror = chaojiying.ReportError(dic['pic_id'])
        if reporterror['err_no'] == 0:
            print('报错验证码已返回分值！')



def return_coordinate(codes):
    """
    处理后返回 x y 坐标元组
    :param codes: 字符串坐标  如  '276,222|275,104|220,158|552,265'
    :return:
    """
    groups = codes.split('|')
    locations = [[int(i) for i in group.split(',')] for group in groups]

    return locations
