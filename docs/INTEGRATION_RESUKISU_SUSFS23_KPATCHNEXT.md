# ReSukiSU + SUSFS 2.3 + KPatch-Next

Branch: `integration/resukisu-susfs23-kpatchnext`

Base: `sync/resolution-pass5-compat-16.0.9.401`

## Layering

1. OnePlus official/common compatibility base
2. ReSukiSU root core
3. SUSFS 2.3.x
4. ReSukiSU ↔ SUSFS adaptation
5. KPatch-Next KPM support
6. network / namespace / NTSYNC
7. ADIOS

## KPatch-Next role

KPatch-Next is used only as the KernelPatch/KPM support layer. It does not replace ReSukiSU as the root implementation.

## Safety / reproducibility

- Pin exact upstream commits.
- No branch-floating release builds.
- Keep ReSukiSU, SUSFS and KPatch-Next changes in separate commits.
- Required integration failure stops the build.
- No partially applied source tree may proceed to packaging.
