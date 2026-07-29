# Resolution pass 4: scheduler architecture

Pass 4 applies after the validated pass-1, pass-2 and pass-3 rules.

Expected cumulative result:

```text
116 initial conflicts
85 after pass 1
67 after pass 2
50 after pass 3
17 scheduler paths resolved by pass 4
33 remaining conflicts
```

## Selected architecture

```text
Default scheduler path: fair / wait
Optional custom path: HMBIRD / 风驰
Official CONFIG_SCHED_CLASS_EXT / SCX: disabled
Official CONFIG_SLIM_SCHED: disabled
```

The official and custom implementations both assign scheduler policy number `7`
and modify the same fork, tick, class-selection, cgroup and idle interfaces.
They cannot be enabled together without a separate ABI and scheduler-class
redesign.

## Uniform local paths

`pass4-scheduler-ours.txt` retains HMBIRD-specific conflict blocks in:

- GKI config and scheduler-class linker ordering
- task and scheduler state definitions
- user-visible policy number
- HMBIRD scheduler class, debug, idle and tick hooks
- the 28 conflict blocks in `kernel/sched/core.c`

Clean official hunks outside conflict blocks remain applied.

## Uniform official hook paths

`pass4-scheduler-theirs.txt` imports official Android trace hook declarations and
exports which are independent from enabling SCX.

## Per-block combined files

`pass4-scheduler-plan.json` handles four mixed files:

- `kernel/fork.c`: keep HMBIRD task cleanup and add the official
  `trace_android_vh_put_task()` hook.
- `kernel/sched/build_policy.c`: keep HMBIRD source composition while accepting
  unconditional helper includes.
- `kernel/sched/fair.c`: retain BORE/base-slice behavior and accept the official
  bounded new-idle cost update.
- `kernel/sched/sched.h`: add the official generic cgroup weight helpers, retain
  HMBIRD policy handling, and keep HMBIRD scheduler declarations.

## Validation

The Actions workflow verifies:

- cumulative conflict counts through all four passes;
- no marker or unmerged index remains in the 17 scheduler paths;
- HMBIRD is enabled in `gki_defconfig`;
- official SCX and SLIM are not enabled;
- only `SCHED_HMBIRD=7` remains in the UAPI policy definitions;
- official task release and task-fits-CPU hooks are retained;
- BORE base-slice export, bounded new-idle cost and cgroup weight helpers exist.

This pass does not create a source merge commit. The remaining 33 conflicts and
full OKI validation continue to block integration.
