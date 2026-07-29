# OnePlus 13 SM8750 Custom Common Kernel

这是 **OnePlus 13（PJZ110 / `sun` / SM8750）** 自定义内核项目的 common 源码仓库，默认开发分支为 `6.6-final`。

> 本仓库只对应完整 OnePlus OKI 工程中的 `kernel_platform/common`。它不包含完整 msm-kernel、vendor modules、设备树、Kleaf/Bazel 依赖和工具链，因此不能单独代表完整 OnePlus 13 内核工程，也不应独立生成正式刷写包。

## 项目关系

| 角色 | 仓库 / 分支 | 说明 |
|---|---|---|
| 项目控制仓库 | [`Zhanfg/OnePlus13-kernel`](https://github.com/Zhanfg/OnePlus13-kernel) / `main` | 构建、补丁、AK3、测试、发布与文档 |
| 本仓库 | `Zhanfg/android_kernel_common_oneplus_sm8750` / `6.6-final` | common 层自定义补丁与开发历史 |
| 官方 manifest | [`OnePlusOSS/kernel_manifest`](https://github.com/OnePlusOSS/kernel_manifest) / `oneplus/sm8750` | 完整 OKI 入口，使用 `oneplus_13_b.xml` |
| 官方 common | [`OnePlusOSS/android_kernel_common_oneplus_sm8750`](https://github.com/OnePlusOSS/android_kernel_common_oneplus_sm8750) | common 官方上游 |
| 官方 msm-kernel | [`OnePlusOSS/android_kernel_oneplus_sm8750`](https://github.com/OnePlusOSS/android_kernel_oneplus_sm8750) | Qualcomm / OnePlus 平台代码 |
| 官方 modules / DT | [`OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750) | vendor modules 与设备树 |

## 当前官方基线

最后核对：**2026-07-29**。

| 项目 | 当前值 |
|---|---|
| 设备版本 | `PJZ110_16.0.9.401(CN01)` |
| Manifest | `oneplus/sm8750` + `oneplus_13_b.xml` |
| 官方 common | `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` |
| 官方 common 版本 | Linux `6.6.118` / `android15-6.6-2026-01_r22` |
| 官方 msm-kernel | `6028f47faddaa27700f8dd3a1d83906ea8f27170` |
| 官方 modules / DT | `d50b305f7da9e14715a25120a4ac7b1a4b8b97c3` |
| 本地分支 | `6.6-final` / Linux `6.6.126` |

本地版本号高于官方 common，并不表示已经包含 OnePlus 16.0.9.401 的全部设备、ABI 和厂商改动。本轮工作是把官方变更移植到较新的自定义 common 基线上，不能以官方 6.6.118 整树覆盖本地 6.6.126。

## 官方同步状态

官方镜像分支：

```text
upstream/oneplus-sm8750-b-16.0.0-oneplus-13
e1b346b6b4f4096eb342ae3684838a942fd6f6c4
```

同步候选：

```text
PR #6
branch: sync/official-16.0.9.401-e1b346b6b
status: Draft / conflicts / not merged
```

已确认关系：

| 项目 | 结果 |
|---|---|
| 共同祖先 | `5a0ffb447c1dbd82e8e3af7a98c4a629f4b6d143` |
| 本地领先 | 8,947 commits |
| 本地落后 | 5 official commits |
| 直接 Git merge | 116 个 unresolved index paths |

早期 80 个数字来自截断的 merge-tree 报告。使用真实 merge 并检查 index stage 后，权威结果为 **116**。

冲突分布：

| 类别 | 数量 |
|---|---:|
| 驱动 | 29 |
| 文件系统 | 17 |
| 内核核心 | 15 |
| 头文件与 hooks | 13 |
| 网络 | 12 |
| ABI/KMI/AFDO | 10 |
| 架构与配置 | 8 |
| 音频 | 6 |
| 根目录与其他 | 6 |

完整路径和处理顺序见 [`docs/UPSTREAM_SYNC_16.0.9.401.md`](docs/UPSTREAM_SYNC_16.0.9.401.md)。

## 调度架构阻塞

官方 16.0.9.401 使用：

```text
CONFIG_SLIM_SCHED=y
CONFIG_SCHED_CLASS_EXT=y
SCHED_EXT=7
```

本地分支使用：

```text
CONFIG_HMBIRD_SCHED=y
SCHED_HMBIRD=7
```

HMBIRD 与官方 SCX 占用同一个策略编号，并改写同一批 fork、tick、pick-next、setscheduler、cgroup 和 idle 接口，因此当前不能直接共存。

在解决以下问题前，不得把 README 中的“SCX 与 HMBIRD 可并存”当作已验证事实：

- 调度策略编号
- `kernel/sched/core.c` 的 28 个冲突块
- fork / cancel / post-fork 接口
- tick、idle、class iteration 与 cgroup 接口
- `gki_defconfig` 中 HMBIRD、SLIM 和 SCX 的配置关系

## 第一轮解决进度

第一轮已建立可审计规则：

```text
sync/resolutions/16.0.9.401/pass1-ours.txt
scripts/resolve_merge_markers.py
.github/workflows/test-upstream-resolution-pass.yml
```

该轮处理 31 个路径。规则不是整文件选择 ours，而是：

1. 先让 Git 合入所有无冲突的官方 hunk。
2. 仅替换指定文件中的冲突标记块为本地段。
3. 保留冲突块之外的官方改动。
4. 检查文件不再含 marker，且不再处于 unmerged index。
5. 预期把冲突路径从 116 降至 85。
6. 仍不创建最终 merge commit，不推送可合并源码分支。

调度、ABI/KMI、AFDO、F2FS 核心和设备接口等高风险项不在第一轮机械处理范围内。

## 自动化

| 工作流 | 用途 |
|---|---|
| `sync-upstream.yml` | 官方 common 镜像和候选检查 |
| `verify-upstream-pr.yml` | PR 可见的共同祖先与 merge-tree 核验 |
| `export-upstream-conflicts.yml` | 导出 base / ours / theirs / conflict-marker 四方文件 |
| `test-upstream-resolution-pass.yml` | 重放并验证分阶段解决规则 |

自动化只拉取必要 ref，使用 blobless Git 获取。它不会自动覆盖或合并 `6.6-final`。

## 正确构建方式

完整构建必须从 OnePlusOSS manifest 开始：

```bash
repo init \
  -u https://github.com/OnePlusOSS/kernel_manifest.git \
  -b oneplus/sm8750 \
  -m oneplus_13_b.xml

repo sync -c --force-sync --no-clone-bundle --no-tags -j"$(nproc)"
repo manifest -r -o manifest-pinned.xml

./kernel_platform/oplus/build/oplus_build_kernel.sh sun perf
```

测试本仓库改动时，应在固定 manifest 的完整 OKI 工作区中，将 `kernel_platform/common` 指向经过审核的提交，再执行 clean build。

## 合并前要求

- [ ] 116 个冲突全部逐文件解决并记录理由
- [ ] HMBIRD / SCX / SLIM 调度架构确定并完成移植
- [ ] 固定 `manifest-pinned.xml`
- [ ] common、msm-kernel、modules / DT revision 匹配
- [ ] ABI/KMI、OPlus symbol list、AFDO 通过
- [ ] `oplus_build_kernel.sh sun perf` clean build 成功
- [ ] Image、vendor_boot、vendor modules 与 vermagic 匹配
- [ ] OnePlus 13 可重复启动、重启和回退
- [ ] 蜂窝、Wi-Fi、蓝牙、相机、指纹正常
- [ ] 充电、电池状态、温控、灭屏和深度休眠正常
- [ ] Root、SuSFS、KPM、wait/HMBIRD/SCX 与网络栈完成验证

## 分支策略

| 分支 | 用途 |
|---|---|
| `6.6-final` | 当前自定义 common 开发基线 |
| `upstream/oneplus-sm8750-b-16.0.0-oneplus-13` | 官方 common 只读镜像 |
| `sync/official-*` | 固定官方 SHA 的同步候选 |
| `sync/resolution-*` | 分阶段冲突解决规则与验证 |
| `fix/*` | 单一问题修复 |
| `feature/*` | 独立功能开发 |

## 禁止事项

- 不把本仓库当作完整 OKI 工程。
- 不直接把单独编译的 Image 标记为稳定刷写包。
- 不使用 `ours` merge strategy、整树覆盖或批量选择一侧。
- 不通过删除 ABI、symbol list、vendor hooks 或配置消除冲突。
- 不把空 Kconfig / Makefile stub 构建当作正式产物。
- 不在未核对 vendor_boot、vendor modules 和 ABI 时刷入。
- 不提交 Token、Cookie、密钥、账号、设备序列号、未脱敏日志或本机绝对路径。

## 验证等级

- **Experimental**：源码可合并、可静态检查或可打包，但未完成真机启动。
- **Boot Verified**：指定 PJZ110 / ColorOS 可以重复启动并可回退。
- **Runtime Verified**：关键硬件与内核功能通过测试。
- **Stable**：完成重复刷写、重启、待机和基础回归。

## 许可证

Linux 内核源码遵循 GPL-2.0。第三方补丁遵循各自许可证和来源要求。
