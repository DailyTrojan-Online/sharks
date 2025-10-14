<script lang="ts">
	import { onMount } from "svelte";
	import { Spring } from "svelte/motion";

	let { letter }: { letter: string } = $props();
	let letterElement: HTMLDivElement | null = $state(null);
	let letterElementWidth = $state(0);
	let letterWidthSpring = new Spring(0, {
		stiffness: 0.1,
		damping: 0.2,
	});
	let letterScale = new Spring(0.2, {
		stiffness: 0.1,
		damping: 0.25,
	});
	let letterAngle = new Spring(-80 * (Math.random() - 0.5), {
		stiffness: 0.1,
		damping: 0.15,
	});

	onMount(() => {
		if (letterElement) {
			letterElementWidth = letterElement.offsetWidth;
			letterWidthSpring.target = letterElementWidth;
			letterScale.target = 1;
			letterAngle.target = 0;
		}
	});
</script>

<svelte:window
	onresize={() => {
		letterElementWidth = letterElement?.offsetWidth ?? 0;
			letterWidthSpring.target = letterElementWidth;
	}}
/>

<div class="letter-wrapper" style:width={`${letterWidthSpring.current}px`}>
	<div
		class="letter"
		bind:this={letterElement}
		style:transform={`translate(-50%, -50%) rotateZ(${letterAngle.current}deg) scale(${letterScale.current})`}
	>
		{letter}
	</div>
</div>

<style>
	.letter-wrapper {
		display: inline-block;
		position: relative;
		perspective: 1000px;
		height: 20px;
	}
	.letter {
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		font-size: 50px;
		font-family: "Nunito", sans-serif;
		font-weight: bold;
	}
	@media (max-width: 500px) {
		.letter {
			font-size: 40px;
		}
	}
</style>
