<template>
	<div class="relative">
		<Search
			class="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400"
		/>
		<input
			:value="modelValue"
			type="search"
			class="input pl-9"
			:placeholder="placeholder"
			@input="$emit('update:modelValue', $event.target.value)"
		/>
	</div>
</template>

<script setup>
import { Search } from "lucide-vue-next";

defineProps({
	modelValue: { type: String, default: "" },
	placeholder: { type: String, default: "Search" },
});
defineEmits(["update:modelValue"]);
</script>
