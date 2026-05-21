#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""publish2lark.py — 将 AI 前沿早报发布到飞书知识库"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# 路径设置
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
_SECRETS_FILE = _PROJECT_ROOT / 'config' / 'secrets.json'


# 导入 WorkModule 基类
sys.path.insert(0, str(_PROJECT_ROOT / 'project-space'))
from utils.work_module import WorkModule


def run_lark_cli(cmd_args: list, capture_output: bool = True, input_text: Optional[str] = None) -> Optional[str]:
    """运行 lark-cli 命令，返回处理后的输出"""
    result = subprocess.run(['lark-cli'] + cmd_args, capture_output=capture_output, text=True, encoding='utf-8', input=input_text)
    if result.returncode != 0:
        return None
    output = result.stdout.strip()
    return output if output and output != 'null' else None


class LarkWikiPublisher(WorkModule):
    """飞书知识库发布器（继承自 WorkModule，复用日志和通用方法）"""
    
    # ==================== 配置模板 ====================
    CMD_NODE_LIST = ['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--page-all', '-q', '{query}']
    CMD_NODE_LIST_BY_PARENT = ['wiki', '+node-list', '--as', 'user', '--space-id', '{space_id}', '--parent-node-token', '{parent_token}', '--page-all', '-q', '{query}']
    CMD_NODE_CREATE = ['wiki', '+node-create', '--as', 'user', '--space-id', '{space_id}', '--obj-type', 'docx', '--title', '{title}', '-q', '.data.node_token']
    CMD_NODE_CREATE_WITH_PARENT = ['wiki', '+node-create', '--as', 'user', '--space-id', '{space_id}', '--title', '{title}', '--parent-node-token', '{parent_token}', '-q', '.data.node_token']
    CMD_NODE_MOVE = ['wiki', '+move', '--as', 'user', '--node-token', '{node_token}', '--target-parent-token', '{target_token}']
    CMD_DOC_UPDATE = ['docs', '+update', '--api-version', 'v1', '--as', 'user', '--doc', '{doc_token}', '--new-title', '{title}', '--mode', 'overwrite', '--markdown', '-']
    
    QUERY_NODE_BY_TITLE = '.data.nodes[] | select(.title == "{title}") | .node_token'
    QUERY_DUPLICATE_NODES = '[.data.nodes[] | select(.title | contains("{title_pattern}")) | .node_token]'
    
    def __init__(self, date: str):
        super().__init__('publish2lark')  # 调用父类初始化，设置模块名称
        self.date = date
        self.output_dir = _PROJECT_ROOT / 'output' / date
        self.briefing_file = self.output_dir / 'briefing.md'
        
        # 加载配置
        with open(_SECRETS_FILE, 'r', encoding='utf-8') as f:
            self.space_id = json.load(f)['feishu']['space_id']
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _find_or_create_node(self, title: str) -> Optional[str]:
        """查找或创建 wiki 节点"""
        query = self.QUERY_NODE_BY_TITLE.format(title=title)
        cmd = [arg.format(space_id=self.space_id, query=query) for arg in self.CMD_NODE_LIST]
        token = run_lark_cli(cmd)
        if token:
            return token
        cmd = [arg.format(space_id=self.space_id, title=title) for arg in self.CMD_NODE_CREATE]
        return run_lark_cli(cmd)
    
    def _find_or_create_month_folder(self) -> Optional[str]:
        """查找或创建月份文件夹"""
        month = self.date[:7]
        self.log(f"=== Step 1/5: 查找或创建月份文件夹 '{month}' ===")
        token = self._find_or_create_node(month)
        if token:
            self.log(f"月份文件夹 Token: {token}")
        return token
    
    def _check_output(self) -> bool:
        """检查早报文件"""
        self.log("=== Step 2/5: 检查输出文件 ===")
        if self.briefing_file.exists():
            size = self.briefing_file.stat().st_size
            lines = sum(1 for _ in open(self.briefing_file))
            self.log(f"找到早报文件: {self.briefing_file} (大小: {size} bytes, 行数: {lines})")
            return True
        self.log(f"早报文件不存在: {self.briefing_file}", level='ERROR')
        return False
    
    def _clean_duplicates(self, parent_token: str) -> None:
        """清理重复文档"""
        self.log("=== Step 3/5: 检查并清理已存在的当日早报 ===")
        title_pattern = f"AI 前沿早报（{self.date}）"
        query = self.QUERY_DUPLICATE_NODES.format(title_pattern=title_pattern)
        cmd = [arg.format(space_id=self.space_id, parent_token=parent_token, query=query) for arg in self.CMD_NODE_LIST_BY_PARENT]
        output = run_lark_cli(cmd)
        
        if not output:
            self.log("未找到已存在的早报文档，跳过清理")
            return
        
        try:
            nodes = json.loads(output)
        except json.JSONDecodeError:
            self.log("未找到已存在的早报文档，跳过清理")
            return
        
        if not isinstance(nodes, list) or len(nodes) == 0:
            self.log("未找到已存在的早报文档，跳过清理")
            return
        
        self.log(f"找到 {len(nodes)} 个重复文档，移入回收站...", level='WARNING')
        trash_token = self._find_or_create_node("回收站")
        if not trash_token:
            self.log("无法创建或找到回收站文件夹", level='ERROR')
            return
        
        self.log(f"回收站文件夹 Token: {trash_token}")
        moved = 0
        for token in nodes:
            if token and token != 'null':
                self.log(f"移动文档 {token} 至回收站...")
                cmd = [arg.format(node_token=token, target_token=trash_token) for arg in self.CMD_NODE_MOVE]
                if run_lark_cli(cmd):
                    moved += 1
        self.log(f"已将 {moved} 个旧文档移入回收站")
    
    def _publish(self, parent_token: str) -> Optional[str]:
        """发布早报文档"""
        self.log("=== Step 4/5: 创建并发布早报文档 ===")
        
        title = f"AI 前沿早报（{self.date}）"
        cmd = [arg.format(space_id=self.space_id, title=title, parent_token=parent_token) for arg in self.CMD_NODE_CREATE_WITH_PARENT]
        node_token = run_lark_cli(cmd)
        
        if not node_token:
            self.log("节点创建失败", level='ERROR')
            return None
        self.log(f"节点创建成功，Doc Token: {node_token}")
        
        self.log("开始写入文档内容...")
        with open(self.briefing_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        cmd = [arg.format(doc_token=node_token, title=title) for arg in self.CMD_DOC_UPDATE]
        if not run_lark_cli(cmd, capture_output=True, input_text=content):
            self.log("文档内容写入失败", level='ERROR')
            return None
        
        self.log("文档内容写入成功")
        url = f"https://my.feishu.cn/wiki/{node_token}"
        print(url)
        return url
    
    def run(self) -> int:
        """执行完整发布流程"""
        sep = "=" * 63
        self.log(sep)
        self.log("=== 开始发布 AI 前沿早报到飞书知识库 ===")
        self.log(f"发布日期: {self.date}")
        self.log(f"全量执行日志将保存至: {self._log_file}")
        self.log(sep)
        
        parent_token = self._find_or_create_month_folder()
        if not parent_token:
            self.log("无法创建或找到月份文件夹", level='ERROR')
            return 1
        self.log(f"目标目录: {self.date[:7]} (Token: {parent_token})")
        
        if not self._check_output():
            return 1
        
        self._clean_duplicates(parent_token)
        url = self._publish(parent_token)
        
        self.log("=== Step 5/5: 发布完成 ===")
        self.log(sep)
        if url:
            self.log(f"AI 前沿早报（{self.date}）已发布到飞书知识库")
            self.log(sep)
            return 0
        self.log("发布失败", level='ERROR')
        self.log(sep)
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description='将 AI 前沿早报发布到飞书知识库')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'), help='日期 (YYYY-MM-DD)')
    return LarkWikiPublisher(parser.parse_args().date).run()


if __name__ == '__main__':
    sys.exit(main())
