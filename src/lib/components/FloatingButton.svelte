<script lang="ts">
	import chroma from "chroma-js";
	let {
		character,
		timesPlayed = $bindable(0),
		disabled,
		fear,
		onclick,
	}: {
		character: string;
		timesPlayed: number;
		disabled: boolean;
		fear: boolean;
		onclick?: () => void;
	} = $props();

	let scale = chroma.scale(["#00aaff", "#004080"]).mode("lab").colors(10);
	import { onMount } from "svelte";

	// Simple Perlin noise implementation
	const permutation = new Uint8Array(512);
	const p = new Uint8Array(256);

	for (let i = 0; i < 256; i++) p[i] = i;
	for (let i = 0; i < 256; i++) {
		const j = Math.floor(Math.random() * 256);
		[p[i], p[j]] = [p[j], p[i]];
	}
	for (let i = 0; i < 512; i++) permutation[i] = p[i & 255];

	function fade(t: number) {
		return t * t * t * (t * (t * 6 - 15) + 10);
	}

	function lerp(a: number, b: number, t: number) {
		return a + t * (b - a);
	}

	function grad(hash: number, x: number) {
		// 1D gradient: either +x or -x depending on lowest bit of hash
		return (hash & 1) === 0 ? x : -x;
	}

	function perlin(x: number) {
		const xi = Math.floor(x) & 255;
		const xf = x - Math.floor(x);
		const u = fade(xf);

		const g1 = grad(permutation[xi], xf);
		const g2 = grad(permutation[xi + 1], xf - 1);

		return lerp(g1, g2, u);
	}

	let angle = $state(0);
	let translationY = $state(0);

	let t = 0;
	let animationFrame: number;

	let lastTime: number = performance.now();

	function animate() {
		const now = performance.now();
		const delta = (now - (lastTime ?? now)) / 1000; // seconds
		lastTime = now;
		t += delta * 0.5; // 1.5 = speed factor, adjust as needed
		if (fear) {
		}
		angle = perlin(t) * 12;
		translationY = perlin(t + 100) * 4; // -10px to +10px
		animationFrame = requestAnimationFrame(animate);
	}

	onMount(() => {
		animate();
		return () => cancelAnimationFrame(animationFrame);
	});
</script>

<div
	class="floating-button-wrapper"
	style:transform={`translateY(${translationY}px) rotate(${angle}deg)`}
>
	<button
		{disabled}
		class="floating-button"
		{onclick}
		style:background={scale[Math.min(timesPlayed, 9)]}>{character}</button
	>
</div>

<style>
	.floating-button-wrapper {
		height: 80px;
		width: 80px;
		z-index: 10;
		display: flex;
		align-items: center;
		justify-content: center;
		position: relative;
	}
	.floating-button {
		background: #007acc;
		border: none;
		border-radius: 12px;
		color: white;
		cursor: pointer;
		font-size: 2.15rem;
		height: 100%;
		width: 100%;
		flex-shrink: 0;
		display: flex;
		font-weight: bold;
		font-family: "Nunito";
		justify-content: center;
		align-items: center;
		transition:
			background 0.3s,
			transform 0.2s;
		z-index: 10;
		box-shadow: inset 0 -6px 0 rgba(8, 0, 39, 0.2);
	}
	.floating-button:disabled {
		background: transparent !important;
		border: 4px dashed rgb(75, 90, 123);
		color: rgb(75, 90, 123);
		opacity: 0.5;
		cursor: unset !important;
	}

	.floating-button:hover {
		transform: scale(1.05);
	}

	.floating-button:active {
		transform: scale(0.9);
	}

	.floating-button:disabled:hover {
		transform: scale(1);
	}

	.floating-button:disabled:active {
		transform: scale(1);
	}

	@media (max-width: 575px) {
		.floating-button {
			font-size: 2rem;
		}
		.floating-button-wrapper {
			height: 65px;
			width: 65px;
		}
	}
</style>
