"""
Cookie 管理与登录模块
"""
import os
import time
import logging


class CookieManager:
    """Cookie 管理器，支持本地文件读取和浏览器登录获取"""
    
    def __init__(self, cookie_file: str = 'cookie.txt'):
        """
        初始化 Cookie 管理器
        
        Args:
            cookie_file: Cookie 文件路径
        """
        self.cookie_file = cookie_file
        self._cookies = None
    
    def cookie_exists(self) -> bool:
        """检查本地 Cookie 文件是否存在"""
        return os.path.exists(self.cookie_file)
    
    def read_cookie(self) -> str:
        """
        读取 Cookie 文件内容
        
        Returns:
            Cookie 字符串
            
        Raises:
            FileNotFoundError: Cookie 文件不存在
        """
        if not self.cookie_exists():
            raise FileNotFoundError(f"未找到 {self.cookie_file}，请先登录获取 Cookie")
        
        with open(self.cookie_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    
    def parse_cookie(self) -> dict:
        """
        解析 Cookie 字符串为字典
        
        Returns:
            Cookie 字典
        """
        cookie_text = self.read_cookie()
        cookie_items = [item.strip().split('=', 1) for item in cookie_text.split(';') if item]
        return {k.strip(): v.strip() for k, v in cookie_items}
    
    def save_cookie(self, cookies: dict) -> None:
        """
        保存 Cookie 到文件
        
        Args:
            cookies: Cookie 字典
        """
        cookie_str = '; '.join([f'{k}={v}' for k, v in cookies.items()])
        with open(self.cookie_file, 'w', encoding='utf-8') as f:
            f.write(cookie_str)
        logging.info(f"Cookie 已保存到 {self.cookie_file}")
    
    def login_via_browser(self, timeout: int = 300) -> bool:
        """
        通过浏览器登录网易云音乐获取 Cookie
        
        使用 Selenium 打开浏览器，用户手动登录后自动获取 Cookie
        
        Args:
            timeout: 登录超时时间（秒），默认 5 分钟
            
        Returns:
            是否登录成功
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
        except ImportError:
            logging.error("请先安装 selenium: pip install selenium")
            raise ImportError("需要安装 selenium 库")
        
        logging.info("正在打开浏览器，请登录网易云音乐...")
        
        options = Options()
        # 不使用无头模式，让用户可以看到登录页面
        options.add_argument('--start-maximized')
        
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get("https://music.163.com/")
            
            start_time = time.time()
            logged_in = False
            
            # 等待用户登录，检测 MUSIC_U Cookie
            while time.time() - start_time < timeout:
                cookies = driver.get_cookies()
                cookie_dict = {c['name']: c['value'] for c in cookies}
                
                # MUSIC_U 是登录成功后的关键 Cookie
                if 'MUSIC_U' in cookie_dict and cookie_dict['MUSIC_U']:
                    logging.info("检测到登录成功！")
                    self.save_cookie(cookie_dict)
                    self._cookies = cookie_dict
                    logged_in = True
                    break
                
                time.sleep(2)
            
            if not logged_in:
                logging.warning("登录超时")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"浏览器登录失败：{str(e)}")
            return False
        finally:
            if driver:
                driver.quit()
    
    def get_cookies(self) -> dict:
        """
        获取 Cookie，优先从缓存获取
        
        Returns:
            Cookie 字典
        """
        if self._cookies:
            return self._cookies
        
        if self.cookie_exists():
            self._cookies = self.parse_cookie()
            return self._cookies
        
        raise FileNotFoundError("Cookie 不存在，请先登录")
    
    def clear_cache(self) -> None:
        """清除 Cookie 缓存"""
        self._cookies = None
    
    def delete_cookie_file(self) -> None:
        """删除本地 Cookie 文件"""
        if self.cookie_exists():
            os.remove(self.cookie_file)
            logging.info(f"已删除 {self.cookie_file}")
        self.clear_cache()
