import sys
import execjs
import base64
import ddddocr
import feapder
import argparse
import os
import configparser
import time
from tools import send_msg

# Pillow兼容性补丁
import pillow_compat

from env import *
from feapder.utils.log import log


class CQ(feapder.AirSpider):
    class InfoError(Exception):
        def __init__(self, *args, **kwargs):
            pass

    class CodeError(Exception):
        def __init__(self, *args, code='', code_result='', **kwargs):
            self.code = code
            self.code_result = code_result

    def start_requests(self):
        log.info("开始执行")
        log.info(f"用户名：{USERNAME}")
        self.send_msg("开始执行", level="INFO")
        code_url = "https://ids.gzist.edu.cn/lyuapServer/kaptcha"
        yield feapder.Request(url=code_url, callback=self.parse_tryLogin)

    def parse_tryLogin(self, request, response):
        login_url = "https://ids.gzist.edu.cn/lyuapServer/v1/tickets"
        try:
            uid = response.json["uid"]
            code_base64_str = response.json["content"].split(",")[-1]

            if code_base64_str == '-1':
                code_result = None
                code = None
            else:
                code, code_result = self.code_ocr(code_base64_str)
                log.info(f"验证码: {code};答案: {code_result}")

            post_data = {
                "username": USERNAME,
                "password": self.encrypt_password(PASSWORD),
                "service": "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do",
                "id": uid,
                "code": code_result
            }
            log.info(f"准备登录，参数: username={USERNAME}, id={uid}, code={code_result}")

            # 使用 feapder 发送登录请求
            try:
                login_response_obj = feapder.Request(url=login_url, data=post_data).get_response()
                login_response = login_response_obj.json
                log.info(f"登录响应状态码: {login_response_obj.status_code}")
                log.info(f"登录响应内容: {login_response}")
            except Exception as e:
                log.error(f"登录请求异常: {e}")
                raise

            # 处理登录响应
            try:
                params = {"ticket": login_response["ticket"]}
            except KeyError:
                data_code = login_response["data"]["code"]
                if data_code == 'NOUSER':
                    raise self.InfoError("用户名错误")
                elif data_code == 'PASSERROR':
                    raise self.InfoError("密码错误")
                elif data_code == 'CODEFALSE':
                    raise self.CodeError(f"验证码错误,尝试重新运行,{request.retry_times}", code=code,
                                         code_result=code_result)
                elif data_code == 'ISMODIFYPASS':
                    raise self.InfoError("密码未修改")
                elif data_code == 'ISPHONEOREMAILORANSWER':
                    raise self.InfoError("未绑定手机或邮箱或密保问题")
                raise KeyError(f"返回值未知,尝试重新运行: {data_code}")

            jump_url = "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/*default/index.do"
            yield feapder.Request(
                url=jump_url,
                callback=self.parse_getSelRoleConfig,
                params=params)

        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            log.error(f"parse_tryLogin发生错误: {e}")
            log.error(f"详细错误信息: {error_detail}")
            raise

    def parse_getSelRoleConfig(self, request, response):
        url = "https://xsfw.gzist.edu.cn/xsfw/sys/swpubapp/MobileCommon/getSelRoleConfig.do"
        cookies = response.cookies
        json = {
            "APPID": "5405362541914944",
            "APPNAME": "swmzncqapp"
        }
        yield feapder.Request(
            url,
            callback=self.parse_done,
            cookies=cookies,
            json=json)

    def parse_done(self, request, response):
        url = "https://xsfw.gzist.edu.cn/xsfw/sys/swmzncqapp/modules/studentCheckController/uniFormSignUp.do"
        cookies = response.cookies
        yield feapder.Request(
            url,
            callback=self.parse,
            cookies=cookies)

    def parse(self, request, response):
        try:
            result = response.json["msg"]
            if result == ' 当前时段不在考勤时段内':
                log.warning(f"::warning:: {result}")
                self.send_msg(result, "INFO")
                return
            elif result == ' 您已签到,请勿重复签到':
                pass
            log.info(fr"查寝结果：{result}")
            self.send_msg(result, "INFO")
        except Exception as e:
            log.error(f"::error:: 查寝失败，结果未知：{e}")

    def exception_request(self, request, response, e: Exception):
        if type(e) is self.InfoError:
            self.send_msg(f"{e}", "ERROR")
            self.stop_spider()
            # 注意：tools.delay_time 可能未导入，若报错请注释下一行
            # tools.delay_time(1)
        elif type(e) is self.CodeError:
            self.send_msg(f"验证码错误\n验证码:{e.code}\n答案:{e.code_result}", "ERROR")
        elif type(e) is KeyError:
            self.send_msg(f"返回值未知：{e}", "ERROR")
        elif type(e) is Exception:
            self.send_msg(f"发生未知错误：{e}", "ERROR")

        log.error(f"::error:: {e}")

    @staticmethod
    def send_msg(msg, level="DEBUG", message_prefix=""):
        msg = f"{USERNAME}\n{msg}"
        send_msg(msg, level=level, message_prefix=message_prefix)

    # 获取并识别验证码
    def code_ocr(self, code_base64_str):
        replace_str = {"o": "0", "O": "0", "l": "1", "i": "1", "I": "1", "s": "5", "S": "5", "b": "6", "B": "8"}
        ocr = ddddocr.DdddOcr()
        code = ocr.classification(self.base64_to_byte(code_base64_str))
        for key, value in replace_str.items():
            if key in code:
                code = code.replace(key, value)

        # 清理验证码字符串，只保留数字和运算符
        code_clean = ''.join([c for c in code if c.isdigit() or c in ['+', '-', '*', '/', '=']])

        # 计算验证码答案
        try:
            # 去掉最后的等号
            if code_clean.endswith('='):
                code_calc = code_clean[:-1]
                code_result = eval(code_calc)
            else:
                code_result = None
        except Exception as e:
            log.error(f"验证码计算错误: {code_clean}, 错误: {e}")
            code_result = None

        return code, code_result

    # 新的验证码获取和识别方式（备用方案）
    def get_and_ocr_captcha(self, save_dir=None):
        import requests
        from PIL import Image
        import os

        if not save_dir:
            save_dir = os.path.join(os.path.dirname(__file__), "captcha_images")
            os.makedirs(save_dir, exist_ok=True)

        # 获取验证码
        captcha_url = "https://jw.gzist.edu.cn/jwglxt/kaptcha?time=" + str(int(time.time() * 1000))
        resp = requests.get(url=captcha_url)

        # 获取当前目录下最大的数字编号
        existing_files = [f for f in os.listdir(save_dir) if f.endswith('.png') and f.split('.')[0].isdigit()]
        next_num = max([int(f.split('.')[0]) for f in existing_files]) + 1 if existing_files else 1

        # 保存验证码图片
        image_path = os.path.join(save_dir, f"{next_num}.png")
        with open(image_path, "wb") as f:
            f.write(resp.content)
        print(f"验证码图片已保存到: {image_path}")

        # 识别验证码
        ocr = ddddocr.DdddOcr()
        code = ocr.classification(resp.content)
        print(f"识别结果: {code}")
        return code, resp.content

    # base64字符串转二进制流
    @staticmethod
    def base64_to_byte(s):
        base64_byte = base64.b64decode(s)
        return base64_byte

    @staticmethod
    def js_from_file(file_name):
        with open(file_name, 'r', encoding='UTF-8') as file:
            result = file.read()
        return result

    def encrypt_password(self, password):
        try:
            # 使用 subprocess 调用 Node.js 进行加密
            import subprocess
            js_code = self.js_from_file('./login.js')
            test_script = js_code + "\nconsole.log(encrypt('" + password + "'));"

            result = subprocess.run(['node', '-e', test_script],
                                capture_output=True,
                                text=True,
                                encoding='utf-8')

            if result.returncode == 0:
                encrypted_password = result.stdout.strip()
                return encrypted_password
            else:
                raise Exception(f"Node.js加密错误: {result.stderr}")

        except Exception as e:
            log.error(f"Node.js加密失败，尝试使用明文密码: {e}")
            # 如果Node.js加密失败，返回原始密码
            return password


def get_username_password_from_env():
    username = os.environ.get("LOGIN_USERNAME")
    password = os.environ.get("LOGIN_PASSWORD")
    return username, password


def get_username_password_from_config(config_file, section):
    config = configparser.ConfigParser()
    config.read(config_file)
    if config.has_section(section):
        username = config.get(section, 'LOGIN_USERNAME')
        password = config.get(section, 'LOGIN_PASSWORD')
        return username, password
    else:
        return None, None


def get_username_password_manually():
    # 尝试从 login.ini 读取
    config = configparser.ConfigParser()
    config_file = 'login.ini'

    if os.path.exists(config_file):
        config.read(config_file)
        if config.has_section('loginInfo'):
            username = config.get('loginInfo', 'LOGIN_USERNAME')
            password = config.get('loginInfo', 'LOGIN_PASSWORD')
            if username and password:
                return username, password

    # 如果配置文件为空或不存在，提示用户输入
    print("首次运行，请配置账号密码")
    username = input("请输入学号: ").strip()
    password = input("请输入密码: ").strip()

    if not username or not password:
        log.error("账号或密码不能为空")
        return None, None

    # 保存到 login.ini
    if not config.has_section('loginInfo'):
        config.add_section('loginInfo')
    config.set('loginInfo', 'LOGIN_USERNAME', username)
    config.set('loginInfo', 'LOGIN_PASSWORD', password)

    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)

    log.info("账号密码已保存到 login.ini")
    return username, password


def get_username_password():
    parser = argparse.ArgumentParser(description='获取用户名和密码')
    parser.add_argument('-e', '--env', action='store_true', help='从环境变量中获取用户名和密码')
    parser.add_argument('-c', '--config', type=str, help='读取配置文件获取用户名和密码')
    parser.add_argument('-u', '--username', type=str, help='命令行输入用户名')
    parser.add_argument('-p', '--password', type=str, help='命令行输入密码')
    args = parser.parse_args()

    if args.env:
        set_setting_from_env()
        return get_username_password_from_env()
    elif args.config:
        set_setting_from_config(args.config, "setting")
        return get_username_password_from_config(args.config, 'loginInfo')
    elif args.username and args.password:
        return args.username, args.password
    else:
        return get_username_password_manually()


if __name__ == '__main__':
    USERNAME, PASSWORD = get_username_password()
    if USERNAME and PASSWORD:
        CQ().start()
    else:
        if not USERNAME:
            log.error("::error:: 账号不能为空")
        if not PASSWORD:
            log.error("::error:: 密码不能为空")
        sys.exit(1)