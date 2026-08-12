<script lang="ts">
    import { onMount } from "svelte";
    import chroma from "chroma-js";

    let canvas: HTMLCanvasElement;
    let ctx: CanvasRenderingContext2D;

    let particles: {
        x: number;
        y: number;
        color: string;
        opacity: number;
        vX: number;
        vY: number;
    }[] = [];

    onMount(() => {
        canvas.width = window.innerWidth * window.devicePixelRatio;
        canvas.height = window.innerHeight * window.devicePixelRatio;
        ctx = canvas.getContext("2d")!;
        ctx.fillStyle = "red";
        ctx.fillRect(0, 0, 10, 10);
        requestAnimationFrame(render);
    });

    let lastTime = 0;
    let scale = chroma.scale(["#00aaff", "#004080"]).mode("lab").colors(10);
    let debug = $state(false);

    function render(timestamp: number) {
        const deltaTime = (timestamp - lastTime) / 1000;
        lastTime = timestamp;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        let toDelete: number[] = [];
        particles.forEach((p, i) => {
            ctx.fillStyle = p.color;
            p.x += p.vX * deltaTime;
            p.y += p.vY * deltaTime;
            p.vY += gravity * deltaTime;
            if (p.y > window.innerHeight * window.devicePixelRatio)
                toDelete.push(i);

            ctx.fillRect(p.x, p.y, 10, 10);
        });
        toDelete.reverse().forEach((index) => {
            particles.splice(index, 1);
        });
        requestAnimationFrame(render);
    }

    let minVelocity = $state(160);
    let maxVelocity = $state(120);
    let gravity = $state(1200);
    let vUp = $state(320);
    let maxCount = $state(100);

    export function spawnAtPoint(
        x: number,
        y: number,
        w: number,
        h: number,
        count: number,
    ) {
        for (let i = 0; i < count; i++) {
            let magnitude = Math.random() * maxVelocity + minVelocity;
            let direction = Math.random() * Math.PI * 2;
            let vX = Math.cos(direction) * magnitude;
            let vY = Math.sin(direction) * magnitude;
            particles.push({
                x: x + Math.random() * w,
                y: y + Math.random() * h,
                vX,
                vY: vY - vUp,
                color: scale[Math.floor(Math.random() * scale.length)],
                opacity: 1,
            });
        }
    }
</script>

{#if debug}
    <div class="debug">
        <div>
            min
            <input type="range" min={0} max={600} bind:value={minVelocity} />
            {minVelocity}
        </div>
        <div>
            max
            <input type="range" min={0} max={600} bind:value={maxVelocity} />
            {maxVelocity}
        </div>
        <div>
            vUp
            <input type="range" min={0} max={600} bind:value={vUp} />
            {vUp}
        </div>
        <div>
            g
            <input type="range" min={0} max={1000} bind:value={gravity} />
            {gravity}
        </div>
        <div>
            ct
            <input type="range" min={0} max={600} bind:value={maxCount} />
            {maxCount}
        </div>
    </div>
{/if}
<canvas bind:this={canvas}></canvas>

<style>
    canvas {
        width: 100vw;
        height: 100vh;
        position: fixed;
        top: 0;
        left: 0;
        z-index: 98;
        pointer-events: none;
    }
    .debug {
        position: fixed;
        width: 400px;
        bottom: 0;
        left: 0;
        z-index: 99;
        display: flex;
        flex-direction: column;
    }
</style>
