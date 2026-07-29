# Resolution pass 3

Pass 3 applies after the validated pass-1 and pass-2 rules.

Expected cumulative result:

```text
116 initial conflicts
85 after pass 1
67 after pass 2
17 resolved by pass 3
50 remaining conflicts
```

## Local conflict blocks retained

`pass3-ours.txt` keeps local conflict blocks where the custom 6.6.126 tree has a newer or project-specific implementation:

- ARM64 BPF capability check uses the initial user namespace without audit noise.
- x86 KASLR keeps the broader `ZONE_DEVICE` direct-map constraint.
- Bluetooth and HDA retain additional device quirks.
- cpuidle keeps the project residency threshold.
- Realtek SDIO keeps the chip-specific indirect-access guard.
- Tegra SPI keeps locked `curr_xfer` cleanup.
- TCPM accepts both null and error-pointer role switches.
- NTFS3 keeps sparse-LCN overflow handling.
- ESP4/ESP6 use the newer `xfrm_offload()->proto` interface.
- Open vSwitch keeps strict nested NSH validation.
- IFE keeps normal statement semantics instead of comma chaining.

## Official conflict blocks retained

`pass3-theirs.txt` accepts official conflict blocks where the OnePlus update carries the required fix:

- SVM accesses the LBR-specific VMCB through `svm_get_lbr_vmcb()`.
- AMD display uses `fsleep()` instead of a frame-length busy wait.
- mlx5 rate-limit validation compares the encoded bandwidth value.
- KSMBD releases the session user during logoff.

## Excluded paths

Pass 3 does not include:

- HMBIRD / SCX / SLIM scheduler architecture
- ABI/KMI and AFDO files
- F2FS core paths
- IOMMU and device-tree-sensitive interfaces
- complex Mellanox firmware reset state handling
- Unix-domain socket graph rewrite
- Renesas reset lifecycle changes

These require manual combined resolutions rather than choosing one conflict side.
