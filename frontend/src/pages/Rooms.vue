<template>
	<div>
		<PageHeader
			title="Rooms"
			:subtitle="`${rooms.length} rooms across ${floors.length} floor${
				floors.length === 1 ? '' : 's'
			}`"
		>
			<Button :icon="Plus" @click="openDialog('room')">Add room</Button>
			<Button variant="primary" :icon="KeyRound" @click="openDialog('allotRoom')"
				>Allot room</Button
			>
		</PageHeader>

		<div class="mb-5 flex flex-wrap items-center gap-3">
			<div class="flex flex-wrap gap-1.5">
				<button
					v-for="s in statusFilters"
					:key="s.value"
					class="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-sm font-medium ring-1 transition"
					:class="
						status === s.value
							? 'bg-slate-900 text-white ring-slate-900'
							: 'bg-white text-slate-600 ring-slate-200 hover:bg-slate-50'
					"
					@click="status = s.value"
				>
					{{ s.label }}
					<span class="tabular text-xs opacity-60">{{ s.count }}</span>
				</button>
			</div>
			<select v-model="floor" class="input w-auto sm:ml-auto">
				<option value="">All floors</option>
				<option v-for="f in floors" :key="f" :value="f">{{ f }} floor</option>
			</select>
		</div>

		<div
			v-if="loading && !rooms.length"
			class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
		>
			<Skeleton v-for="i in 8" :key="i" class="h-52 rounded-2xl" />
		</div>

		<EmptyState
			v-else-if="!filtered.length"
			:icon="DoorOpen"
			title="No rooms here"
			:description="
				rooms.length ? 'Try a different filter.' : 'Add your first room to get started.'
			"
		>
			<Button v-if="!rooms.length" variant="primary" :icon="Plus" @click="openDialog('room')"
				>Add room</Button
			>
		</EmptyState>

		<div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
			<div
				v-for="room in filtered"
				:key="room.name"
				class="card group flex flex-col p-5 transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-slate-900/5"
			>
				<div class="flex items-start justify-between">
					<div>
						<p class="text-xs font-medium text-slate-500">{{ room.floor }} floor</p>
						<p class="mt-0.5 text-2xl font-semibold tracking-tight">{{ room.name }}</p>
					</div>
					<StatusBadge :status="room.status" />
				</div>
				<div class="mt-3 flex items-center gap-3 text-xs text-slate-500">
					<span v-if="room.room_type">{{ room.room_type }}</span>
					<span
						v-if="room.is_furnished"
						class="inline-flex items-center gap-1"
						title="Furnished"
						><Sofa class="size-3.5"
					/></span>
					<span
						v-if="room.has_attached_bathroom"
						class="inline-flex items-center gap-1"
						title="Attached bathroom"
						><Bath class="size-3.5"
					/></span>
				</div>
				<p class="tabular mt-3 text-sm">
					<span class="text-lg font-semibold">{{ money(room.room_rent) }}</span
					><span class="text-slate-500"> / month</span>
				</p>

				<div class="mt-4 flex-1 border-t border-dashed border-slate-200 pt-4">
					<RouterLink
						v-if="room.tenant"
						:to="`/tenants/${room.tenant}`"
						class="flex items-center gap-2.5 rounded-lg -m-1.5 p-1.5 transition hover:bg-slate-50"
					>
						<Avatar :name="room.tenant_name" size="sm" />
						<div class="min-w-0">
							<p class="truncate text-sm font-medium">{{ room.tenant_name }}</p>
							<p class="text-xs text-slate-500">
								Since {{ date(room.checkin_date) }}
							</p>
						</div>
					</RouterLink>
					<p v-else class="text-sm text-slate-400">No tenant</p>
					<p
						v-if="room.outstanding"
						class="tabular mt-2 inline-flex rounded-md bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700"
					>
						{{ money(room.outstanding) }} due
					</p>
				</div>

				<div class="mt-4 flex gap-2">
					<template v-if="room.status === 'Occupied' && room.current_allotment">
						<Button
							size="sm"
							class="flex-1"
							:icon="FilePlus"
							@click="openDialog('invoice', { allotment: room.current_allotment })"
							>Invoice</Button
						>
						<Button
							size="sm"
							variant="ghost"
							:icon="LogOut"
							@click="
								openDialog('vacate', {
									allotment: room.current_allotment,
									room: room.name,
									tenantName: room.tenant_name,
								})
							"
							>Vacate</Button
						>
					</template>
					<Button
						v-else-if="['Available', 'Reserved'].includes(room.status)"
						size="sm"
						variant="primary"
						class="flex-1"
						:icon="KeyRound"
						@click="openDialog('allotRoom', { room })"
						>Allot</Button
					>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { Bath, DoorOpen, FilePlus, KeyRound, LogOut, Plus, Sofa } from "lucide-vue-next";
import { computed, ref } from "vue";

import { get } from "@/api";
import Avatar from "@/components/Avatar.vue";
import Button from "@/components/Button.vue";
import EmptyState from "@/components/EmptyState.vue";
import PageHeader from "@/components/PageHeader.vue";
import Skeleton from "@/components/Skeleton.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { openDialog } from "@/dialogs";
import { useResource } from "@/useResource";
import { date, money } from "@/utils";

const { data, loading } = useResource(() => get("get_rooms"), { initial: [] });
const rooms = computed(() => data.value || []);
const status = ref("");
const floor = ref("");

const floorOrder = ["Ground", "First", "Second", "Third", "Fourth"];
const floors = computed(() =>
	[...new Set(rooms.value.map((r) => r.floor))].sort(
		(a, b) => floorOrder.indexOf(a) - floorOrder.indexOf(b)
	)
);
const statusFilters = computed(() => [
	{ value: "", label: "All", count: rooms.value.length },
	...["Available", "Occupied", "Reserved", "Under Renovation"].map((s) => ({
		value: s,
		label: s,
		count: rooms.value.filter((r) => r.status === s).length,
	})),
]);
const filtered = computed(() =>
	rooms.value.filter(
		(r) =>
			(!status.value || r.status === status.value) &&
			(!floor.value || r.floor === floor.value)
	)
);
</script>
