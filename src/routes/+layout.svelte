<script lang="ts">
	import favicon from '$lib/assets/sharks.svg';
	import "$lib/dailytrojan-lib/gameStyles.css"
	import "$lib/dailytrojan-lib/icons/tabler-icons.css"
	import "$lib/dailytrojan-lib/fonts/fonts.css"

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Sharks!</title>
</svelte:head>

{@render children?.()}
