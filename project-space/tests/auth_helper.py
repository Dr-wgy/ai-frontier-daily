#!/usr/bin/env python3
"""飞书 OAuth 授权助手

用于获取第一个 user_access_token 和 refresh_token。
支持自动从浏览器重定向中获取 code。
"""

import sys
import traceback
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# 设置正确的 Python 路径
project_space = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_space))

# 用于存储获取到的 code
received_code = None
auth_server = None

class AuthCallbackHandler(BaseHTTPRequestHandler):
    """处理飞书授权回调的 HTTP 处理器"""
    
    def do_GET(self):
        global received_code
        
        # 解析 URL 中的 code 参数
        if '?code=' in self.path:
            code = self.path.split('?code=')[1].split('&')[0]
            received_code = code
            
            # 返回成功页面
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write("<html><body><h1>授权成功！</h1><p>code 已获取，您可以关闭此页面并返回终端。</p></body></html>".encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write("<html><body><h1>错误：未找到 code 参数</h1></body></html>".encode('utf-8'))
    
    def log_message(self, format, *args):
        """禁用日志输出"""
        pass

def start_auth_server(port=8080):
    """启动授权回调服务器"""
    global auth_server
    server_address = ('127.0.0.1', port)
    auth_server = HTTPServer(server_address, AuthCallbackHandler)
    server_thread = threading.Thread(target=auth_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    return auth_server

def stop_auth_server():
    """停止授权回调服务器"""
    global auth_server
    if auth_server:
        auth_server.shutdown()

def main():
    global received_code
    
    try:
        from utils.lark_sdk_commander import LarkClient
    except ImportError as e:
        print(f"错误: 无法导入 LarkClient")
        print(f"  导入错误详情: {e}")
        print(f"  当前工作目录: {Path.cwd()}")
        print(f"  project_space 路径: {project_space}")
        print(f"  utils 目录存在: {(project_space / 'utils').exists()}")
        print(f"  lark_sdk_commander.py 存在: {(project_space / 'utils' / 'lark_sdk_commander.py').exists()}")
        print("\n请确保运行方式正确:")
        print(f"  cd {project_space}")
        print(f"  python tests/auth_helper.py")
        return

    client = LarkClient()
    
    print("=" * 60)
    print("飞书 OAuth 授权助手")
    print("=" * 60)
    
    # 1. 获取配置的端口号
    redirect_port = client.get_redirect_port()
    
    # 2. 启动本地回调服务器
    print(f"\n步骤 1: 启动本地授权回调服务器...")
    start_auth_server(redirect_port)
    print(f"✓ 服务器已启动: http://127.0.0.1:{redirect_port}")
    
    # 2. 生成授权 URL
    auth_url = client.get_auth_url()
    print(f"\n步骤 2: 正在打开授权页面...")
    print(f"授权成功后，页面会跳转到 http://127.0.0.1:{redirect_port}/?code=xxxx")
    print("-" * 60)
    print(auth_url)
    print("-" * 60)
    
    # 3. 自动打开浏览器
    webbrowser.open(auth_url)
    print("\n请在浏览器中完成授权操作...")
    
    # 4. 等待获取 code
    print("等待获取授权 code...", end="", flush=True)
    while received_code is None:
        import time
        time.sleep(0.5)
        print(".", end="", flush=True)
    
    print("\n\n✓ 成功获取到 code！")
    
    # 5. 停止服务器
    stop_auth_server()
    
    # 6. 换取 Token
    print("\n步骤 3: 正在换取 Access Token...")
    success = client.init_with_code(received_code)
    
    if success:
        print("\n" + "=" * 60)
        print("✓ 初始化成功！自动刷新功能已激活。")
        print("以后运行脚本时，程序会自动管理 Token 续期。")
        print("=" * 60)
    else:
        print("\n✗ 初始化失败，请检查 app_id 和 app_secret 是否正确。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_auth_server()
        print("\n操作已取消。")