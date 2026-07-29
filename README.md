# OnePlus 13 SM8750 Custom Common Kernel

这是 **OnePlus 13（PJZ110 / `sun` / SM8750）** 自定义内核项目的 common 源码仓库，默认开发分支为 `6.6-final`。

> 本仓库只对应完整 OnePlus OKI 工程中的 `kernel_platform/common`。它不包含完整 msm-kernel、vendor modules、设备树、Kleaf/Bazel 依赖和工具链，因此不能单独代表完整 OnePlus 13 内核工程，也不应独立生成正式刷写包。

## 项目关系

| 角色 | 仓库 / 分支 | 说明 |
|---|---|---|
| 项目控制仓库 | [`Zhanfg/OnePlus13-kernel`](https://github.com/Zhanfg/OnePlus13-kernel) / `main` | 构建、补丁、AK3、测试、发布与文档 |
| 本仓库 | `Zhanfg/android_kernel_common_oneplus_sm8750` / `6.6-final` | common 层自定义补丁和开发历史 |
| 官方 manifest | [`OnePlusOSS/kernel_manifest`](https://github.com/OnePlusOSS/kernel_manifest) / `oneplus/sm8750` | 完整 OKI 工程入口，使用 `oneplus_13_b.xml` |
| 官方 common | [`OnePlusOSS/android_kernel_common_oneplus_sm8750`](https://github.com/OnePlusOSS/android_kernel_common_oneplus_sm8750) / `oneplus/sm8750_b_16.0.0_oneplus_13` | 本仓库的主要官方上游 |

完整工程还需要：

- `OnePlusOSS/android_kernel_oneplus_sm8750`
- `OnePlusOSS/android_kernel_modules_and_devicetree_oneplus_sm8750`
- manifest 固定的 CodeLinaro / Kleaf / Bazel / 工具链依赖

## 当前官方基线

最后核对：**2026-07-29**。

| 项目 | 当前值 |
|---|---|
| 设备系统 | `PJZ110_16.0.9.401(CN01)` |
| Manifest | `OnePlusOSS/kernel_manifest:oneplus/sm8750` |
| Manifest 文件 | `oneplus_13_b.xml` |
| 官方 common 分支 | `oneplus/sm8750_b_16.0.0_oneplus_13` |
| 官方 common 提交 | `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` |
| Android common tag | `android15-6.6-2026-01_r22` |
| 内核系列 | Android 15 / Linux 6.6 |
| 本地开发分支 | `6.6-final` |

上游提交会同步到只读跟踪分支：

```text
upstream/oneplus-sm8750-b-16.0.0-oneplus-13
```

跟踪分支只镜像官方 common，不包含本项目自定义补丁。

## 当前状态

- `6.6-final` 包含本项目的 common 层自定义改动。
- 当前分支最新本地提交包含 BORE 生命周期修复等本地补丁。
- 官方 16.0.9.401 common 上游已经确认，但尚未宣称完整合入 `6.6-final`。
- 自动同步只负责更新官方跟踪分支，并在能够安全合并时创建 Draft PR。
- 无共同祖先或出现冲突时，工作流会停止并上传报告，不会覆盖 `6.6-final`。
- 真机启动和运行时验证仍由完整 OKI 工程完成。

## 上游同步

工作流：

```text
.github/workflows/sync-upstream.yml
```

行为：

1. 获取官方 common 最新提交。
2. 强制更新独立的官方跟踪分支。
3. 检查官方上游与 `6.6-final` 是否存在共同祖先。
4. 有共同祖先且普通合并无文本冲突时，创建 `sync/upstream-*` 候选分支和 Draft PR。
5. 无共同祖先或存在冲突时停止，并保存同步报告。
6. 永不自动合并 `6.6-final`。

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

需要测试本仓库改动时，应在固定 manifest 的完整工作区内，将 `kernel_platform/common` 指向经过审核的本仓库提交，再重新进行完整构建。

## 合并前检查

每个上游同步候选至少需要：

- [ ] 记录官方 common 提交 SHA
- [ ] 保存完整 `manifest-pinned.xml`
- [ ] 核对 common 与 msm-kernel / modules / DT 的版本匹配
- [ ] 逐项审核本地调度、ZRAM、Root、网络和安全补丁
- [ ] 完整 OKI clean build 成功
- [ ] Image、vendor_boot 与 vendor modules 的 vermagic / ABI 匹配
- [ ] OnePlus 13 / 对应 ColorOS 版本可重复启动
- [ ] 蜂窝、Wi-Fi、蓝牙、相机、指纹、充电和休眠通过测试
- [ ] Root、SuSFS、调度和网络功能通过测试
- [ ] 回退包和恢复路径可用

## 分支策略

| 分支 | 用途 |
|---|---|
| `6.6-final` | 当前自定义 common 开发基线 |
| `upstream/oneplus-sm8750-b-16.0.0-oneplus-13` | 官方 common 只读镜像 |
| `sync/upstream-*` | 自动生成的上游合并候选 |
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
