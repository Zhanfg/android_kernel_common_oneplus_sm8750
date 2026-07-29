# OnePlus 13 common 上游同步核验：16.0.9.401

更新时间：2026-07-29

## 1. 核验结论

| 项目 | 结果 |
|---|---|
| 本地分支 | `6.6-final` |
| 本地提交 | `83026e393bfba415d829516dcb6886d5070a12ed` |
| 本地 Makefile 版本 | Linux `6.6.126` |
| 官方版本 | `PJZ110_16.0.9.401(CN01)` |
| 官方 common 提交 | `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` |
| 官方 Makefile 版本 | Linux `6.6.118` |
| Android common tag | `android15-6.6-2026-01_r22` |
| 共同祖先 | `5a0ffb447c1dbd82e8e3af7a98c4a629f4b6d143` |
| 本地领先 | 8,947 commits |
| 本地落后 | 5 official commits |
| 文本合并 | 有冲突 |
| 冲突路径 | 80 个 |
| 同步候选 PR | `#6`，保持 Draft |

本地分支与官方分支存在共同祖先，但二者不是简单快进关系。本地 common 已经推进到 Linux 6.6.126，并包含大量自定义改动；官方 OnePlus 16.0.9.401 common 仍以 Linux 6.6.118 为版本号。因此本次工作不能描述为普通的“升级内核版本”，而是将 OnePlus/OPlus 官方设备与 Android common 更新移植到较新的自定义 common 基线上。

## 2. 冲突统计

| 类别 | 数量 | 主要风险 |
|---|---:|---|
| `drivers/` | 29 | USB、Type-C、IOMMU、蓝牙、NVMe、网络与电源驱动 |
| `fs/` | 17 | F2FS、EXT4、BTRFS、NTFS3、SMB/NFSD |
| `include/` | 13 | 调度、内存、vendor hooks、ABI 接口 |
| `android/` | 10 | ABI/KMI、AFDO、protected exports |
| `arch/` | 8 | ARM64 BPF、x86/mips/loongarch 修复与配置 |
| 其他 | 3 | `Makefile`、`.gitignore`、F2FS ABI 文档 |

冲突数量不能用“只落后 5 个提交”来低估。这 5 个官方同步提交本身覆盖约 3,830 个文件。

## 3. 完整冲突路径

### 根目录与文档

- `.gitignore`
- `Makefile`
- `Documentation/ABI/testing/sysfs-fs-f2fs`

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

## 4. 处理优先级

1. `Makefile`、版本号与 Android common tag：明确最终版本语义，禁止把 6.6.118 官方树直接覆盖到 6.6.126 本地树。
2. ABI/KMI：先处理 `.stg`、OPlus symbol list、protected exports、AFDO，再运行 ABI 检查。
3. `gki_defconfig`：逐项保留官方安全配置和项目必需功能，禁止整文件选择 ours/theirs。
4. 调度与内存：`sched.h`、`sched/task.h`、`mm.h`、`mm_types.h`、vendor hooks 必须结合 BORE、wait/HMBIRD、ReSukiSU/SuSFS 等本地改动审核。
5. F2FS/EXT4：先理解官方修复，再移植本地 ZRAM、压缩、文件系统和隐藏相关 hook。
6. USB/Type-C/IOMMU/电源：这些路径可能直接影响启动、充电、外设和稳定性，必须保留独立提交边界。
7. 其他非 OnePlus 设备驱动：按上游修复优先处理，但仍需保证 GKI/allmodconfig 不回归。

## 5. 禁止的解决方式

- 不使用 `git merge -s ours`。
- 不整树选择 ours 或 theirs。
- 不通过删除 ABI、symbol list、vendor hook 或配置项来消除冲突。
- 不将“编译通过”视为 ABI、启动和运行时验证完成。
- 不在未固定完整 `oneplus_13_b.xml` manifest 的情况下发布。
- 不只更新 common 而忽略 msm-kernel、modules/devicetree、vendor_boot 和 vendor modules。

## 6. 合并前验证

- [ ] 80 个冲突全部逐文件解决并记录理由
- [ ] `repo manifest -r` 固定完整 OKI revision
- [ ] `oplus_build_kernel.sh sun perf` clean build 成功
- [ ] ABI/KMI 与 OPlus symbol list 检查通过
- [ ] Image、vendor_boot、vendor modules 和 vermagic 匹配
- [ ] AK3 打包与回退包完成
- [ ] OnePlus 13 可重复启动和重启
- [ ] 蜂窝、移动数据、Wi-Fi、蓝牙、相机、指纹正常
- [ ] 充电、电池状态、温控、灭屏和深度休眠正常
- [ ] Root、SuSFS、KPM、wait/HMBIRD/SCX、网络栈逐项验证

在这些检查完成前，同步 PR `#6` 必须保持 Draft。
