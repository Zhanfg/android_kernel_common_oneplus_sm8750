# Resolution pass 5: general compatibility fixes

Pass 5 applies after the validated scheduler pass.

Expected cumulative result:

```text
116 initial conflicts
85 after pass 1
67 after pass 2
50 after pass 3
33 after scheduler pass 4
10 paths resolved by pass 5
23 remaining conflicts
```

## Local conflict blocks retained

- `.gitignore`: keep project-specific generated-file patterns.
- MIPS R4K TLB: keep the newer local TLB uniquification and cleanup path.
- perf callchain/core: keep `is_user_task()` so the shared definition handles
  kernel threads, user workers and missing user memory consistently.
- MPTCP protocol: keep the stronger fallback lock and `allow_subflows` gate.
- CAKE: keep newer queue/backlog accounting and tree backlog reduction.

## Official conflict blocks retained

- Renesas CAN-FD: use the official common mode helper after channel reset.
- Renesas USB2 PHY: use the channel-owned reset control and official exit-time
  assertion lifecycle.
- MPTCP subflow: import simultaneous-connect fallback propagation.

## Per-block combined file

AMD microcode keeps the local cutoff-table helper while accepting the official
Family 1Ah model-range correction from `0x7f` to `0x6f`.

## Excluded high-risk paths

Pass 5 leaves 23 paths covering:

- ABI/KMI, OPlus symbol lists, protected exports and AFDO
- IOMMU and Android vendor memory hooks
- F2FS/EXT4 and pageblock state
- Mellanox firmware reset lifecycle
- Unix-domain socket graph collection

These require ABI regeneration, full-tree build context or combined semantic
resolutions rather than marker-side selection.
