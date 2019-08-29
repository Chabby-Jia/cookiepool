import time , requests , os
from io import BytesIO
from PIL import Image
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import listdir
from os.path import abspath, dirname
from selenium import webdriver
from login.verification import Verification





TEMPLATES_FOLDER = dirname(abspath(__file__)) + '/templates/'


class WeiboCookies():
    def __init__(self, username, password, browser,driver_service):   #
        self.url = 'https://passport.weibo.cn/signin/login?entry=mweibo&r=https://m.weibo.cn/'
        self.driver_service = driver_service
        self.driver_service.command_line_args()
        self.driver_service.start()

        self.browser =  browser
        self.wait = WebDriverWait(self.browser, 20)
        self.username = username
        self.password = password
    
    def open(self):
        """
        打开网页输入用户名密码并点击
        :return: None
        """
        self.browser.delete_all_cookies()
        self.browser.get(self.url)
        username = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.element_to_be_clickable((By.ID, 'loginAction')))
        username.send_keys(self.username)
        password.send_keys(self.password)
        time.sleep(1)
        submit.click()
    
    def password_error(self):
        """
        判断是否密码错误
        :return:
        """
        try:
            return WebDriverWait(self.browser, 5).until(
                EC.text_to_be_present_in_element((By.ID, 'errorMsg'), '用户名或密码错误'))
        except TimeoutException:
            return False
    
    def login_successfully(self):
        """
        判断是否登录成功
        :return:
        """
        try:
            return bool(
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'lite-iconf-profile'))))
        except TimeoutException:
            return False
    
    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        try:
            img = self.wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/div[1]/div/div[1]/div[1]/div/a/div[1]/div/canvas[1]')))

        except TimeoutException:
            print('未出现验证码')
            self.open()
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return (top, bottom, left, right)
    
    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot
    
    def get_image(self, name='captcha.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()
        print('验证码位置', top, bottom, left, right)
        screenshot = self.get_screenshot()
        captcha = screenshot.crop((left, top, right, bottom))
        return captcha
    
    def is_pixel_equal(self, image1, image2, x, y):
        """
        判断两个像素是否相同
        :param image1: 图片1
        :param image2: 图片2
        :param x: 位置x
        :param y: 位置y
        :return: 像素是否相同
        """
        # 取两个图片的像素点
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold = 20
        if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
            return True
        else:
            return False
    
    def same_image(self, image, template):
        """
        识别相似验证码
        :param image: 待识别验证码
        :param template: 模板
        :return:
        """
        # 相似度阈值
        threshold = 0.99
        count = 0
        for x in range(image.width):
            for y in range(image.height):
                # 判断像素是否相同
                if self.is_pixel_equal(image, template, x, y):
                    count += 1
        result = float(count) / (image.width * image.height)
        if result > threshold:
            print('成功匹配')
            return True
        return False
    
    def detect_image(self, image):
        """
        匹配图片
        :param image: 图片
        :return: 拖动顺序
        """
        for template_name in listdir(TEMPLATES_FOLDER):
            print('正在匹配', template_name)
            template = Image.open(TEMPLATES_FOLDER + template_name)
            if self.same_image(image, template):
                # 返回顺序
                numbers = [int(number) for number in list(template_name.split('.')[0])]
                print('拖动顺序', numbers)
                return numbers
    
    def move(self, numbers):
        """
        根据顺序拖动
        :param numbers:
        :return:
        """
        # 获得四个按点
        try:
            circles = self.browser.find_elements_by_css_selector('.patt-wrap .patt-circ')
            dx = dy = 0
            for index in range(4):
                circle = circles[numbers[index] - 1]
                # 如果是第一次循环
                if index == 0:
                    # 点击第一个按点
                    ActionChains(self.browser) \
                        .move_to_element_with_offset(circle, circle.size['width'] / 2, circle.size['height'] / 2) \
                        .click_and_hold().perform()
                else:
                    # 小幅移动次数
                    times = 30
                    # 拖动
                    for i in range(times):
                        ActionChains(self.browser).move_by_offset(dx / times, dy / times).perform()
                        time.sleep(1 / times)
                # 如果是最后一次循环
                if index == 3:
                    # 松开鼠标
                    ActionChains(self.browser).release().perform()
                else:
                    # 计算下一次偏移
                    dx = circles[numbers[index + 1] - 1].location['x'] - circle.location['x']
                    dy = circles[numbers[index + 1] - 1].location['y'] - circle.location['y']
        except:
            return False
    
    def get_cookies(self):
        """
        获取Cookies
        :return:
        """
        return self.browser.get_cookies()

    def coick_code(self):
        """
        获取点击验证码
        :return:
        """
        d_yanzhengma = self.wait.until(EC.presence_of_element_located((By.ID, 'show-message')))
        # 判断是否有点击验证码
        if d_yanzhengma:
            print('2找到')
            # 找寻点击按钮
            # 将鼠标移动到定位的元素上面等待
            # print('悬停等待3s')
            ActionChains(self.browser).move_to_element(d_yanzhengma).perform()

            time.sleep(3)

            d2_yanzhengma = self.wait.until(EC.presence_of_element_located((By.ID, 'embed-captcha')))
            # 鼠标摁着不放
            # print('摁着不放')
            ActionChains(self.browser).click_and_hold(d2_yanzhengma).perform()
            time.sleep(1)
            print('释放鼠标进入验证码界面')
            ActionChains(self.browser).release().perform()  # 释放鼠标，相当于点击该位置
            time.sleep(5)
            # print('保存图片')
            # self.browser.save_screenshot('jietu.png')

    def china_code(self):
        """
        获取文字点击验证码
        :return:
        """
        # 文字验证码
        try:
            w_img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_item_img')))
        except Exception as e :
            print(e)
            self.main()
        print('文字验证码搜索到')
        img_link = w_img.get_attribute('src')  # 获取验证码链接
        print(img_link)
        if img_link:
            target_img = Image.open(BytesIO(requests.get(img_link).content))  # 保存验证码图片
            target_img.save('wei.jpg')
            im = open('wei.jpg', 'rb').read()
            locations = Verification(im)  # 返回坐标字符串
            print(locations)
            for location in locations:
                ActionChains(self.browser).move_to_element_with_offset(w_img, location[0],
                                                                 location[1]).click().perform()
                time.sleep(1)
            submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip')))
            submit.click()

            time.sleep(5)

    def main(self):
        """
        破解入口
        :return:
        """
        self.open()
        if self.password_error():
            return {
                'status': 2,
                'content': '用户名或密码错误'
            }
        # 如果不需要验证码直接登录成功
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        #获取点击验证码
        dianji = self.coick_code()
        # 如果不需要验证码直接登录成功
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        #顺序点击文字验证码
        self.china_code()


        # 获取滑动验证码图片
        # image = self.get_image('captcha.png')
        # numbers = self.detect_image(image)
        # self.move(numbers)
        if self.login_successfully():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        else:
            return {
                'status': 3,
                'content': '登录失败'
            }


if __name__ == '__main__':
    result = WeiboCookies('username', 'passwd').main()
    print(result)
