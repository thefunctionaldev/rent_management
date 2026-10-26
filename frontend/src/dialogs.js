import { reactive } from "vue";

// One place to open any dialog from any page: openDialog("recordPayment", { invoice })
export const dialog = reactive({ name: null, props: {} });

export function openDialog(name, props = {}) {
	dialog.props = props;
	dialog.name = name;
}

export function closeDialog() {
	dialog.name = null;
}
