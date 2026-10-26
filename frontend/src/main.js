import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";
import { loadBoot } from "./store";
import "./style.css";

loadBoot()
	.catch(() => {
		// not logged in, or no access: send to the login page
		window.location.href = `/login?redirect-to=${encodeURIComponent(
			window.location.pathname
		)}`;
	})
	.finally(() => createApp(App).use(router).mount("#app"));
