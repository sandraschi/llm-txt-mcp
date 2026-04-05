class AudioController {
    constructor() {
        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        this.masterGain = this.ctx.createGain();
        this.masterGain.gain.value = 0.3; // Keep it reasonable
        this.masterGain.connect(this.ctx.destination);
    }

    playTone(freq, type, duration, startTime = 0) {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();

        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime + startTime);

        gain.gain.setValueAtTime(1, this.ctx.currentTime + startTime);
        gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + startTime + duration);

        osc.connect(gain);
        gain.connect(this.masterGain);

        osc.start(this.ctx.currentTime + startTime);
        osc.stop(this.ctx.currentTime + startTime + duration);
    }

    playHop() {
        // "Boing" sound
        this.playTone(300, 'sine', 0.1);
        // Pitch bend up
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.frequency.setValueAtTime(200, this.ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(600, this.ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.5, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0, this.ctx.currentTime + 0.1);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 0.1);
    }

    playLand() {
        // Thud
        this.playTone(100, 'square', 0.05);
    }

    playDeath() {
        // Falling whistle
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.frequency.setValueAtTime(800, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(100, this.ctx.currentTime + 1.0);
        gain.gain.setValueAtTime(0.5, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0, this.ctx.currentTime + 1.0);
        osc.connect(gain);
        gain.connect(this.masterGain);
        osc.start();
        osc.stop(this.ctx.currentTime + 1.0);

        // Crash at end
        setTimeout(() => this.playTone(50, 'sawtooth', 0.2), 1000);
    }

    playSwear() {
        // Garbled noise
        for (let i = 0; i < 5; i++) {
            this.playTone(200 + Math.random() * 400, 'sawtooth', 0.05, i * 0.06);
        }
    }

    playCoilyJump() {
        this.playTone(150, 'sawtooth', 0.1);
    }

    playLevelClear() {
        // Simple jingle
        [523.25, 659.25, 783.99, 1046.50].forEach((freq, i) => {
            this.playTone(freq, 'square', 0.2, i * 0.2);
        });
    }
}
