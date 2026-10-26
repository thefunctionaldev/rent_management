<template>
	<Teleport to="body">
		<Transition
			enter-active-class="duration-200 ease-out"
			enter-from-class="opacity-0"
			leave-active-class="duration-150 ease-in"
			leave-to-class="opacity-0"
		>
			<div v-if="open" class="fixed inset-0 z-30 bg-slate-900/30" @click="$emit('close')" />
		</Transition>
		<Transition
			enter-active-class="transition duration-250 ease-out"
			enter-from-class="translate-x-full"
			leave-active-class="transition duration-200 ease-in"
			leave-to-class="translate-x-full"
		>
			<aside
				v-if="open"
				class="fixed inset-y-0 right-0 z-30 flex w-full max-w-xl flex-col bg-white shadow-2xl shadow-slate-900/20"
			>
				<slot />
			</aside>
		</Transition>
	</Teleport>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from "vue";

const props = defineProps({ open: Boolean });
const emit = defineEmits(["close"]);

const onKey = (e) => props.open && e.key === "Escape" && emit("close");
onMounted(() => window.addEventListener("keydown", onKey));
onBeforeUnmount(() => window.removeEventListener("keydown", onKey));
</script>
