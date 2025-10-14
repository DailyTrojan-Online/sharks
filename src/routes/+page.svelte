<script lang="ts">
	import { onMount } from "svelte";
	import NumberFlow from "@number-flow/svelte";
	import SharksLogo from "$lib/assets/sharks.svg";
	import { DTGameCore } from "$lib/dailytrojan-lib/gameCore";
	import DTLogo from "$lib/assets/dt-logo.png";
	import FloatingButton from "$lib/components/FloatingButton.svelte";
	import Fin from "$lib/assets/fin.svg";

	import { words } from "$lib/filtered_words";
	import LetterSpringAnimate from "$lib/components/LetterSpringAnimate.svelte";
	import { fly, slide } from "svelte/transition";
	import { cubicIn, cubicOut } from "svelte/easing";
	import { Spring } from "svelte/motion";
	let gameSplash: HTMLElement | null = null;
	let gameDate: HTMLElement | null = null;
	let DTGCore: DTGameCore;

	let totalLetters = 9;
	let maxWordLength = 15;

	let typedWord = $state("");
	let correctWords: string[] = [];

	onMount(() => {
		DTGCore = new DTGameCore(gameSplash, gameDate);
		window.DTGCore = DTGCore;
		init();
		playGame();
	});

	function playGame() {
		DTGCore.hideSplashScreen();
	}
	let allLetters = "ETAOINSHRDLUCMWFGYPBVKJXQZ".split("");
	const weights = [
		12.7, 9.1, 8.2, 7.5, 7.0, 6.7, 6.3, 6.1, 6.0, 4.3, 4.0, 2.8, 2.8, 2.4, 2.4,
		2.2, 2.0, 2.0, 1.9, 1.5, 1.0, 0.8, 0.15, 0.15, 0.1, 0.07,
	];

	// Helper: weighted random choice
	function weightedChoice(arr: string | string[], weights: number[]) {
		const total = weights.reduce((a: any, b: any) => a + b, 0);
		const r = DTGCore.randomFloat() * total;
		let cum = 0;
		for (let i = 0; i < arr.length; i++) {
			cum += weights[i];
			if (r <= cum) return i;
		}
		return arr.length - 1;
	}
	let letters: string[] = $state([]);
	let uses: number[] = $state([]);
	let disabled: boolean[] = $state([]);
	let turn = $state(0);
	let sharkInterval = 4;

	let foundWords: string[] = $state([]);

	let gameOver = $state(false);

	let message = $state("");
	let messageTimeout: number;

	let shakeNo = $state(false);
	let shakeTimeout: number | null = null;

	let totalPoints = $state(0);

	let pointsGiven = $state(0);
	let pointsTimeout: number;

	let coreWordSuccessScaleSpring = new Spring(1, {
		stiffness: 0.1,
		damping: 0.25,
	});
	let coreWordSuccessAngleSpring = new Spring(0, {
		stiffness: 0.1,
		damping: 0.25,
	});

	function showMessage(msg: string) {
		pointsGiven = 0;
		message = msg;
		clearTimeout(messageTimeout);
		messageTimeout = setTimeout(() => {
			message = "";
		}, 2000);
	}

	function givePoints(points: number) {
		message = "";
		pointsGiven = points;
		totalPoints += pointsGiven;
		coreWordSuccessAngleSpring.target = (Math.random() > 0.5 ? 1 : -1) * 5;
		coreWordSuccessScaleSpring.target = 1.5;
		blockInput = true;
		setTimeout(() => {
			coreWordSuccessAngleSpring.target = 0;
			coreWordSuccessScaleSpring.target = 1;
		}, 100);
		clearTimeout(pointsTimeout);
		pointsTimeout = setTimeout(() => {
			blockInput = false;
			pointsGiven = 0;
			transitionClearWord();
			coreWordSuccessScaleSpring.target = 1;
		}, 2000);
	}

	function shakeWordsNo() {
		if (shakeTimeout != null) return;
		shakeNo = true;
		blockInput = true;
		clearTimeout(shakeTimeout ?? -1);
		shakeTimeout = setTimeout(() => {
			shakeNo = false;
			shakeTimeout = null;
			blockInput = false;
		}, 500);
	}

	let transitionClearWordTimeout: number;
	let clearWord = $state(false);

	function transitionClearWord() {
		blockInput = true;
		clearWord = true;
		clearTimeout(transitionClearWordTimeout);

		transitionClearWordTimeout = setTimeout(() => {
			blockInput = false;
			clearWord = false;
			typedWord = "";
		}, 300);
	}

	function init() {
		for (let i = 0; i < totalLetters; i++) {
			let randomIndex = weightedChoice(allLetters, weights);
			letters.push(allLetters[randomIndex]);
			uses.push(0);
			disabled.push(false);

			//remove letter
			allLetters.splice(randomIndex, 1);
		}
		//count how many words can be made with these letters
		let possibleWords = words.filter((word) => {
			if (word.length > maxWordLength) return false;
			for (let char of word.toUpperCase()) {
				if (!letters.includes(char)) {
					return false;
				}
			}
			return true;
		});
		correctWords = possibleWords;
		let maxLength = 0;
		let maxI = 0;
		words.forEach((w, i) => {
			maxLength = Math.max(w.length, maxLength);
			if (w.length == maxLength) maxI = i;
		});
		console.log("Possible words:", possibleWords.length);
		console.log(possibleWords);
		console.log(maxLength, words[maxI]);
	}

	function typeLetter(letter: string) {
		if (letters.includes(letter) && typedWord.length < maxWordLength) {
			typedWord += letter;
		}
	}

	function deleteLetter() {
		typedWord = typedWord.slice(0, -1);
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (blockInput) return;
		const key = event.key.toUpperCase();
		if (key === "BACKSPACE") {
			deleteLetter();
		} else if (key === "ENTER") {
			// Submit word logic here
			checkWord();
		} else if (letters.includes(key) && !disabled[letters.indexOf(key)]) {
			typeLetter(key);
		}
	}

	let blockInput = false;

	function checkWord() {
		if (typedWord == "") return;
		if (!correctWords.includes(typedWord.toLowerCase())) {
			shakeWordsNo();
			showMessage("Word not in word bank.");
			return;
		}
		if (foundWords.includes(typedWord.toLowerCase())) {
			shakeWordsNo();
			showMessage("Word already found.");
			return;
		}
		turn++;
		let originalUses = [...uses];
		for (let i = 0; i < typedWord.length; i++) {
			let j = letters.indexOf(typedWord[i]);
			uses[j] = originalUses[j] + 1;
		}
		let points = 4;
		for (let i = 1; i <= typedWord.length - 4; i++) {
			points += i;
		}
		givePoints(points);
		if (turn % sharkInterval == 0) {
			let max = 0;
			for (let i = 0; i < uses.length; i++) {
				if (uses[i] > max && !disabled[i]) {
					max = uses[i];
				}
			}
			let indexes = [];
			for (let i = 0; i < uses.length; i++) {
				if (uses[i] == max && !disabled[i]) {
					indexes.push(i);
				}
			}
			console.log(indexes);
			let i = indexes[Math.floor(DTGCore.randomInt(0, indexes.length - 1))];
			console.log(i);
			disabled[i] = true;
			//filter out now based on the new disabled;
			correctWords = correctWords.filter((word) => {
				for (let char of word.toUpperCase()) {
					let i = letters.indexOf(char);
					if (disabled[i]) {
						return false;
					}
				}
				return true;
			});
			console.log(correctWords);
		}
		foundWords.push(typedWord.toLowerCase());
		let isUnfoundWord = false;
		correctWords.forEach((word) => {
			if (foundWords.indexOf(word) == -1) {
				isUnfoundWord = true;
			}
		});
		if (!isUnfoundWord) {
			console.log("gameoer!!!!");
			console.log(foundWords.length);
			gameOver = true;
		}
	}
</script>

<svelte:window on:keydown={handleKeyDown} />

<header>
	<img
		id="dt-logo"
		src={DTLogo}
		height="50"
		width="auto"
		style="cursor: pointer;"
		alt="Daily Trojan Logo"
	/>
</header>
<div class="game-splash-wrapper" id="splash" bind:this={gameSplash}>
	<img width="80" src={SharksLogo} alt="Sharks! Logo" />
	<h1>Sharks!</h1>
	<h2 id="game-tagline">
		How many words can you make before the sharks eat your letters?
	</h2>
	<div class="flex-hor">
		<button id="game-back-button">Back</button>
		<button id="game-action-button" onclick={playGame}>Play</button>
	</div>
	<p id="splash-date" bind:this={gameDate}>date</p>
	<p id="splash-date">Game by Noah Pinales</p>
</div>

<main>
	<div class="game-wrapper">
		<h1>Sharks!</h1>
		<div class="top-details">
			<div class="word-container" id="word-container"></div>
			<div class="points-bar">
				<div class="spread">
					<div class="todays-theme">Words Found: {turn}</div>
					<div class="todays-theme">
						<NumberFlow value={totalPoints} /> Points
					</div>
				</div>
			</div>
		</div>
		<div class="game-zone">
			<div class="game-zone-tooltips">
				<div class="tooltip-wrapper">
					{#if message != ""}
						<div
							class="toast"
							in:fly={{ duration: 350, y: 20, easing: cubicOut }}
							out:fly={{ duration: 350, y: 10, easing: cubicIn }}
						>
							{message}
						</div>
					{/if}
				</div>

				<div class="tooltip-wrapper">
					{#if pointsGiven != 0}
						<div
							class="points"
							in:fly={{ duration: 350, y: 20, easing: cubicOut }}
							out:fly={{ duration: 350, y: 10, easing: cubicIn }}
						>
							+{pointsGiven}pts
						</div>
					{/if}
				</div>
			</div>
			<div
				class="current-word"
				class:shake-no={shakeNo}
				class:scale-down={clearWord}
				style:transform={`scale(${coreWordSuccessScaleSpring.current}) rotateZ(${coreWordSuccessAngleSpring.current}deg)`}
			>
				{#each typedWord.split("") as char}
					<LetterSpringAnimate letter={char} />
				{/each}
			</div>
		</div>
		<div class="spacer"></div>
		<div class="letters-wrapper">
			<div class="fin" class:visible={(turn + 1) % sharkInterval == 0}>
				<img width="60" src={Fin} alt="Shark fin" />
			</div>
			<div class="waves">
				<div class="letters">
					{#each letters as letter, i}
						<FloatingButton
							disabled={disabled[i]}
							fear={(turn + 1) % sharkInterval == 0}
							character={letter}
							timesPlayed={uses[i]}
							onclick={() => typeLetter(letter)}
						/>
					{/each}
				</div>
				<div class="flex-hor">
					<button id="delete-button" onclick={deleteLetter}>Delete</button>
					<button id="enter-button">Submit</button>
				</div>
			</div>
		</div>
	</div>
</main>
<div class="modal-wrapper" id="result-modal" class:modal-visible={gameOver}>
	<div class="modal-content">
		<div class="modal-inner">
			<img width="80" src={SharksLogo} />
			<h1 id="modal-title">Great job!</h1>
			<h2>
				You completed Spelling Beads in<br /><strong id="result-time"></strong>.
			</h2>
			<button
				class="close-button"
				onclick={() => {
					gameOver = false;
				}}><i class="ti ti-x"></i></button
			>
			<div class="flex-hor">
				<button><i class="ti ti-device-gamepad"></i>All Games</button>
				<button class="button-share"
					><i class="ti ti-share"></i> Share Results</button
				>
			</div>
			<a
				href="https://docs.google.com/forms/d/e/1FAIpQLSfzk0dC8SsfzfbbCXP4_YOsIw6ja_9zdOIVki3L48HX9QH-pg/viewform?usp=dialog"
				>Help us improve Spelling Beads! <u>Share your feedback.</u></a
			>
		</div>
	</div>
</div>

<style>
	.toast {
		font-family: "Inter", sans-serif;
		border: none;
		background: transparent;
		box-sizing: border-box;
		border: 1px solid var(--outline);
		background: var(--button-bg);
		border-radius: 10px;
		font-size: 16px;
		flex-shrink: 0;
		padding: 10px 15px;
		display: flex;
		gap: 10px;
		justify-content: center;
		align-items: center;
		transition:
			transform 0.3s,
			opacity 0.3s;
		color: var(--button-text);
		height: 45px;
	}
	.points {
		font-family: "Nunito", sans-serif;
		border: none;
		background: transparent;
		box-sizing: border-box;
		border-radius: 10px;
		font-size: 26px;
		font-weight: bold;
		flex-shrink: 0;
		display: flex;
		gap: 10px;
		justify-content: center;
		align-items: center;
		transition:
			transform 0.3s,
			opacity 0.3s;
		height: 45px;
		color: #0084ff;
	}
	.game-zone-tooltips {
		position: relative;
		height: 40px;
	}
	.spread {
		width: 100%;
		display: flex;
		justify-content: space-between;
	}
	.points-bar {
		width: 100%;
	}
	.top-details {
		width: 100%;
	}
	.tooltip-wrapper {
		width: 100%;
		height: 100%;
		position: absolute;
		left: 0;
		top: 0;
		display: flex;
		justify-content: center;
		align-items: center;
	}
	.shake-no {
		animation: shake 0.5s ease-in-out;
		animation-fill-mode: forwards;
	}
	.scale-down {
		animation: scaleDown 0.3s cubic-bezier(0.6, 0, 0.85, 0.23);
		animation-fill-mode: forwards;
	}
	@keyframes shake {
		0% {
			transform: translateX(0);
		}
		25% {
			transform: translateX(10px);
		}
		50% {
			transform: translateX(-5px);
		}
		75% {
			transform: translateX(2px);
		}
		100% {
			transform: translateX(0);
		}
	}
	@keyframes scaleDown {
		from {
			transform: scale(1);
			opacity: 1;
		}
		to {
			transform: scale(0);
			opacity: 0;
		}
	}

	.game-zone {
		width: 100%;
		height: 100%;
		flex-grow: 1;
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		gap: 0px;
	}
	.current-word {
		height: 100px;
		width: 100%;
		flex-grow: 0;
		display: flex;
		justify-content: center;
		align-items: center;
		gap: 0px;
		margin-bottom: 20px;
	}
	.game-wrapper {
		width: 100%;
		height: 100%;
		position: relative;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: space-between;
	}
	.game-splash-wrapper {
		background: #15194c;
		color: white;
	}
	.letters-wrapper {
		width: 100%;
		position: fixed;
		bottom: 0;
		left: 0;
	}
	.spacer {
		height: 350px;
		flex-shrink: 0;
		width: 100%;
	}
	@keyframes waveScroll {
		0% {
			-webkit-mask-position:
				0 0,
				0 0;
		}
		100% {
			-webkit-mask-position:
				225px 0,
				225px 0;
		}
	}
	.waves {
		width: 100%;
		background: linear-gradient(to bottom, #b1e2ff, #62a6ff);
		mask-image: linear-gradient(white, white),
			url("data:image/svg+xml,%3Csvg id='b' data-name='Layer 2' xmlns='http://www.w3.org/2000/svg' width='300' height='40' viewBox='0 0 300 40'%3E%3Cg id='c' data-name='b'%3E%3Cpath d='M0,40c15.793,0,31.587-7.685,42.771-23.056,3.543-4.87,10.914-4.87,14.458,0,22.369,30.742,63.173,30.742,85.542,0,3.543-4.87,10.914-4.87,14.458,0,22.369,30.742,63.173,30.742,85.542,0,3.543-4.87,10.914-4.87,14.458,0,11.185,15.371,26.978,23.056,42.771,23.056V0H0v40Z' fill='%23fff' stroke-width='0'/%3E%3C/g%3E%3C/svg%3E");
		mask-repeat: repeat-x;
		mask-size:
			100% 100%,
			auto 30px; /** width is now 225px*/
		mask-composite: exclude;
		animation: waveScroll 10s linear infinite;
		-webkit-mask-composite: xor;
		padding-bottom: 50px;
		padding-top: 40px;
	}
	.fin {
		position: fixed;
		transform: translate(50%, -25px);
		z-index: -1;

		animation: finSwim 10s ease-in-out infinite;
		z-index: -1;
		opacity: 0;
		transition: 0.3s opacity;
	}
	.fin.visible {
		opacity: 1;
	}
	@keyframes finSwim {
		0% {
			left: 90px;
			transform: rotateY(0deg) translate(0, -25px);
		}
		45% {
			left: calc(100vw - 150px);
			transform: rotateY(0deg) translate(0, -25px);
		}
		50% {
			left: calc(100vw - 150px);
			transform: rotateY(180deg) translate(0, -25px);
		}
		95% {
			left: 90px;
			transform: rotateY(180deg) translate(0, -25px);
		}
		100% {
			left: 90px;
			transform: rotateY(0deg) translate(0, -25px);
		}
	}
	.letters {
		display: flex;
		justify-content: center;
		align-items: flex-start;
		flex-wrap: wrap;
		gap: 20px;
		width: calc(100vw - 80px);
		padding-top: 0px;
		max-width: 500px;
		position: relative;
		margin: auto;
		bottom: 0;
		left: 0;
		padding-bottom: 20px;
		padding-top: 20px;
	}
</style>
