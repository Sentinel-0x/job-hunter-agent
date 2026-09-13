# Build Log: job-hunter-agent

## Log 001: 上层业务解耦与求职流水线独立
- **什么坏了 (What broke)**: 
  原单体架构中的求职情报聚合、简历防幻觉优化器（`JobHunterPipeline`）以及 Telegram 异步推送模块与底层 ReAct 引擎深度耦合，缺乏独立的运行上下文与配置管理。
- **为什么坏 (Why it broke)**: 
  将底座与业务混在同一个仓库中会导致高内聚、低耦合的模块化设计失效，且不利于上层应用针对特定的求职/GTM 业务流进行独立迭代和配置（如 `settings.yaml`）。
- **怎么修的 (How it was fixed)**: 
  创建独立的上层项目 `job-hunter-agent`，将所有垂直业务代码（`pipeline/`, `notifications/`, `config/`）整体迁入，并建立专属的 `BUILD_LOG.md` 追踪上层业务的迭代与防幻觉对齐日志。

## Log 002: 实现防幻觉简历优化管道与 SQLite 状态持久层
- **什么坏了 (What broke)**: 写入 `pipeline/resume_optimizer.py` 时报 `No such file or directory` 错误。
- **为什么坏 (Why it broke)**: 目标子目录 `pipeline/` 尚未提前创建，Bash 重定向无法自动创建中间目录。
- **怎么修的 (How it was fixed)**: 使用 `mkdir -p pipeline` 确保父目录存在后再进行文件写入，成功补全核心业务代码与 SQLite 持久化模块。
