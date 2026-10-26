<template>
	<div>
		<div class="flex items-center gap-4 text-xs text-slate-500">
			<span v-for="s in series" :key="s.key" class="inline-flex items-center gap-1.5">
				<span class="size-2.5 rounded-sm" :class="s.color" />{{ s.label }}
			</span>
		</div>
		<div class="relative mt-4 h-56">
			<!-- grid lines -->
			<div class="absolute inset-0 bottom-7 flex flex-col justify-between">
				<div
					v-for="tick in ticks"
					:key="tick"
					class="relative border-t border-dashed border-slate-200"
				>
					<span
						class="tabular absolute -top-2.5 left-0 bg-white pr-2 text-[11px] text-slate-400"
					>
						{{ money(tick, { compact: true }) }}
					</span>
				</div>
			</div>
			<!-- bars -->
			<div class="absolute inset-0 left-12 flex items-end gap-2 sm:gap-4">
				<div
					v-for="row in rows"
					:key="row.label"
					class="group flex h-full flex-1 flex-col"
				>
					<div class="flex flex-1 items-end justify-center gap-1 pb-0">
						<div
							v-for="s in series"
							:key="s.key"
							class="relative w-full max-w-7 rounded-t-md transition-all duration-500 group-hover:opacity-90"
							:class="s.color"
							:style="{
								height: `${(row[s.key] / max) * 100}%`,
								minHeight: row[s.key] ? '3px' : '0',
							}"
							:title="`${s.label}: ${money(row[s.key])}`"
						/>
					</div>
					<div class="h-7 pt-2 text-center text-[11px] font-medium text-slate-500">
						{{ row.short }}
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { computed } from "vue";

import { money } from "@/utils";

const props = defineProps({
	rows: { type: Array, required: true },
	series: { type: Array, required: true },
});

const max = computed(() => {
	const highest = Math.max(
		1,
		...props.rows.flatMap((r) => props.series.map((s) => r[s.key] || 0))
	);
	// round the axis up to a "nice" number
	const magnitude = 10 ** Math.floor(Math.log10(highest));
	return Math.ceil(highest / magnitude) * magnitude;
});
const ticks = computed(() => [4, 3, 2, 1, 0].map((i) => (max.value / 4) * i));
</script>
