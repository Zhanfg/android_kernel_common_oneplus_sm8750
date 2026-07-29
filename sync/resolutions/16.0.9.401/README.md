# OnePlus 13 common 16.0.9.401 conflict resolution

This directory contains auditable resolution inputs for merging official common
commit `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` into custom branch
`6.6-final`.

## Authoritative conflict count

A direct `git merge --no-commit --no-ff` reports **116 unresolved index paths**.
The earlier count of 80 came from a truncated merge-tree report and omitted
conflicts under `kernel/`, `net/`, `sound/`, `init/`, `lib/` and `mm/`.

## Resolution method

The resolver does not check out an entire file from one side. It replaces only
standard conflict-marker blocks with the selected section. Text outside the
markers remains unchanged, preserving all clean official hunks already merged by
Git.

Every pass must:

1. start from the same fixed local and official SHAs;
2. reproduce the expected incoming conflict count;
3. resolve only paths listed in the pass files;
4. verify that listed files contain no conflict markers and are no longer
   unmerged in the index;
5. reproduce the expected remaining-conflict count;
6. abort the temporary merge without creating a source integration commit.

## Pass 1

Files:

```text
pass1-ours.txt
```

The 31 paths contain official changes already present in the Linux 6.6.126
custom file, or a newer equivalent local implementation. The validated result is:

```text
116 initial conflicts
31 resolved paths
85 remaining conflicts
```

Scheduler architecture conflicts and high-risk ABI/KMI files are excluded.

## Pass 2

Files:

```text
pass2-ours.txt
pass2-theirs.txt
```

Pass 2 adds 18 paths whose conflict blocks have clear local or official
semantics:

- LoongArch BPF index zero-extension already required by the newer local JIT.
- GPIO regmap failure must remove an already registered gpiochip before freeing
  memory.
- USB HID keeps the downstream malformed-descriptor compatibility handling.
- OCC keeps compile-time format checking.
- BTRFS keeps the conflicting-inode safety gate.
- HFS+ uses the caller-provided maximum length instead of a fixed constant.
- NFSD and migration code keep newer local function signatures and lock handling.
- ETS and vsock keep newer queue/state handling.
- PCM header, OSS caller and PCM implementation stay on the same error-returning
  API; USB endpoint keeps the unlock path on validation failure.
- Battery delayed-work registration keeps return-value checking.
- Raw Gadget keeps the bounded allocation limit.
- Broadcom USB3 keeps the official enum-typed assignment.

Expected cumulative result:

```text
116 initial conflicts
85 after pass 1
18 resolved by pass 2
67 remaining conflicts
```

Pass 2 deliberately excludes scheduler architecture, core ABI/KMI, AFDO, F2FS
core, IOMMU and other device-sensitive conflicts.

## Unresolved architecture blocker

Official 16.0.9.401 enables `CONFIG_SCHED_CLASS_EXT` / SCX and
`CONFIG_SLIM_SCHED`. The custom HMBIRD implementation uses the same scheduler
policy number (`7`) and replaces many of the same fork, tick, class-selection
and cgroup paths. These implementations cannot be combined by choosing one side
of the conflict.

A separate design decision and code port are required before resolving:

- `arch/arm64/configs/gki_defconfig`
- `include/uapi/linux/sched.h`
- `include/linux/sched/task.h`
- `kernel/Kconfig.preempt`
- `kernel/sched/*`
- related task, fork, tick and vendor-hook paths

## Safety rules

- Do not merge the official 6.6.118 tree over the custom 6.6.126 tree.
- Do not batch-select one side for unreviewed conflicts.
- Keep each resolution pass reproducible in GitHub Actions.
- Do not create a final merge commit until no unmerged index entries remain.
- After resolution, require a full pinned-manifest OKI build, ABI/KMI checks and
  OnePlus 13 device validation.
