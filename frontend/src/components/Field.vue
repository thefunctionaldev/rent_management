<template>
	<label class="block">
		<span class="label">
			{{ label }}<span v-if="required" class="text-rose-500"> *</span>
		</span>
		<slot />
		<span v-if="hint" class="mt-1 block text-xs text-slate-500">{{ hint }}</span>
	</label>
</template>

<script setup>
defineProps({
	label: { type: String, required: true },
	hint: { type: String, default: "" },
	required: Boolean,
});
</script>
