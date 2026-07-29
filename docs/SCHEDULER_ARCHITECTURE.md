# OnePlus 13 scheduler architecture

更新时间：2026-07-29

## 1. 当前结论

OnePlus 13 自定义 common 的当前可维护调度架构为：

```text
Default path: fair / wait
Optional custom path: HMBIRD / 风驰
Official sched_ext / SCX: disabled for this synchronization
Official CONFIG_SLIM_SCHED: disabled for this synchronization
```

这保留了项目原本要求的 wait 与风驰切换路径，同时避免把两套占用相同策略编号和公共接口的扩展调度实现强行编入同一内核。

## 2. HMBIRD 不是官方 SCX

本地配置：

```text
CONFIG_HMBIRD_SCHED=y
SCHED_HMBIRD=7
```

本地实现位于：

```text
kernel/sched/hmbird/
kernel/sched/hmbird.h
include/linux/sched/hmbird.h
```

它实现独立的 `hmbird_sched_class`，并直接接入 fork、tick、pick-next、setscheduler、cgroup、idle、debugfs 和 shadow tick 路径。

`kernel/sched/hmbird/slim.h` 是 HMBIRD 私有头文件，包含 HMBIRD 的运行时参数和辅助接口。它不等于官方 `CONFIG_SLIM_SCHED`。

## 3. 官方 16.0.9.401 调度实现

官方 common 配置：

```text
CONFIG_SLIM_SCHED=y
CONFIG_SCHED_CLASS_EXT=y
SCHED_EXT=7
```

官方 SCX 使用 `ext_sched_class`、`kernel/sched/ext.c` 和 BPF struct_ops 接口。

官方 `CONFIG_SLIM_SCHED` 还会改变稳定结构中的 KABI 使用：

- `task_struct` 增加 `sched_prop`、`sched_ext_entity *scx` 等字段。
- `rq` 增加 `struct scx_rq *scx`。
- proc/debug 输出增加调度属性。
- shadow tick 与调度辅助接口使用官方 SCX 数据结构。

因此它不是一个可以独立勾选、且与 HMBIRD 无关的小优化。

## 4. 无法直接共存的原因

### 策略编号冲突

```text
SCHED_HMBIRD = 7
SCHED_EXT = 7
```

用户态传入策略编号 7 时，内核无法同时把它解释为 HMBIRD 和官方 sched_ext。

### 调度类与公共接口冲突

两套实现同时修改：

- `sched_fork()` / cancel / post-fork
- `scheduler_tick()`
- `pick_next_task()` 和调度类遍历
- `__sched_setscheduler()` 与 policy 校验
- idle 通知和 tick 停止判断
- cgroup 调度属性
- task / rq 扩展字段
- debugfs 和 proc 输出

`kernel/sched/core.c` 在官方同步中出现 28 个冲突块，说明这不是配置层面的简单冲突。

### KABI 与状态模型不同

HMBIRD 主要通过 Android OEM 数据区域保存自定义实体和属性；官方 SLIM/SCX 使用 Android KABI 槽位保存 `sched_prop`、SCX task entity 和 runqueue state。两套状态模型需要明确的生命周期、初始化、fork、释放和 ABI 设计，不能同时拼接。

## 5. 本轮同步决策

针对官方 `PJZ110_16.0.9.401(CN01)` common 同步候选：

```text
CONFIG_HMBIRD_SCHED=y
CONFIG_SCHED_CLASS_EXT=n
CONFIG_SLIM_SCHED=n
```

处理原则：

1. 保留 wait / fair 默认路径。
2. 保留现有 HMBIRD / 风驰实现和策略编号 7。
3. 保留官方 `ext.c` 等新增源码文件，但本轮不编译、不启用。
4. 移植官方与 SCX 无关的调度、内存、安全和设备修复。
5. 对同时触及 HMBIRD 的官方通用修复逐项人工移植。
6. 不把“官方 SCX 源码存在于树中”写成“SCX 已启用”。
7. 不把 `hmbird/slim.h` 写成官方 SLIM_SCHED。

## 6. 后续恢复 SCX 的正确方式

若未来需要官方 SCX，必须建立独立功能分支，至少完成：

1. 为 HMBIRD 与 SCX 重新设计用户态策略选择；不能共享编号 7。
2. 统一 task / rq 的 KABI 数据布局和生命周期。
3. 重构 fork、tick、pick-next、idle 和 cgroup 公共入口。
4. 确认 HMBIRD、SCX 和 fair/wait 的启停与回退状态机。
5. 分别构建 HMBIRD-only、SCX-only 和目标共存配置。
6. 完成重复切换、压力、休眠、温控和真机回归。

在此工作完成前，SCX 应保持关闭。

## 7. 验证要求

### 静态与构建

- [ ] `gki_defconfig` 只启用 HMBIRD，不启用官方 SCX/SLIM
- [ ] 不存在 `SCHED_EXT` 与 `SCHED_HMBIRD` 的重复运行时解释
- [ ] HMBIRD task entity 的创建、fork、取消、释放路径完整
- [ ] shadow tick 和 idle 路径可编译
- [ ] 完整 OKI `sun perf` clean build 成功
- [ ] ABI/KMI 与 OPlus symbol list 通过

### 真机

- [ ] 默认 wait/fair 正常启动
- [ ] HMBIRD/风驰可启用和回退
- [ ] 多次切换后无任务卡死、watchdog、RCU stall 或软锁死
- [ ] 前台响应、游戏负载和后台限制符合预期
- [ ] 灭屏、深度休眠、唤醒和温控正常
- [ ] Root、SuSFS、网络与调度切换无明显冲突

## 8. 文档口径

当前对外说明应使用：

```text
默认 wait / fair；HMBIRD / 风驰为可选自定义调度路径。
官方 SCX / sched_ext 与 SLIM_SCHED 尚未集成，保持关闭。
```

不得使用：

```text
HMBIRD、SCX、SLIM 已完成共存。
```
