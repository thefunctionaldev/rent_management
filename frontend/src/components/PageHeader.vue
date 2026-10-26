<template>
	<div class="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
		<div class="min-w-0">
			<slot name="eyebrow" />
			<h1 class="text-2xl font-semibold tracking-tight text-slate-900">{{ title }}</h1>
			<p v-if="subtitle" class="mt-1 text-sm text-slate-500">{{ subtitle }}</p>
		</div>
		<div v-if="$slots.default" class="flex flex-wrap items-center gap-2">
			<slot />
		</div>
	</div>
</template>

<script setup>
defineProps({
	title: { type: String, required: true },
	subtitle: { type: String, default: "" },
});
</script>
