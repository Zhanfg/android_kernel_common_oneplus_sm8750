# OnePlus 13 SM8750 Custom Common Kernel

这是 **OnePlus 13（PJZ110 / `sun` / SM8750）** 自定义内核项目的 common 源码仓库，默认开发分支为 `6.6-final`。

> 本仓库只对应完整 OnePlus OKI 工程中的 `kernel_platform/common`。它不包含完整 msm-kernel、vendor modules、设备树、Kleaf/Bazel 依赖和工具链，因此不能单独代表完整 OnePlus 13 内核工程，也不应独立生成正式刷写包。

## 项目关系

| 角色 | 仓库 / 分支 | 说明 |
|---|---|---|
| 项目控制仓库 | [`Zhanfg/OnePlus13-kernel`](https://github.com/Zhanfg/OnePlus13-kernel) / `main` | 构建、补丁、AK3、测试、发布与文档 |
| 本仓库 | `Zhanfg/android_kernel_common_oneplus_sm8750` / `6.6-final` | common 层自定义补丁和开发历史 |
| 官方 manifest | [`OnePlusOSS/kernel_manifest`](https://github.com/OnePlusOSS/kernel_manifest) / `oneplus/sm8750` | 完整 OKI 工程入口，使用 `oneplus_13_b.xml` |
| 官方 common | [`OnePlusOSS/android_kernel_common_oneplus_sm8750`](https://github.com/OnePlusOSS/android_kernel_common_oneplus_sm8750) / `oneplus/sm8750_b_16.0.0_oneplus_13` | common 官方上游 |
| 官方 msm-kernel | [`OnePlusOSS/android_kernel_oneplus_sm8750`](https://github.com/OnePlusOSS/android_kernel_oneplus_sm8750) | 平台内核与 OnePlus/OPlus 代码 |
| 官方 modules / DT | [`OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`](https://github.com/OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750) | vendor modules 与设备树 |

完整工程还需要 manifest 固定的 CodeLinaro、Kleaf/Bazel、工具链和其他依赖。

## 当前基线与差异

最后核对：**2026-07-29**。

| 项目 | 当前值 |
|---|---|
| 设备系统 | `PJZ110_16.0.9.401(CN01)` |
| Manifest | `OnePlusOSS/kernel_manifest:oneplus/sm8750` |
| Manifest 文件 | `oneplus_13_b.xml` |
| 官方 common 提交 | `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` |
| 官方 common 版本 | Linux `6.6.118` / `android15-6.6-2026-01_r22` |
| 官方 msm-kernel 提交 | `6028f47faddaa27700f8dd3a1d83906ea8f27170` |
| 官方 modules / DT 提交 | `d50b305f7da9e14715a25120a4ac7b1a4b8b97c3` |
| 本地开发分支 | `6.6-final` |
| 本地 common 版本 | Linux `6.6.126` |
| 共同祖先 | `5a0ffb447c1dbd82e8e3af7a98c4a629f4b6d143` |
| 本地相对官方 | 领先 8,947 commits，落后 5 official commits |

这里存在两套不同含义的版本：

- **官方设备基线**：OnePlus 13 `16.0.9.401`，common Makefile 为 Linux 6.6.118。
- **本地 common 开发基线**：`6.6-final`，Makefile 已推进到 Linux 6.6.126，并包含大量自定义补丁。

因此不能通过整树覆盖把官方 6.6.118 直接写入本地 6.6.126，也不能把本次同步描述为普通内核版本升级。正确工作是把官方设备、安全、ABI 和 Android common 更新移植到当前自定义基线上。

## 当前上游同步状态

官方跟踪分支：

```text
upstream/oneplus-sm8750-b-16.0.0-oneplus-13
```

该分支已精确镜像官方提交 `e1b346b6b4f4096eb342ae3684838a942fd6f6c4`。

同步候选：

```text
PR #6: chore: 同步 OnePlus 13 官方 common 16.0.9.401
branch: sync/official-16.0.9.401-e1b346b6b
status: Draft / conflicts
```

实际 `merge-tree` 核验发现 **80 个冲突路径**。主要分布：

- `drivers/`：29
- `fs/`：17
- `include/`：13
- `android/` ABI/KMI/AFDO：10
- `arch/`：8
- 根目录与文档：3

完整冲突清单和处理顺序见 [`docs/UPSTREAM_SYNC_16.0.9.401.md`](docs/UPSTREAM_SYNC_16.0.9.401.md)。在冲突、完整 OKI 构建和真机验收完成前，PR #6 必须保持 Draft。

## 自动上游核验

工作流：

```text
.github/workflows/sync-upstream.yml
.github/workflows/verify-upstream-pr.yml
```

行为：

1. 使用 blobless 历史获取和稀疏工作树，避免完整检出大型 common 仓库。
2. 获取官方 common 最新提交。
3. 更新独立官方跟踪分支。
4. 检查共同祖先和提交差异。
5. 使用非破坏性的 `git merge-tree` 检查文本冲突。
6. 只有无冲突时才允许建立普通合并候选。
7. 永不自动覆盖或合并 `6.6-final`。

详细规则见 [`UPSTREAM.md`](UPSTREAM.md)。

## 正确的完整构建方式

本仓库不提供独立正式构建入口。完整构建应在 OnePlusOSS OKI 工作区中进行：

```bash
repo init \
  -u https://github.com/OnePlusOSS/kernel_manifest.git \
  -b oneplus/sm8750 \
  -m oneplus_13_b.xml

repo sync -c --force-sync --no-clone-bundle --no-tags -j"$(nproc)"
repo manifest -r -o manifest-pinned.xml

./kernel_platform/oplus/build/oplus_build_kernel.sh sun perf
```

测试本仓库改动时，应在固定 manifest 的完整工作区内，将 `kernel_platform/common` 指向经过审核的本仓库提交，再执行 clean build。

## 合并前检查

- [ ] 80 个冲突逐文件解决并记录理由
- [ ] 保存完整 `manifest-pinned.xml`
- [ ] common、msm-kernel、modules / DT revision 匹配
- [ ] ABI/KMI、OPlus symbol list 和 AFDO 检查通过
- [ ] `oplus_build_kernel.sh sun perf` clean build 成功
- [ ] Image、vendor_boot、vendor modules 与 vermagic 匹配
- [ ] OnePlus 13 / 对应 ColorOS 可重复启动和回退
- [ ] 蜂窝、Wi-Fi、蓝牙、相机、指纹、充电、温控和休眠通过测试
- [ ] Root、SuSFS、KPM、wait/HMBIRD/SCX 和网络功能通过测试

## 分支策略

| 分支 | 用途 |
|---|---|
| `6.6-final` | 当前自定义 common 开发基线 |
| `upstream/oneplus-sm8750-b-16.0.0-oneplus-13` | 官方 common 只读镜像 |
| `sync/official-*` / `sync/upstream-*` | 固定官方提交的同步候选 |
| `fix/*` | 单一问题修复 |
| `feature/*` | 独立功能开发 |

## 禁止事项

- 不把本仓库当作完整 OKI 工程。
- 不直接把单独编译的 Image 标记为可刷写稳定包。
- 不使用 `ours`、整树覆盖或删除冲突代码伪造同步成功。
- 不把空 Kconfig / Makefile stub 构建当作正式产物。
- 不在未核对 vendor_boot、vendor modules 和 ABI 时刷入。
- 不提交 Token、Cookie、密钥、账号、设备序列号、未脱敏日志或本机绝对路径。

## 验证等级

- **Experimental**：源码可合并或可编译，但未完成真机启动。
- **Boot Verified**：指定 PJZ110 / ColorOS 版本可以重复启动并可回退。
- **Runtime Verified**：关键硬件与内核功能通过测试。
- **Stable**：完成重复刷写、重启、待机和基础回归。

## 许可证

Linux 内核源码遵循 GPL-2.0。第三方补丁遵循各自许可证和来源要求。
