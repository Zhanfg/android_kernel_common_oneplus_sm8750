/* SPDX-License-Identifier: GPL-2.0-or-later */

#ifndef _ZRAM_WRITEBACK_H_
#define _ZRAM_WRITEBACK_H_

#include "zram_drv.h"

/* GC constants */
#define ZRAM_GC_PERIODIC_INTERVAL	(15 * HZ)
#define ZRAM_ZMS_GC_MIN_USED_BLOCKS	16UL
#define ZRAM_ZMS_GC_PARTIAL_PCT		25UL
#define ZRAM_ZMS_GC_FREE_PCT		15UL
#define ZRAM_ZMS_WB_MIN_FREE_BLOCKS	8UL
#define ZRAM_WB_BATCH_MAX		32U

#define ZRAM_ZMS_PREFETCH_MAX		2U
#define ZRAM_PREFETCH_NEIGHBOR_SCAN_MAX	4U
#define ZRAM_PREFETCH_TTL_MS		1000U

#if IS_ENABLED(CONFIG_ZRAM_WRITEBACK)
int setup_zram_writeback(void);
void destroy_zram_writeback(void);
void zram_init_gc(struct zram *zram);
void zram_cancel_gc(struct zram *zram);
void zram_schedule_gc(struct zram *zram);
int zram_zms_gc_run(struct zram *zram, const char *reason);
#else
static inline int setup_zram_writeback(void) { return 0; }
static inline void destroy_zram_writeback(void) {}
static inline void zram_init_gc(struct zram *zram) {}
static inline void zram_cancel_gc(struct zram *zram) {}
static inline void zram_schedule_gc(struct zram *zram) {}
static inline int zram_zms_gc_run(struct zram *zram, const char *reason)
{
	return 0;
}
#endif

#endif /* _ZRAM_WRITEBACK_H_ */
