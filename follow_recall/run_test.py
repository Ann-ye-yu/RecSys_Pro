import unittest

from test_func import TestFunc
from html_test_runner import HTMLTestRunner


if __name__ == '__main__':
    # 1、创建测试套件
    suite = unittest.TestSuite()
    # 2、加载测试用例类
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestFunc))

    # 3、用HTMLTestRunner生成测试报告
    runner = HTMLTestRunner(stream=open("report.html", "wb"),  # 打开一个报告文件，将句柄传给stream
                            tester="zheng,zhao",  # 报告中显示的测试人员
                            description="基于关注学者召回测试报告",  # 报告中显示的描述信息
                            title="基于关注学者召回函数自动化测试")  # 报告的标题
    # 4、使用启动器去执行测试套件里的用例
    runner.run(suite)
