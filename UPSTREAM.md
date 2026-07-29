# SM8750 Common Upstream Policy

更新时间：2026-07-29

## 1. 官方上游

```text
Repository: OnePlusOSS/android_kernel_common_oneplus_sm8750
Branch: oneplus/sm8750_b_16.0.0_oneplus_13
Tracking branch: upstream/oneplus-sm8750-b-16.0.0-oneplus-13
```

当前核对发布：

| 项目 | 当前值 |
|---|---|
| 设备版本 | `PJZ110_16.0.9.401(CN01)` |
| common SHA | `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` |
| common 版本 | Linux `6.6.118` |
| Android common tag | `android15-6.6-2026-01_r22` |
| msm-kernel SHA | `6028f47faddaa27700f8dd3a1d83906ea8f27170` |
| modules / DT SHA | `d50b305f7da9e14715a25120a4ac7b1a4b8b97c3` |
| Manifest | `OnePlusOSS/kernel_manifest:oneplus/sm8750` / `oneplus_13_b.xml` |

正式构建必须保存 `repo manifest -r` 生成的固定 revision manifest。浮动分支 tip 不能代替可复现版本记录。

## 2. 本地与官方关系

| 项目 | 当前结果 |
|---|---|
| 本地分支 | `6.6-final` |
| 本地 common 版本 | Linux `6.6.126` |
| 官方 common 版本 | Linux `6.6.118` |
| 共同祖先 | `5a0ffb447c1dbd82e8e3af7a98c4a629f4b6d143` |
| 本地领先 | 8,947 commits |
| 本地落后 | 5 official commits |
| 固定同步候选 | `sync/official-16.0.9.401-e1b346b6b` |
| 同步 PR | `#6` / Draft |
| 权威冲突路径 | **116 个** |

116 个数字来自真实 `git merge --no-commit --no-ff` 后对 unmerged index 的检查。早期 80 个数字来自截断的 merge-tree 输出，已经废止。

本次同步不是普通版本升级。必须把 OnePlus/OPlus 设备、安全、ABI 和 Android common 更新移植到本地较新的 6.6.126 common 基线上，不能用官方 6.6.118 整树覆盖。

完整冲突清单：

```text
docs/UPSTREAM_SYNC_16.0.9.401.md
```

## 3. 完整 OKI 依赖

本仓库只对应 `kernel_platform/common`。任何同步和发布还必须检查：

- `OnePlusOSS/android_kernel_oneplus_sm8750`
- `OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`
- `OnePlusOSS/kernel_manifest`
- manifest 固定的 CodeLinaro、Kleaf/Bazel、工具链和模块依赖
- Image、vendor_boot、vendor modules、DT/DTBO、ABI/KMI 与 vermagic

只更新 common 后直接发布属于不完整构建。

## 4. 调度架构要求

官方 16.0.9.401 启用 `CONFIG_SCHED_CLASS_EXT` / SCX 和 `CONFIG_SLIM_SCHED`，使用 `SCHED_EXT=7`。

本地 HMBIRD 使用 `CONFIG_HMBIRD_SCHED` 和 `SCHED_HMBIRD=7`，并改写同一组调度公共接口。

因此：

1. HMBIRD 与官方 SCX 当前不能简单同时启用。
2. `kernel/sched/core.c` 的 28 个冲突块不能批量选择一侧。
3. 必须明确采用 HMBIRD 保留、官方 SCX 恢复或双实现重构方案。
4. 在代码和真机验证完成前，不得声明 HMBIRD/SCX 已可共存。
5. wait 与风驰的运行时策略关系必须与 SCX 架构问题分开说明。

## 5. 自动化

| 工作流 | 职责 |
|---|---|
| `.github/workflows/sync-upstream.yml` | 镜像官方 tip，检查普通合并候选 |
| `.github/workflows/verify-upstream-pr.yml` | PR 可见的共同祖先和 merge-tree 核验 |
| `.github/workflows/export-upstream-conflicts.yml` | 导出 base / ours / theirs / conflict-marker 四方文件 |
| `.github/workflows/test-upstream-resolution-pass.yml` | 重放并验证分阶段解决规则 |

自动化要求：

- 只拉取必要 ref，使用 blobless Git 获取。
- 官方镜像分支可以强制更新，但不得承载本地开发提交。
- 固定同步候选必须使用不可变官方 SHA。
- 不自动修改或合并 `6.6-final`。
- 有冲突时上传报告并保持 PR Draft。

## 6. 分阶段解决

### Pass 1

```text
sync/resolutions/16.0.9.401/pass1-ours.txt
scripts/resolve_merge_markers.py
```

第一轮包含 31 个已核验路径。处理方式不是整文件 checkout ours，而是仅将冲突标记块替换为本地段，同时保留 Git 已自动合入的官方无冲突 hunk。

预期结果：

```text
116 initial conflicts
31 resolved paths
85 remaining conflicts
```

该轮不处理调度架构、核心 ABI/KMI、AFDO 和其他需要语义设计的高风险冲突。

### 后续 Pass

建议按以下顺序建立独立解决清单：

1. Makefile / version / tag
2. ABI/KMI、OPlus symbols、protected exports、AFDO
3. HMBIRD / SCX / SLIM 调度架构
4. `gki_defconfig`、Kleaf/Bazel 与工具链
5. task/fork/tick、内存和 vendor hooks
6. F2FS、EXT4、ZRAM 与文件系统 hooks
7. USB、Type-C、IOMMU、电源与设备驱动
8. 网络与音频

每个 Pass 必须可重复运行，输出解决前后冲突计数，并在仍有冲突时禁止生成最终 merge commit。

## 7. 合并原则

1. 上游同步只通过独立 Draft PR。
2. 不使用 `git merge -s ours`。
3. 不整树或批量选择 ours/theirs。
4. 不通过删除 ABI、symbol list、vendor hooks 或配置项消除冲突。
5. 所有解决必须保留来源、理由和可回退提交边界。
6. 非冲突官方 hunk 应保留，除非有明确回退理由。
7. 未完成完整 OKI clean build 和 Boot Verified 前不得进入 Stable。

## 8. 完整验证

### 源码与构建

- [ ] 116 个冲突逐文件解决并记录理由
- [ ] 调度架构和策略编号冲突解决
- [ ] `repo manifest -r` 已保存
- [ ] common / msm-kernel / modules / DT revision 匹配
- [ ] 无空 stub 或缺失组件绕过
- [ ] `oplus_build_kernel.sh sun perf` clean build 成功
- [ ] ABI/KMI、OPlus symbol list、AFDO 检查通过
- [ ] Image、vendor_boot、vendor modules 与 vermagic 匹配

### 真机

- [ ] 可重复启动、重启和回退
- [ ] 蜂窝、移动数据、VoLTE / IMS
- [ ] Wi-Fi、蓝牙、相机、指纹
- [ ] 充电、电池状态、温控
- [ ] 灭屏、深度休眠、唤醒
- [ ] Root、SuSFS、KPM
- [ ] wait、HMBIRD/风驰、SCX 的实际启用路径
- [ ] 网络栈、VPN/TUN、WireGuard

## 9. 回退

上游同步必须保持独立 PR 和分阶段提交。若构建或真机验证失败，优先回退对应 Pass 或整个同步 PR，不在 `6.6-final` 上连续追加无法追踪的临时修补。
