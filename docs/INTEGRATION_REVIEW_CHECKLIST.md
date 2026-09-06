# Fusion V2 集成审查清单

目标栈：OnePlus 13 common + ReSukiSU + SUSFS 2.3.x；KPatch-Next 在 Image 构建后处理，不直接写入 common 源码树。

## Root / SUSFS
- [ ] ReSukiSU 固定 commit 已记录
- [ ] ReSukiSU 是唯一 Root Core
- [ ] SUSFS 固定为 2.3.x
- [ ] SUSFS 6.6 patch 可在当前 OnePlus common 上 clean apply 或有逐 hunk 适配记录
- [ ] `zygote_next`、`TIF_PROC_NO_SU`、stat/faccessat 新接口兼容
- [ ] AVC spoof 与 ReSukiSU 自身相关逻辑无重复 Hook

## OnePlus 兼容
- [ ] HMBIRD / slim_walt / EEVDF 路径不被 Root/SUSFS 改坏
- [ ] OPlus vendor hooks 无 ABI/KMI 回归
- [ ] 不通过修改 `6.6.x` 显示值伪装兼容性
- [ ] 保留 SafeSetID，除非有单独验证依据

## 功能差异
- [ ] TTL / IPv6 HL
- [ ] USER_NS / PID_NS / IPC_NS
- [ ] SYSVIPC / POSIX_MQUEUE
- [ ] NTSYNC
- [ ] ADIOS 仅在单独验证后决定是否默认
- [ ] Baseband Guard 不进入第一轮基础集成
- [ ] Lindroid EVDI 不进入第一轮基础集成

## 发布边界
- [ ] common 源码树不嵌入 KPatch-Next
- [ ] KPatch-Next 由控制仓库在最终 Image 上固定执行
- [ ] 不提供安装时 KPM 开关
- [ ] pre/post KPatch Image SHA256 可追溯
