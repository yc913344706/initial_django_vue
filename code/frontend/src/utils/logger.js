
// 日志级别定义
const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
}

// 从配置文件获取日志级别，默认为 INFO
const currentLevel = LOG_LEVELS[import.meta.env.VITE_LOG_LEVEL || 'INFO']

class Logger {
  debug(...args) {
    if (currentLevel <= LOG_LEVELS.DEBUG) {
      console.debug('[DEBUG]', ...args)
    }
  }

  info(...args) {
    if (currentLevel <= LOG_LEVELS.INFO) {
      console.log('[INFO]', ...args)
    }
  }

  warn(...args) {
    if (currentLevel <= LOG_LEVELS.WARN) {
      console.warn('[WARN]', ...args)
    }
  }

  error(...args) {
    if (currentLevel <= LOG_LEVELS.ERROR) {
      console.error('[ERROR]', ...args)
    }
  }
}

export default new Logger() 