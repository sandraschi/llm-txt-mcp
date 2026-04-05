class Game {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = CONSTANTS.SCREEN_WIDTH;
        this.canvas.height = CONSTANTS.SCREEN_HEIGHT;

        this.input = new InputHandler();
        this.audio = new AudioController();
        this.pyramid = new Pyramid();
        this.player = new Qbert();
        this.enemies = [];
        this.discs = [];

        this.score = 0;
        this.level = 1;
        this.round = 1;
        this.lives = 3;

        this.state = 'MENU'; // MENU, PLAYING, GAMEOVER, LEVEL_TRANSITION

        this.lastTime = 0;

        this.input.setMoveCallback((dir) => this.handlePlayerMove(dir));
        this.input.setEnterCallback(() => this.handleEnter());

        this.loop = this.loop.bind(this);
        requestAnimationFrame(this.loop);
    }

    handleEnter() {
        if (this.state === 'MENU' || this.state === 'GAMEOVER') {
            this.startGame();
        }
    }

    startGame() {
        this.state = 'PLAYING';
        this.score = 0;
        this.level = 1;
        this.round = 1;
        this.lives = 3;
        this.resetLevel();

        document.getElementById('start-screen').classList.add('hidden');
        document.getElementById('game-over-screen').classList.add('hidden');
        this.updateUI();
    }

    resetLevel() {
        this.pyramid.init();
        this.player = new Qbert();
        this.enemies = [];
        this.spawnTimer = 0;

        // Spawn Discs
        this.discs = [
            new Disc(3, -1),
            new Disc(5, 6)
        ];

        // Expose game instance for entities to access
        window.gameInstance = this;
    }

    spawnEnemy() {
        const r = Utils.randomInt(0, 100);
        if (r < 40) {
            // Red Ball
            const startCol = Utils.randomInt(0, 1);
            this.enemies.push(new Ball(1, startCol, CONSTANTS.ENTITY_TYPE.RED_BALL));
        } else if (r < 60) {
            // Coily (Purple Ball)
            this.enemies.push(new Coily(1, Utils.randomInt(0, 1)));
        } else if (r < 80) {
            // Slick/Sam
            this.enemies.push(new SlickSam(1, Utils.randomInt(0, 1), CONSTANTS.ENTITY_TYPE.SLICK));
        } else {
            // Green Ball
            this.enemies.push(new GreenBall(1, Utils.randomInt(0, 1)));
        }
    }

    handlePlayerMove(dir) {
        if (this.state !== 'PLAYING') return;
        if (this.player.isMoving) return;

        let dRow = 0;
        let dCol = 0;

        if (dir === CONSTANTS.DIR.DOWN_LEFT) { dRow = 1; dCol = 0; }
        else if (dir === CONSTANTS.DIR.DOWN_RIGHT) { dRow = 1; dCol = 1; }
        else if (dir === CONSTANTS.DIR.UP_LEFT) { dRow = -1; dCol = -1; }
        else if (dir === CONSTANTS.DIR.UP_RIGHT) { dRow = -1; dCol = 0; }

        const targetRow = this.player.gridRow + dRow;
        const targetCol = this.player.gridCol + dCol;

        // Check if valid move (on grid)
        if (Utils.isValidGrid(targetRow, targetCol)) {
            this.player.jump(dRow, dCol);
            this.audio.playHop();

            this.player.onMoveComplete = () => {
                this.onPlayerLand(targetRow, targetCol);
            };
        } else {
            // Check for Disc
            const discIndex = this.discs.findIndex(d => d.gridRow === targetRow && d.gridCol === targetCol);

            if (discIndex !== -1) {
                // Jump onto Disc
                this.player.jump(dRow, dCol);
                this.audio.playHop();
                this.player.onMoveComplete = () => {
                    this.rideDisc(discIndex);
                };
            } else {
                // Jump off pyramid!
                this.player.jump(dRow, dCol);
                this.audio.playHop();
                this.player.onMoveComplete = () => {
                    this.handleDeath();
                };
            }
        }
    }

    rideDisc(index) {
        const disc = this.discs[index];
        this.score += CONSTANTS.SCORE.UNUSED_DISC;

        // Teleport to top (simplified animation)
        this.player.gridRow = 0;
        this.player.gridCol = 0;
        const topPos = Utils.gridToScreen(0, 0);
        this.player.x = topPos.x;
        this.player.y = topPos.y;
        this.player.targetX = topPos.x;
        this.player.targetY = topPos.y;

        // Remove disc
        this.discs.splice(index, 1);

        // Clear enemies
        this.enemies = [];
        this.audio.playTone(1000, 'sine', 0.5);
    }

    onPlayerLand(row, col) {
        this.audio.playLand();
        const tile = this.pyramid.getTile(row, col);
        if (tile && tile.color !== CONSTANTS.COLORS.CUBE_TOP_ACTIVE) {
            tile.color = CONSTANTS.COLORS.CUBE_TOP_ACTIVE;
            this.score += CONSTANTS.SCORE.COLOR_CHANGE;
            this.updateUI();

            if (this.pyramid.isComplete()) {
                this.handleLevelComplete();
            }
        }
    }

    handleDeath() {
        this.audio.playDeath();
        this.audio.playSwear();
        this.lives--;
        this.updateUI();

        if (this.lives <= 0) {
            this.state = 'GAMEOVER';
            document.getElementById('game-over-screen').classList.remove('hidden');
            document.getElementById('final-score').innerText = this.score;
        } else {
            // Respawn
            setTimeout(() => {
                this.player = new Qbert();
                this.enemies = [];
            }, 2000);
        }
    }

    handleLevelComplete() {
        this.audio.playLevelClear();
        this.state = 'LEVEL_TRANSITION';
        setTimeout(() => {
            this.level++;
            this.resetLevel();
            this.state = 'PLAYING';
            this.updateUI();
        }, 2000);
    }

    update(dt) {
        if (this.state === 'PLAYING') {
            this.player.update();
            this.discs.forEach(d => d.update());

            // Spawning
            this.spawnTimer++;
            if (this.spawnTimer > 180) { // Every 3 seconds approx
                this.spawnTimer = 0;
                this.spawnEnemy();
            }

            // Update Enemies
            this.enemies.forEach((e, index) => {
                e.update();
                if (e.dead) {
                    this.enemies.splice(index, 1);
                }
            });

            // Collision Detection
            this.checkCollisions();
        }
    }

    checkCollisions() {
        const pRow = this.player.gridRow;
        const pCol = this.player.gridCol;

        for (let i = this.enemies.length - 1; i >= 0; i--) {
            const e = this.enemies[i];
            if (e.gridRow === pRow && e.gridCol === pCol) {
                if (e.type === CONSTANTS.ENTITY_TYPE.GREEN_BALL) {
                    this.score += CONSTANTS.SCORE.CATCH_GREEN_BALL;
                    this.enemies.splice(i, 1);
                    this.audio.playTone(800, 'sine', 0.2);
                } else if (e.type === CONSTANTS.ENTITY_TYPE.SLICK || e.type === CONSTANTS.ENTITY_TYPE.SAM) {
                    this.score += CONSTANTS.SCORE.CATCH_SLICK_SAM;
                    this.enemies.splice(i, 1);
                    this.audio.playTone(600, 'sine', 0.2);
                } else {
                    // Lethal
                    this.handleDeath();
                    return; // Stop checking
                }
            }
        }
    }

    draw() {
        // Clear
        this.ctx.fillStyle = CONSTANTS.COLORS.BACKGROUND;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.pyramid.draw(this.ctx);

        // Draw entities sorted by Y to handle depth
        const entities = [this.player, ...this.enemies, ...this.discs];
        entities.sort((a, b) => a.y - b.y);
        entities.forEach(e => e.draw(this.ctx));
    }

    loop(timestamp) {
        const dt = timestamp - this.lastTime;
        this.lastTime = timestamp;

        this.update(dt);
        this.draw();

        requestAnimationFrame(this.loop);
    }

    updateUI() {
        document.getElementById('p1-score').innerText = this.score;
        document.getElementById('level-display').innerText = this.level;
        document.getElementById('round-display').innerText = this.round;
    }
}
