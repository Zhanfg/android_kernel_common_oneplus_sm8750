// SPDX-License-Identifier: GPL-2.0-or-later

#define KMSG_COMPONENT "zram_wb"
#define pr_fmt(fmt) KMSG_COMPONENT ": " fmt

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/ktime.h>
#include <linux/slab.h>
#include <linux/sysms_finder.h>
#include <linux/workqueue.h>

#include "zram_wb.h"
#include "zms.h"

static bool zram_zms_gc_should_run(const struct zms_stats *stats)
{
	unsigned long partial_pct;
	unsigned long free_pct;

	if (!stats || !stats->nr_blocks || !stats->used_blocks)
		return false;

	if (stats->used_blocks < ZRAM_ZMS_GC_MIN_USED_BLOCKS)
		return false;

	if (stats->pending_free)
		return true;

	if (stats->dirty_blocks)
		return true;

	if (!stats->partial_blocks)
		return false;

	partial_pct = stats->partial_blocks * 100 / stats->used_blocks;
	if (partial_pct >= ZRAM_ZMS_GC_PARTIAL_PCT)
		return true;

	free_pct = stats->free_blocks * 100 / stats->nr_blocks;
	return free_pct <= ZRAM_ZMS_GC_FREE_PCT;
}

int zram_zms_gc_run(struct zram *zram, const char *reason)
{
	struct zms_stats stats;
	struct zms_io io;
	int ret;
	int flush_ret;

	if (!zram || !zram->zms)
		return 0;

	ret = zms_get_stats(zram->zms, &stats);
	if (ret)
		return ret;

	if (!zram_zms_gc_should_run(&stats))
		return 0;

	if (stats.dirty_blocks) {
		flush_ret = zms_flush_all(zram->zms, GFP_NOIO, &io);
		if (flush_ret) {
			pr_warn_ratelimited(
				"zms gc flush failed reason=%s dirty=%lu ret=%d\n",
				reason, stats.dirty_blocks, flush_ret);
			return flush_ret;
		}
	}

	ret = zms_compact(zram->zms, GFP_NOIO, &io);
	if (ret && ret != -EAGAIN)
		pr_warn_ratelimited(
			"zms gc failed reason=%s used=%lu free=%lu partial=%lu dirty=%lu ret=%d\n",
			reason, stats.used_blocks, stats.free_blocks,
			stats.partial_blocks, stats.dirty_blocks, ret);
	else
		pr_debug(
			"zms gc %s reason=%s used=%lu free=%lu partial=%lu dirty=%lu ret=%d\n",
			ret == -EAGAIN ? "continue" : "done", reason,
			stats.used_blocks, stats.free_blocks,
			stats.partial_blocks, stats.dirty_blocks, ret);
	return ret;
}

static void zram_gc_workfn(struct work_struct *work)
{
	struct zram *zram = container_of(work, struct zram, gc_work);
	int ret;

	if (READ_ONCE(zram->gc_stopping))
		goto out;

	down_read(&zram->init_lock);
	if (zram->disksize && zram->zms)
		ret = zram_zms_gc_run(zram, "scheduled");
	else
		ret = 0;
	up_read(&zram->init_lock);

	/*
	 * Compact may return -EAGAIN when time-limited. Keep going while
	 * work is still pending and device is alive.
	 */
	if (ret == -EAGAIN && !READ_ONCE(zram->gc_stopping) &&
	    atomic_read(&zram->gc_pending))
		queue_work(system_unbound_wq, &zram->gc_work);

out:
	if (atomic_dec_and_test(&zram->gc_pending))
		/* nothing */;
}

static void zram_gc_periodic_workfn(struct work_struct *work)
{
	struct zram *zram = container_of(to_delayed_work(work), struct zram,
					 gc_periodic_work);

	if (READ_ONCE(zram->gc_stopping))
		return;

	/* Prefer compact while charging; still run lightly otherwise. */
	if (check_charging_state() || !check_game_pid())
		zram_schedule_gc(zram);

	if (!READ_ONCE(zram->gc_stopping))
		queue_delayed_work(system_unbound_wq, &zram->gc_periodic_work,
				   ZRAM_GC_PERIODIC_INTERVAL);
}

void zram_schedule_gc(struct zram *zram)
{
	if (!zram || !zram->zms || READ_ONCE(zram->gc_stopping))
		return;

	if (atomic_inc_return(&zram->gc_pending) == 1)
		queue_work(system_unbound_wq, &zram->gc_work);
}

void zram_cancel_gc(struct zram *zram)
{
	if (!zram)
		return;

	WRITE_ONCE(zram->gc_stopping, true);
	cancel_delayed_work_sync(&zram->gc_periodic_work);
	cancel_work_sync(&zram->gc_work);
	atomic_set(&zram->gc_pending, 0);
}

void zram_init_gc(struct zram *zram)
{
	INIT_WORK(&zram->gc_work, zram_gc_workfn);
	INIT_DELAYED_WORK(&zram->gc_periodic_work, zram_gc_periodic_workfn);
	atomic_set(&zram->gc_pending, 0);
	WRITE_ONCE(zram->gc_stopping, false);
}

int setup_zram_writeback(void)
{
	return 0;
}

void destroy_zram_writeback(void)
{
}
