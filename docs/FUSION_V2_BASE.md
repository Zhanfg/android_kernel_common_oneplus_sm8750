# Fusion V2 official common base

## Base

Fusion V2 starts from the exact OnePlus 13 / ColorOS 16.0.9.401 common mirror:

```text
branch: upstream/oneplus-sm8750-b-16.0.0-oneplus-13
sha:    e1b346b6b4f4096eb342ae3684838a942fd6f6c4
ROM:    PJZ110_16.0.9.401(CN01)
AOSP/QCOM basis: android15-6.6-2026-01_r22
```

This replaces the earlier idea of using `sync/resolution-pass5-compat-16.0.9.401` as a build base. The pass branches are retained only as migration/audit references; their top commits document conflict-resolution passes and do not represent a fully integrated, build-verified source merge.

## Integration stack

```text
OnePlus official common
  -> ReSukiSU
  -> SUSFS 2.3.x kernel-side patch
  -> Fusion config
  -> complete OnePlus OKI sun perf build
  -> Image
  -> KPatch-Next post-build patch
```

KPatch-Next is not vendored into this common tree and is not a Root Core.

## Root architecture

- Root Core: ReSukiSU
- SUSFS: 2.3.x
- KPM runtime: standalone KPatch-Next
- Do not restore ReSukiSU's removed in-tree KPM implementation.
- Do not apply SUSFS's `KernelSU/10_enable_susfs_for_ksu.patch` directly to ReSukiSU; use ReSukiSU's own SUSFS adaptation layer.

## Migration rule

Features from the historical `6.6-final` custom tree are reintroduced one subsystem at a time only after the official base boots/builds with the preceding layer.

The historical 116-way merge-conflict set is not replayed wholesale. Old pass documents are evidence for selecting useful changes, not a requirement to merge every historical local patch.

## Verification order

1. exact official common SHA
2. ReSukiSU source integration
3. SUSFS 2.3 kernel-side integration
4. Kconfig resolution
5. complete OKI clean build
6. KPatch-Next Image patch metadata validation
7. AK3 packaging
8. device boot verification
9. runtime hardware/root/hiding regression
