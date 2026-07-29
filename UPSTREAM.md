# SM8750 Common Upstream Policy

更新时间：2026-07-29

## 1. 主要官方上游

```text
Repository: OnePlusOSS/android_kernel_common_oneplus_sm8750
Branch: oneplus/sm8750_b_16.0.0_oneplus_13
Tracking branch: upstream/oneplus-sm8750-b-16.0.0-oneplus-13
```

2026-07-29 核对到的官方发布：

```text
Device release: PJZ110_16.0.9.401(CN01)
Android common tag: android15-6.6-2026-01_r22
```

完整 OnePlusOSS 核心组件：

| 组件 | 分支 | 核对提交 |
|---|---|---|
| common | `oneplus/sm8750_b_16.0.0_oneplus_13` | `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` |
| msm-kernel | `oneplus/sm8750_b_16.0.0_oneplus_13` | `6028f47faddaa27700f8dd3a1d83906ea8f27170` |
| modules / devicetree | `oneplus/sm8750_b_16.0.0_oneplus_13` | `d50b305f7da9e14715a25120a4ac7b1a4b8b97c3` |
| manifest | `oneplus/sm8750` / `oneplus_13_b.xml` | 正式构建以 `repo manifest -r` 固定结果为准 |

这些 SHA 只表示核对时各官方分支的 tip。正式构建必须保存 `OnePlusOSS/kernel_manifest:oneplus/sm8750` 下 `oneplus_13_b.xml` 对应的固定 revision manifest。

## 2. 当前同步状态

| 项目 | 当前结果 |
|---|---|
| 本地分支 | `6.6-final` |
| 本地 common 版本 | Linux `6.6.126` |
| 官方 common 版本 | Linux `6.6.118` |
| 共同祖先 | `5a0ffb447c1dbd82e8e3af7a98c4a629f4b6d143` |
| 本地领先 | 8,947 commits |
| 本地落后 | 5 official commits |
| 官方镜像分支 | 已更新到 `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` |
| 同步候选 | PR `#6` / Draft |
| 文本冲突 | 80 个路径 |

官方 16.0.9.401 与本地 `6.6-final` 存在共同祖先，但不是普通快进。本地 common 已经推进到 6.6.126，而官方设备树仍以 6.6.118 为版本号。本次工作是将官方设备、安全、ABI 和 Android common 更新移植到本地较新内核基线上，不得通过整树覆盖完成。

完整冲突清单、风险分类和处理顺序见：

```text
docs/UPSTREAM_SYNC_16.0.9.401.md
```

在 80 个冲突、完整 OKI clean build、ABI/KMI 和真机验收完成前，PR `#6` 必须保持 Draft。

## 3. 完整工程依赖

本仓库只对应 `kernel_platform/common`。上游审核时还必须同步检查：

- `OnePlusOSS/android_kernel_oneplus_sm8750`
- `OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`
- `OnePlusOSS/kernel_manifest`
- manifest 固定的 CodeLinaro、Kleaf/Bazel、工具链与模块依赖

不能只更新 common 后直接发布。

## 4. 自动工作流行为

`.github/workflows/sync-upstream.yml` 与 `.github/workflows/verify-upstream-pr.yml` 会：

1. 使用 blobless 历史获取和稀疏工作树，避免完整检出大型 common 仓库。
2. 获取官方 common 分支。
3. 将官方 tip 强制同步到独立跟踪分支。
4. 记录本地 SHA、官方 SHA、内核版本和共同祖先。
5. 使用非破坏性的 `git merge-tree` 检查冲突。
6. 只有不存在文本冲突时才允许建立普通合并候选。
7. 无共同祖先或出现冲突时停止，不创建误导性自动合并结果。
8. 上传 Markdown 报告并写入 Actions Summary。
9. 永不直接修改或自动合并 `6.6-final`。

跟踪分支的强制更新是预期行为，因为它只镜像官方浮动分支；本地开发提交不得放入该分支。正式同步应使用固定 SHA 的 `sync/official-*` 分支。

## 5. 合并原则

1. 上游同步必须使用独立 Draft PR。
2. 不使用 `git merge -s ours`、整树覆盖或删除冲突文件。
3. 设备、ABI、安全和构建修复应先理解官方意图，再移植本地功能。
4. 本地补丁按功能组保留清晰提交边界。
5. 每次合并记录：
   - 官方 common SHA
   - 完整固定 manifest
   - 本地基线 SHA
   - 本地与官方内核版本
   - 冲突文件和处理方式
   - 工具链与构建结果
   - 真机验证结果
6. 未完成 Boot Verified 前不得进入 Stable 发布。

## 6. 冲突处理顺序

1. `Makefile`、版本号与 Android common tag
2. ABI / KMI / symbol list / AFDO
3. common 与 msm-kernel 接口
4. vendor modules / device tree 依赖
5. `gki_defconfig`、Kleaf / Bazel 和工具链
6. Root / ReSukiSU / SuSFS / KPM
7. 调度器、task / scheduler 与 vendor hooks
8. ZRAM、内存、I/O、F2FS 和 EXT4
9. USB / Type-C / IOMMU / 电源与设备驱动
10. 网络、BBR、Netfilter、WireGuard
11. Baseband Guard、省电和其他功能
12. 非必要编译优化

调度器、`task_struct`、RCU、内存生命周期、文件系统、ABI 和网络栈冲突必须逐项审查，不能以“编译通过”替代运行时正确性。

## 7. 完整验证

### 源码与构建

- [ ] 80 个冲突逐文件解决并记录理由
- [ ] `repo manifest -r` 已保存
- [ ] common / msm-kernel / modules / DT revision 匹配
- [ ] 无空 stub 或缺失组件绕过
- [ ] `oplus_build_kernel.sh sun perf` clean build 成功
- [ ] Image、vendor_boot、vendor modules 版本匹配
- [ ] ABI / KMI、OPlus symbol list 和 AFDO 检查通过

### 真机

- [ ] 可重复启动和重启
- [ ] Fastboot / Recovery 回退可用
- [ ] 蜂窝、移动数据、VoLTE / IMS 基础功能
- [ ] Wi-Fi、蓝牙
- [ ] 相机、指纹
- [ ] 充电、电池状态、温控
- [ ] 灭屏、深度休眠、唤醒
- [ ] Root、SuSFS、KPM
- [ ] 默认 wait 与可选 HMBIRD / SCX 路径
- [ ] 网络栈、VPN / TUN、WireGuard

## 8. 回退

上游同步必须保持单独 PR 和提交边界。真机失败时优先整体回退同步 PR，再按功能组拆分定位；不要在 `6.6-final` 上连续追加无法追踪的临时修补。
