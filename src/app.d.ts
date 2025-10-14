// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

// Extend the Window interface to include DTGameCore
declare global {
	interface Window {
		DTGCore: DTGameCore;
	}
}

export {};
