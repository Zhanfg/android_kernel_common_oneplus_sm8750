# OnePlus 13 common 16.0.9.401 conflict resolution

This directory contains auditable resolution inputs for merging official common
commit `e1b346b6b4f4096eb342ae3684838a942fd6f6c4` into custom branch
`6.6-final`.

## Authoritative conflict count

A direct `git merge --no-commit --no-ff` reports **116 unresolved index paths**.
The earlier count of 80 came from a truncated merge-tree report and omitted
conflicts under `kernel/`, `net/`, `sound/`, `init/`, `lib/` and `mm/`.

## Pass 1

`pass1-ours.txt` lists 31 paths whose official base-to-16.0.9.401 delta is
already present in the Linux 6.6.126 custom version, or has been superseded by a
newer equivalent implementation.

The pass does **not** run `git checkout --ours` on whole files. The resolver only
replaces the marked conflict blocks with their local section. Every clean
official hunk that Git merged outside those blocks remains in the worktree.

Evidence used for this pass:

1. The official additions are present in the custom file and official removals
   are already absent or replaced.
2. The conflict-marker version was inspected to confirm the overlap is caused
   by version skew, relocation or a newer local equivalent.
3. `Makefile` keeps Linux 6.6.126 and `KCFLAGS += -D__ANDROID_COMMON_KERNEL__`;
   the official linker and tools changes are already present in the custom file.
4. Scheduler architecture conflicts are deliberately excluded from pass 1.
5. ABI/KMI files are excluded unless their official delta is fully represented
   and the conflict is limited to ordering or a newer local symbol entry.

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
- Do not batch-select ours/theirs for remaining conflicts.
- Keep each resolution pass reproducible in GitHub Actions.
- Do not create a final merge commit until no unmerged index entries remain.
- After resolution, require full pinned-manifest OKI build, ABI/KMI checks and
  OnePlus 13 device validation.
