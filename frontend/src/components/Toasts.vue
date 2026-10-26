<template>
	<div
		class="pointer-events-none fixed inset-x-0 bottom-0 z-50 flex flex-col items-center gap-2 p-4 sm:items-end"
	>
		<TransitionGroup
			enter-active-class="transition duration-200 ease-out"
			enter-from-class="translate-y-2 opacity-0"
			leave-active-class="transition duration-150 ease-in"
			leave-to-class="opacity-0"
		>
			<div
				v-for="t in toasts"
				:key="t.id"
				class="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-xl bg-slate-900 px-4 py-3 text-sm text-white shadow-xl shadow-slate-900/20"
			>
				<CircleCheck
					v-if="t.type === 'success'"
					class="mt-0.5 size-4 shrink-0 text-emerald-400"
				/>
				<CircleAlert v-else class="mt-0.5 size-4 shrink-0 text-rose-400" />
				<p class="flex-1 whitespace-pre-line">{{ t.message }}</p>
				<button class="text-slate-400 hover:text-white" @click="dismissToast(t.id)">
					<X class="size-4" />
				</button>
			</div>
		</TransitionGroup>
	</div>
</template>

<script setup>
import { CircleAlert, CircleCheck, X } from "lucide-vue-next";

import { dismissToast, toasts } from "@/store";
</script>
