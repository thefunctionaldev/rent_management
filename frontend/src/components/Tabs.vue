<template>
	<div class="-mb-px flex gap-1 overflow-x-auto border-b border-slate-200">
		<button
			v-for="tab in tabs"
			:key="tab.value"
			class="relative inline-flex items-center gap-2 px-3 pt-1 pb-3 text-sm font-medium whitespace-nowrap transition"
			:class="
				modelValue === tab.value ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700'
			"
			@click="$emit('update:modelValue', tab.value)"
		>
			{{ tab.label }}
			<span
				v-if="tab.count !== undefined"
				class="tabular rounded-full px-1.5 py-px text-[11px]"
				:class="
					modelValue === tab.value
						? 'bg-brand-50 text-brand-700'
						: 'bg-slate-100 text-slate-500'
				"
				>{{ tab.count }}</span
			>
			<span
				v-if="modelValue === tab.value"
				class="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-brand-600"
			/>
		</button>
	</div>
</template>

<script setup>
defineProps({
	tabs: { type: Array, required: true },
	modelValue: { type: [String, Number], default: "" },
});
defineEmits(["update:modelValue"]);
</script>
