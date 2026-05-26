#!/usr/bin/env node
/**
 * screenshot-redbook.js — 小红书卡片批量截图
 * 
 * 用法: node screenshot-redbook.js [date]
 *   date: 日期，格式 YYYY-MM-DD，默认今天
 * 
 * 输入: output/{date}/redbook/*.html
 * 输出: output/{date}/redbook-png/*.png
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ============ Logger — 写入 output/{date}/run.log，格式与 Python 端对齐 ============
class Logger {
  static NAME = 'screenshot-redbook';

  constructor(date) {
    const logDir = path.resolve(__dirname, '..', 'output', date);
    fs.mkdirSync(logDir, { recursive: true });
    this._logFile = path.join(logDir, 'run.log');
  }

  _write(level, msg) {
    const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
    const line = `${ts} - ${Logger.NAME} - ${level.padEnd(8)} - ${msg}\n`;
    fs.appendFileSync(this._logFile, line, 'utf-8');
  }

  info(msg)    { console.log(msg);   this._write('INFO', msg); }
  warning(msg) { console.warn(msg);  this._write('WARNING', msg); }
  error(msg)   { console.error(msg); this._write('ERROR', msg); }
}

// ============ BrowserSession — 封装 agent-browser CLI 客户端 ============
class BrowserSession {
  static CLI = 'agent-browser';

  constructor(padding = 0, sessionId = null) {
    this.padding = padding;
    this.sessionId = sessionId || `redbook-${Date.now()}`;
  }

  /** 执行 agent-browser 子命令（无需带前缀） */
  run(subCmd) {
    const fullCmd = `${BrowserSession.CLI} --session "${this.sessionId}" ${subCmd}`;
    try {
      // console.log(fullCmd);
      return execSync(fullCmd, { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }).trim();
    } catch (e) {
      if (e.stderr && e.stderr.includes('close')) return '';
      throw e;
    }
  }

  close() {
    this.run('close 2>/dev/null || true');
  }

  static closeAll() {
    try {
      execSync(`${BrowserSession.CLI} close --all 2>/dev/null || true`, { encoding: 'utf-8' });
    } catch {}
  }

  open(filePath) {
    this.run(`open "file://${filePath}"`);
    this.run('wait --load networkidle');
  }

  detectCardType() {
    const raw = this.run(`eval --json --stdin <<'EOF'
(function() {
  if (document.querySelector('section.quick-view-card')) return 'quick-view-card';
  if (document.querySelector('section.news-card')) return 'news-card';
  return 'unknown';
})();
EOF`);
    const parsed = JSON.parse(raw);
    const result = parsed?.data?.result || parsed;
    return result.replace(/^"|"$/g, '');
  }

  getRect(cardType) {
    const raw = this.run(`eval --json 'const r = document.querySelector("section.${cardType}").getBoundingClientRect(); ({x: r.x, y: r.y, width: r.width, height: r.height})'`);
    const parsed = JSON.parse(raw);
    return parsed?.data?.result || parsed;
  }

  fitViewport(rect) {
    const w = 450;
    const h = Math.floor(rect.height) + this.padding;
    this.run(`set viewport ${w} ${h}`);
    this.run('reload');
    this.run('wait --load networkidle');
    return { w, h };
  }

  capture(outputPath) {
    // this.run('wait --fonts');
    this.run(`screenshot --screenshot-format png "${outputPath}"`);
    return fs.existsSync(outputPath);
  }
}

// ============ RedbookScreenshot — 主流程编排 ============
class RedbookScreenshot {
  constructor(date, opts = {}) {
    this.date = date;
    this.padding = opts.padding ?? 16;
    this.baseDir = path.resolve(__dirname, '..', 'output');
    this.redbookDir = path.join(this.baseDir, date, 'redbook');
    this.outputDir = path.join(this.baseDir, date, 'redbook-png');
    this.logger = new Logger(date);
  }

  validate() {
    if (!fs.existsSync(this.redbookDir)) {
      throw new Error(`redbook 目录不存在: ${this.redbookDir}`);
    }

    this.htmlFiles = fs.readdirSync(this.redbookDir)
      .filter(f => f.endsWith('.html'))
      .sort()
      .map(f => path.join(this.redbookDir, f));

    if (this.htmlFiles.length === 0) {
      throw new Error('redbook 目录中没有 HTML 文件');
    }

    fs.mkdirSync(this.outputDir, { recursive: true });
    return this;
  }

  logSummary() {
    this.logger.info(`📁 日期: ${this.date}`);
    this.logger.info(`📁 输入: ${this.redbookDir}`);
    this.logger.info(`📁 输出: ${this.outputDir}`);
    this.logger.info(`📐 留白: ${this.padding}px`);
    this.logger.info(`📄 找到 ${this.htmlFiles.length} 个文件`);
  }

  processOne(browser, htmlFile, index, total) {
    const basename = path.basename(htmlFile, '.html');
    this.logger.info(`📸 [${index + 1}/${total}] 处理: ${basename}.html`);

    browser.open(htmlFile);
    this.logger.info('  ✓ 页面已打开');

    const cardType = browser.detectCardType();
    if (cardType === 'unknown') {
      this.logger.warning('  ⚠️  未找到已知卡片类型，跳过');
      return false;
    }
    this.logger.info(`  ✓ 卡片类型: ${cardType}`);

    const rect = browser.getRect(cardType);
    this.logger.info(`  ✓ 位置: x=${Math.floor(rect.x)}, y=${Math.floor(rect.y)}  尺寸: ${Math.floor(rect.width)}x${Math.floor(rect.height)}`);

    const { w, h } = browser.fitViewport(rect);
    this.logger.info(`  ✓ 视口: ${w}x${h} 已设置`);

    const outputFile = path.join(this.outputDir, `${basename}.png`);
    const ok = browser.capture(outputFile);

    if (ok) {
      const size = fs.statSync(outputFile).size;
      this.logger.info(`  ✅ 已保存: ${basename}.png (${size} bytes)`);
    } else {
      this.logger.error('  ❌ 警告: 截图未生成');
    }
    return ok;
  }

  run() {
    this.validate();
    this.logSummary();

    BrowserSession.closeAll();

    const browser = new BrowserSession(this.padding);
    let success = 0;

    try {
      for (let i = 0; i < this.htmlFiles.length; i++) {
        if (this.processOne(browser, this.htmlFiles[i], i, this.htmlFiles.length)) {
          success++;
        }
      }
    } finally {
      browser.close();
    }

    this.logger.info('🎉 批量截图完成！');
    this.logger.info(`📁 输出目录: ${this.outputDir}`);
    this.logger.info(`📊 共处理 ${this.htmlFiles.length} 个文件，成功 ${success} 个`);

    return { total: this.htmlFiles.length, success };
  }
}

// ============ 入口 ============
function getToday() {
  return new Date().toISOString().slice(0, 10);
}

const date = process.argv[2] || getToday();
new RedbookScreenshot(date).run();
