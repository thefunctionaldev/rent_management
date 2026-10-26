<template>
	<Modal
		open
		title="Add room"
		subtitle="Add a room or unit to the property"
		@close="$emit('close')"
	>
		<form id="room-form" class="space-y-4" @submit.prevent="save">
			<div class="grid gap-4 sm:grid-cols-2">
				<Field label="Room number" required>
					<input
						v-model="form.room_number"
						class="input"
						required
						autofocus
						placeholder="101"
					/>
				</Field>
				<Field label="Floor" required>
					<select v-model="form.floor" class="input" required>
						<option v-for="f in floors" :key="f">{{ f }}</option>
					</select>
				</Field>
			</div>

			<div v-if="!newType">
				<div class="mb-1.5 flex items-center justify-between">
					<span class="label mb-0">Room type</span>
					<button
						type="button"
						class="text-xs font-medium text-brand-600 hover:underline"
						@click="newType = true"
					>
						+ New type
					</button>
				</div>
				<select v-model="form.room_type" class="input">
					<option value="">—</option>
					<option v-for="t in types.data.value || []" :key="t.name" :value="t.name">
						{{ t.name }} · {{ money(t.standard_rent) }}/mo
					</option>
				</select>
			</div>
			<div
				v-else
				class="space-y-4 rounded-xl border border-dashed border-slate-300 bg-slate-50/60 p-4"
			>
				<div class="flex items-center justify-between">
					<p class="text-sm font-medium text-slate-900">New room type</p>
					<button
						type="button"
						class="text-xs text-slate-500 hover:underline"
						@click="newType = false"
					>
						Pick existing
					</button>
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<Field label="Type name" required>
						<input
							v-model="type.type"
							class="input"
							required
							placeholder="Single Room"
						/>
					</Field>
					<Field label="Standard rent" required>
						<input
							v-model="type.standard_rent"
							class="input tabular"
							type="number"
							min="0"
							required
						/>
					</Field>
					<Field label="Security deposit">
						<input
							v-model="type.security_deposit"
							class="input tabular"
							type="number"
							min="0"
						/>
					</Field>
					<div class="flex flex-col justify-end gap-2 pb-1 text-sm text-slate-700">
						<label class="flex items-center gap-2"
							><input
								v-model="type.is_furnished"
								type="checkbox"
								class="accent-brand-600"
							/>
							Furnished</label
						>
						<label class="flex items-center gap-2"
							><input
								v-model="type.has_attached_bathroom"
								type="checkbox"
								class="accent-brand-600"
							/>
							Attached bathroom</label
						>
					</div>
				</div>
			</div>

			<Field label="Monthly rent" hint="Leave blank to use the room type's standard rent">
				<input
					v-model="form.room_rent"
					class="input tabular"
					type="number"
					min="0"
					:placeholder="defaultRent"
				/>
			</Field>
		</form>
		<template #footer>
			<Button @click="$emit('close')">Cancel</Button>
			<Button variant="primary" type="submit" form="room-form" :loading="loading"
				>Add room</Button
			>
		</template>
	</Modal>
</template>

<script setup>
import { computed, reactive, ref } from "vue";

import { get, post } from "@/api";
import Button from "@/components/Button.vue";
import Field from "@/components/Field.vue";
import Modal from "@/components/Modal.vue";
import { useAction, useResource } from "@/useResource";
import { money } from "@/utils";

const emit = defineEmits(["close"]);
const floors = ["Ground", "First", "Second", "Third", "Fourth"];

const form = reactive({ room_number: "", floor: "Ground", room_type: "", room_rent: "" });
const type = reactive({
	type: "",
	standard_rent: "",
	security_deposit: "",
	is_furnished: false,
	has_attached_bathroom: false,
});
const newType = ref(false);
const types = useResource(() => get("get_room_types"));

const defaultRent = computed(() => {
	if (newType.value) return type.standard_rent;
	const selected = types.data.value?.find((t) => t.name === form.room_type);
	return selected ? String(selected.standard_rent) : "";
});

const { loading, run } = useAction(
	async () => {
		let roomType = form.room_type;
		if (newType.value) {
			roomType = await post("create_room_type", {
				data: {
					...type,
					deposit_applicable: type.security_deposit > 0 ? 1 : 0,
					is_furnished: type.is_furnished ? 1 : 0,
					has_attached_bathroom: type.has_attached_bathroom ? 1 : 0,
				},
			});
		}
		return post("create_room", {
			data: {
				...form,
				room_type: roomType || null,
				room_rent: form.room_rent || null,
				status: "Available",
			},
		});
	},
	{ success: (name) => `Room ${name} added` }
);

async function save() {
	await run();
	emit("close");
}
</script>
