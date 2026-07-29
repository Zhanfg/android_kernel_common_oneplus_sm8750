# OnePlus 13 common 上游同步核验：16.0.9.401

更新时间：2026-07-29

## 1. 核验结论

| 项目 | 结果 |
|---|---|
| 本地分支 | `6.6-final` |
| 权威导出基线 | `8c8a5eede0ae990b1672ea3d28ce4058e3cd8dc2` |
| 本地内核代码基线 | Linux `6.6.126` |
| 官方版本 | `PJZ110_16.0.9.401(CN01)` |
| 官方 common 提交 | `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` |
| 官方 common 版本 | Linux `6.6.118` |
| Android common tag | `android15-6.6-2026-01_r22` |
| 共同祖先 | `5a0ffb447c1dbd82e8e3af7a98c4a629f4b6d143` |
| 本地领先 | 8,947 commits |
| 本地落后 | 5 official commits |
| 直接 Git merge | 有冲突 |
| 权威冲突路径 | **116 个** |
| 同步候选 | PR `#6`，保持 Draft |

之前记录的 80 个冲突来自截断的 `merge-tree` 文本报告，漏掉了 `kernel/`、`net/`、`sound/`、`init/`、`lib/` 和 `mm/` 下的路径。2026-07-29 使用真实：

```bash
git merge --no-commit --no-ff e1b346b6b4f4096eb342ae3684838a942fd6f6c4
git diff --name-only --diff-filter=U
```

并导出 Git index stage 1/2/3 后，确认权威结果为 **116 个 unresolved index paths**。后续所有文档和验收均以 116 为准。

本地分支与官方分支存在共同祖先，但不是简单快进。本地 common 已推进到 Linux 6.6.126 并包含大量自定义改动；官方 OnePlus 16.0.9.401 common 仍以 Linux 6.6.118 为版本号。本次工作是将官方设备、安全、ABI 与 Android common 更新移植到较新的自定义 common 基线上，不能整树覆盖。

## 2. 冲突统计

| 类别 | 数量 | 主要风险 |
|---|---:|---|
| `drivers/` | 29 | USB、Type-C、IOMMU、蓝牙、NVMe、网络、电源与平台驱动 |
| `fs/` | 17 | F2FS、EXT4、BTRFS、NTFS3、SMB、NFSD |
| `kernel/` | 15 | 调度、fork、tick、events、power、printk |
| `include/` | 13 | 调度、内存、vendor hooks、ABI 接口 |
| `net/` | 12 | MPTCP、Open vSwitch、CAKE/ETS、ESP、vsock、wireless |
| `android/` | 10 | ABI/KMI、OPlus symbol list、AFDO、protected exports |
| `arch/` | 8 | ARM64 配置/BPF、x86、MIPS、LoongArch |
| `sound/` | 6 | PCM、USB audio、HDA、AMD SoC audio |
| 根目录 | 2 | `.gitignore`、`Makefile` |
| 其他 | 4 | Documentation、init、lib、mm |
| **合计** | **116** | — |

5 个官方同步提交覆盖约 3,830 个文件，不能按“只差 5 个提交”低估风险。

## 3. 调度架构阻塞

官方 16.0.9.401 引入并启用：

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

两者占用同一个用户态调度策略编号 `7`，并同时改写：

- fork / cancel / post-fork
- scheduler tick
- pick-next / active class iteration
- setscheduler / policy validation
- cgroup 属性
- idle 通知
- debugfs 与调度状态输出
- `kernel/sched/core.c`、`sched.h`、`build_policy.c` 等公共接口

因此 HMBIRD/风驰与官方 SCX 不能通过简单同时打开配置实现共存。`kernel/sched/core.c` 单文件包含 28 个冲突块，是本轮最高风险项。

在继续前必须选择并实现一种明确架构：

1. **HMBIRD 保留方案**：保留本地 HMBIRD，官方 SCX 代码存在但禁用；逐项移植官方非 SCX 修复。
2. **官方 SCX 方案**：恢复官方 `SCHED_CLASS_EXT`，重新移植 HMBIRD/风驰为独立可选层，解决 policy ID 与接口冲突。
3. **双实现方案**：重新分配策略编号并重构公共 fork/tick/class 接口。风险最高，不应在同一个大提交中完成。

当前不允许把 README 中“SCX 与 HMBIRD 已可共存”视为已验证事实。

## 4. 第一轮可审计解决

`sync/resolutions/16.0.9.401/pass1-ours.txt` 列出 31 个路径。核验表明这些文件的官方 base-to-16.0.9.401 变化已经存在于本地 6.6.126 文件中，或已由更新实现替代。

第一轮不是执行整文件 `git checkout --ours`，而是：

- 保留 Git 已自动合入的所有官方非冲突 hunk；
- 仅把标记冲突块替换为本地段；
- 对每个路径执行 conflict-marker 和 unmerged-index 检查；
- 预期将冲突路径从 116 降至 85；
- 不生成最终 merge commit，不推送源码集成分支。

对应脚本：

```text
scripts/resolve_merge_markers.py
.github/workflows/test-upstream-resolution-pass.yml
```

## 5. 完整冲突路径

### 根目录与文档

- `.gitignore`
- `Documentation/ABI/testing/sysfs-fs-f2fs`
- `Makefile`

### ABI / KMI / AFDO

- `android/abi_gki_aarch64.stg`
- `android/abi_gki_aarch64_oplus`
- `android/abi_gki_aarch64_pixel_watch`
- `android/abi_gki_aarch64_sunxi`
- `android/abi_gki_aarch64_transsion`
- `android/abi_gki_aarch64_vivo`
- `android/abi_gki_aarch64_xiaomi`
- `android/abi_gki_protected_exports_aarch64`
- `android/gki/aarch64/afdo/README.md`
- `android/gki/aarch64/afdo/kernel.afdo`

### 架构与配置

- `arch/arm64/configs/gki_defconfig`
- `arch/arm64/net/bpf_jit_comp.c`
- `arch/loongarch/net/bpf_jit.c`
- `arch/mips/mm/tlb-r4k.c`
- `arch/x86/configs/microdroid_defconfig`
- `arch/x86/kernel/cpu/microcode/amd.c`
- `arch/x86/kvm/svm/svm.c`
- `arch/x86/mm/kaslr.c`

### 驱动

- `drivers/android/vendor_hooks.c`
- `drivers/bluetooth/btusb.c`
- `drivers/cpuidle/governors/menu.c`
- `drivers/gpio/gpio-regmap.c`
- `drivers/gpu/drm/amd/amdgpu/amdgpu_device.c`
- `drivers/gpu/drm/amd/display/dc/dcn20/dcn20_hwseq.c`
- `drivers/hid/hid-ids.h`
- `drivers/hid/hid-quirks.c`
- `drivers/hid/usbhid/hid-core.c`
- `drivers/hwmon/occ/common.c`
- `drivers/input/serio/i8042-acpipnpio.h`
- `drivers/iommu/arm/arm-smmu-v3/arm-smmu-v3-kvm.c`
- `drivers/misc/mei/hw-me-regs.h`
- `drivers/misc/mei/pci-me.c`
- `drivers/net/can/rcar/rcar_canfd.c`
- `drivers/net/ethernet/mellanox/mlx5/core/en_dcbnl.c`
- `drivers/net/ethernet/mellanox/mlx5/core/fw_reset.c`
- `drivers/net/phy/mscc/mscc_main.c`
- `drivers/net/wireless/realtek/rtw88/sdio.c`
- `drivers/nvme/host/pci.c`
- `drivers/phy/broadcom/phy-bcm-ns-usb3.c`
- `drivers/phy/renesas/phy-rcar-gen3-usb2.c`
- `drivers/platform/x86/amd/pmc/pmc-quirks.c`
- `drivers/power/supply/cw2015_battery.c`
- `drivers/spi/spi-tegra210-quad.c`
- `drivers/usb/dwc3/dwc3-pci.c`
- `drivers/usb/gadget/legacy/raw_gadget.c`
- `drivers/usb/storage/unusual_devs.h`
- `drivers/usb/typec/tcpm/tcpm.c`

### 文件系统

- `fs/btrfs/tree-log.c`
- `fs/ext4/orphan.c`
- `fs/ext4/super.c`
- `fs/ext4/xattr.c`
- `fs/f2fs/compress.c`
- `fs/f2fs/data.c`
- `fs/f2fs/f2fs.h`
- `fs/f2fs/gc.c`
- `fs/f2fs/super.c`
- `fs/hfsplus/unicode.c`
- `fs/nfsd/blocklayout.c`
- `fs/nfsd/nfs4proc.c`
- `fs/nfsd/vfs.c`
- `fs/ntfs3/inode.c`
- `fs/ntfs3/run.c`
- `fs/smb/client/smb2file.c`
- `fs/smb/server/smb2pdu.c`

### 内核头文件与 hooks

- `include/asm-generic/vmlinux.lds.h`
- `include/linux/mm.h`
- `include/linux/mm_types.h`
- `include/linux/pageblock-flags.h`
- `include/linux/sched.h`
- `include/linux/sched/task.h`
- `include/linux/zstd.h`
- `include/sound/pcm.h`
- `include/trace/hooks/dtask.h`
- `include/trace/hooks/mm.h`
- `include/trace/hooks/sched.h`
- `include/trace/hooks/vmscan.h`
- `include/uapi/linux/sched.h`

### 内核核心

- `init/Kconfig`
- `kernel/Kconfig.preempt`
- `kernel/events/callchain.c`
- `kernel/events/core.c`
- `kernel/fork.c`
- `kernel/power/process.c`
- `kernel/printk/printk.c`
- `kernel/sched/build_policy.c`
- `kernel/sched/core.c`
- `kernel/sched/cpufreq_schedutil.c`
- `kernel/sched/debug.c`
- `kernel/sched/fair.c`
- `kernel/sched/idle.c`
- `kernel/sched/sched.h`
- `kernel/sched/vendor_hooks.c`
- `kernel/time/tick-sched.c`
- `lib/zstd/zstd_compress_module.c`
- `mm/migrate.c`

### 网络

- `net/core/dst.c`
- `net/ipv4/esp4_offload.c`
- `net/ipv6/esp6_offload.c`
- `net/mptcp/protocol.c`
- `net/mptcp/subflow.c`
- `net/openvswitch/flow_netlink.c`
- `net/sched/act_ife.c`
- `net/sched/sch_cake.c`
- `net/sched/sch_ets.c`
- `net/unix/garbage.c`
- `net/vmw_vsock/virtio_transport_common.c`
- `net/wireless/sme.c`

### 音频

- `sound/core/oss/pcm_oss.c`
- `sound/core/pcm_native.c`
- `sound/pci/hda/patch_realtek.c`
- `sound/soc/amd/yc/acp6x-mach.c`
- `sound/usb/endpoint.c`
- `sound/usb/quirks.c`

## 6. 处理优先级

1. 调度架构决策：HMBIRD / SCX / SLIM 与 policy ID。
2. `Makefile`、版本号和 Android common tag。
3. ABI/KMI、OPlus symbol list、protected exports、AFDO。
4. `gki_defconfig`、Kleaf/Bazel 和工具链。
5. common 与 msm-kernel / vendor modules 接口。
6. task/fork/tick、调度、内存和 vendor hooks。
7. F2FS、EXT4、ZRAM 和文件系统 hooks。
8. USB、Type-C、IOMMU、电源和设备驱动。
9. 网络与音频。
10. 完整 OKI clean build、ABI/KMI 和真机验证。

## 7. 禁止的解决方式

- 不使用 `git merge -s ours`。
- 不整树或批量选择 ours/theirs。
- 不通过删除 ABI、symbol list、vendor hook 或配置项消除冲突。
- 不把“编译通过”视为 ABI、启动和运行时验证完成。
- 不在未固定完整 `oneplus_13_b.xml` manifest 时发布。
- 不只更新 common 而忽略 msm-kernel、modules/devicetree、vendor_boot 和 vendor modules。

## 8. 合并前验证

- [ ] 116 个冲突全部逐文件解决并记录理由
- [ ] 调度架构和策略编号冲突解决
- [ ] `repo manifest -r` 固定完整 OKI revision
- [ ] `oplus_build_kernel.sh sun perf` clean build 成功
- [ ] ABI/KMI、OPlus symbol list、AFDO 检查通过
- [ ] Image、vendor_boot、vendor modules 和 vermagic 匹配
- [ ] AK3 与回退包完成
- [ ] OnePlus 13 可重复启动、重启和回退
- [ ] 蜂窝、Wi-Fi、蓝牙、相机、指纹正常
- [ ] 充电、电池状态、温控、灭屏和深度休眠正常
- [ ] Root、SuSFS、KPM、wait/HMBIRD/SCX 与网络栈逐项验证

在这些检查完成前，同步 PR `#6` 必须保持 Draft。
