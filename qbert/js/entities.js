class Entity {
    constructor(row, col, type) {
        this.gridRow = row;
        this.gridCol = col;
        this.type = type;

        // Screen position (for smooth animation)
        const pos = Utils.gridToScreen(row, col);
        this.x = pos.x;
        this.y = pos.y;
        this.targetX = pos.x;
        this.targetY = pos.y;

        this.isMoving = false;
        this.moveProgress = 0;
        this.moveSpeed = 0.1; // Speed of animation (0 to 1 per frame/tick)

        this.dead = false;
    }

    update() {
        if (this.isMoving) {
            this.moveProgress += this.moveSpeed;
            if (this.moveProgress >= 1) {
                this.moveProgress = 0;
                this.isMoving = false;
                this.x = this.targetX;
                this.y = this.targetY;
                this.onMoveComplete();
            } else {
                // Lerp
                this.x = this.x + (this.targetX - this.x) * this.moveSpeed;
                this.y = this.y + (this.targetY - this.y) * this.moveSpeed;
                // Add hop arc
                // Simple jump height
                // const jumpHeight = 20;
                // const jumpY = Math.sin(this.moveProgress * Math.PI) * jumpHeight;
                // this.y -= jumpY; // Visual only, might complicate drawing if we don't separate visual Y
            }
        }
    }

    draw(ctx) {
        // Placeholder draw
        const pos = Utils.gridToScreen(this.gridRow, this.gridCol);
        // Use current x/y for animation

        // Draw shadow
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.beginPath();
        ctx.ellipse(this.x, this.y + 10, 10, 5, 0, 0, Math.PI * 2);
        ctx.fill();

        // Draw Entity Body
        ctx.fillStyle = this.getColor();
        ctx.beginPath();
        ctx.arc(this.x, this.y - 10, 15, 0, Math.PI * 2);
        ctx.fill();
    }

    getColor() {
        return '#FFF';
    }

    jump(dRow, dCol) {
        if (this.isMoving) return;

        this.gridRow += dRow;
        this.gridCol += dCol;

        const pos = Utils.gridToScreen(this.gridRow, this.gridCol);
        this.targetX = pos.x;
        this.targetY = pos.y;
        this.isMoving = true;
    }

    onMoveComplete() { }
}

class Qbert extends Entity {
    constructor() {
        super(0, 0, CONSTANTS.ENTITY_TYPE.PLAYER);
        this.nextMove = null;
    }

    getColor() {
        return CONSTANTS.COLORS.QBERT;
    }

    draw(ctx) {
        // Draw Q*bert (Orange blob with nose)
        const x = this.x;
        const y = this.y - 15; // Lift up a bit

        // Body
        ctx.fillStyle = this.getColor();
        ctx.beginPath();
        ctx.arc(x, y, 14, 0, Math.PI * 2);
        ctx.fill();

        // Nose
        ctx.beginPath();
        ctx.moveTo(x + 10, y);
        ctx.lineTo(x + 25, y + 5);
        ctx.lineTo(x + 10, y + 10);
        ctx.fill();

        // Eyes
        ctx.fillStyle = '#FFF';
        ctx.beginPath();
        ctx.arc(x - 4, y - 4, 4, 0, Math.PI * 2);
        ctx.arc(x + 6, y - 4, 4, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.arc(x - 4, y - 4, 1.5, 0, Math.PI * 2);
        ctx.arc(x + 6, y - 4, 1.5, 0, Math.PI * 2);
        ctx.fill();
    }
}

class Enemy extends Entity {
    constructor(row, col, type) {
        super(row, col, type);
        this.moveTimer = 0;
        this.moveInterval = 60; // Frames between moves (1 second at 60fps)
    }

    update() {
        super.update();
        if (!this.isMoving && !this.dead) {
            this.moveTimer++;
            if (this.moveTimer >= this.moveInterval) {
                this.moveTimer = 0;
                this.decideMove();
            }
        }
    }

    decideMove() {
        // Base random move downwards
        const moves = [
            { dRow: 1, dCol: 0 }, // Down-Left
            { dRow: 1, dCol: 1 }  // Down-Right
        ];
        const move = Utils.randomChoice(moves);
        this.jump(move.dRow, move.dCol);
    }

    jump(dRow, dCol) {
        super.jump(dRow, dCol);
        // Check if fell off world
        if (!Utils.isValidGrid(this.gridRow, this.gridCol)) {
            this.dead = true;
            // Remove self from game (handled in game loop)
        }
    }
}

class Ball extends Enemy {
    constructor(row, col, type) {
        super(row, col, type);
        this.moveInterval = 45;
    }

    getColor() {
        return this.type === CONSTANTS.ENTITY_TYPE.RED_BALL ? CONSTANTS.COLORS.ENEMY_RED : CONSTANTS.COLORS.ENEMY_PURPLE;
    }

    draw(ctx) {
        const x = this.x;
        const y = this.y - 10;
        ctx.fillStyle = this.getColor();
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, Math.PI * 2);
        ctx.fill();
    }
}

class Coily extends Enemy {
    constructor(row, col) {
        super(row, col, CONSTANTS.ENTITY_TYPE.COILY);
        this.isSnake = false; // Starts as purple ball
        this.moveInterval = 40;
    }

    getColor() {
        return CONSTANTS.COLORS.ENEMY_PURPLE;
    }

    decideMove() {
        if (!this.isSnake) {
            // Ball behavior: bounce down
            super.decideMove();
            // Check if reached bottom
            if (this.gridRow === CONSTANTS.GRID_ROWS - 1) {
                this.isSnake = true;
                this.moveInterval = 50; // Slower as snake? Or faster?
                // Wait a bit before transforming?
            }
        } else {
            // Snake behavior: Chase Q*bert
            // We need reference to player position. 
            // For now, let's assume we can access it globally or pass it.
            // Hack: Access global game instance or pass in update.
            // Let's make decideMove take a target.

            // Simple chase logic: minimize distance
            // Available moves: All 4 directions? No, Coily hops.
            // Usually Coily can move in all 4 diagonal directions.

            const target = window.gameInstance?.player; // Global hack for now
            if (!target) return;

            const tr = target.gridRow;
            const tc = target.gridCol;
            const r = this.gridRow;
            const c = this.gridCol;

            let bestMove = null;
            let minDist = Infinity;

            const possibleMoves = [
                { dRow: 1, dCol: 0 }, { dRow: 1, dCol: 1 },
                { dRow: -1, dCol: -1 }, { dRow: -1, dCol: 0 }
            ];

            // Filter valid moves (stay on pyramid)
            const validMoves = possibleMoves.filter(m => Utils.isValidGrid(r + m.dRow, c + m.dCol));

            validMoves.forEach(m => {
                const dist = Math.abs((r + m.dRow) - tr) + Math.abs((c + m.dCol) - tc);
                if (dist < minDist) {
                    minDist = dist;
                    bestMove = m;
                }
            });

            if (bestMove) {
                this.jump(bestMove.dRow, bestMove.dCol);
            }
        }
    }

    draw(ctx) {
        const x = this.x;
        const y = this.y - 10;

        ctx.fillStyle = this.getColor();

        if (!this.isSnake) {
            ctx.beginPath();
            ctx.arc(x, y, 10, 0, Math.PI * 2);
            ctx.fill();
        } else {
            // Draw Snake (Coily)
            // Spring shape? Or just a head with body.
            ctx.beginPath();
            ctx.arc(x, y - 5, 12, 0, Math.PI * 2); // Head
            ctx.fill();

            // Eyes
            ctx.fillStyle = '#FFF';
            ctx.beginPath();
            ctx.arc(x - 4, y - 8, 3, 0, Math.PI * 2);
            ctx.arc(x + 4, y - 8, 3, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#000';
            ctx.beginPath();
            ctx.arc(x - 4, y - 8, 1, 0, Math.PI * 2);
            ctx.arc(x + 4, y - 8, 1, 0, Math.PI * 2);
            ctx.fill();

            // Coils
            ctx.strokeStyle = this.getColor();
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.lineTo(x - 5, y + 10);
            ctx.lineTo(x + 5, y + 10);
            ctx.stroke();
        }
    }
}

class UggWrongway extends Enemy {
    constructor(row, col, type) {
        super(row, col, type);
        this.moveInterval = 45;
        // Ugg (Right side, moves Left/Up-Left)
        // Wrongway (Left side, moves Right/Up-Right)
        // They move on "sides" of cubes.
        // This is tricky visually. We might just render them offset.
    }

    getColor() {
        return CONSTANTS.COLORS.ENEMY_PURPLE;
    }

    decideMove() {
        // Simplified: They move horizontally or upwards
        let moves = [];
        if (this.type === CONSTANTS.ENTITY_TYPE.UGG) {
            // Moves Left or Up-Left
            moves = [{ dRow: -1, dCol: -1 }, { dRow: 0, dCol: -1 }]; // Wait, grid logic
            // Ugg starts bottom right (Row 6, Col 6).
            // Moves to Row 6, Col 5? Or Row 5, Col 5?
            // Let's just make them move randomly Up/Sideways
            moves = [
                { dRow: -1, dCol: -1 }, // Up-Left
                { dRow: 0, dCol: -1 }   // Left (Fake move? No, grid doesn't support direct left)
                // Direct Left in grid: (r, c) -> (r, c-1)
                // Is (r, c-1) valid? Yes, if c > 0.
            ];
        } else {
            // Wrongway starts bottom left (Row 6, Col 0)
            // Moves Right or Up-Right
            moves = [
                { dRow: -1, dCol: 0 }, // Up-Right
                { dRow: 0, dCol: 1 }   // Right
            ];
        }

        const move = Utils.randomChoice(moves);
        // They can move off grid (sides)
        this.jump(move.dRow, move.dCol);
    }

    draw(ctx) {
        const x = this.x;
        const y = this.y - 5;
        ctx.fillStyle = this.getColor();
        // Draw weird shape
        ctx.beginPath();
        ctx.moveTo(x, y - 15);
        ctx.lineTo(x + 10, y);
        ctx.lineTo(x - 10, y);
        ctx.fill();

        // Eyes on side
        ctx.fillStyle = '#FFF';
        ctx.beginPath();
        ctx.arc(x, y - 5, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.arc(x, y - 5, 1.5, 0, Math.PI * 2);
        ctx.fill();
    }
}

class SlickSam extends Enemy {
    constructor(row, col, type) {
        super(row, col, type);
        this.moveInterval = 50;
    }

    getColor() {
        return CONSTANTS.COLORS.ENEMY_GREEN;
    }

    onMoveComplete() {
        // Revert tile color
        const tile = window.gameInstance?.pyramid.getTile(this.gridRow, this.gridCol);
        if (tile) {
            tile.color = CONSTANTS.COLORS.CUBE_TOP_INACTIVE; // Reset to start
        }
    }

    draw(ctx) {
        const x = this.x;
        const y = this.y - 10;
        ctx.fillStyle = this.getColor();
        ctx.beginPath();
        ctx.fillRect(x - 6, y - 12, 12, 12);

        // Sunglasses for Slick
        if (this.type === CONSTANTS.ENTITY_TYPE.SLICK) {
            ctx.fillStyle = '#000';
            ctx.fillRect(x - 6, y - 10, 12, 4);
        }
    }
}

class GreenBall extends Enemy {
    constructor(row, col) {
        super(row, col, CONSTANTS.ENTITY_TYPE.GREEN_BALL);
        this.moveInterval = 45;
    }

    getColor() {
        return CONSTANTS.COLORS.ENEMY_GREEN;
    }

    draw(ctx) {
        const x = this.x;
        const y = this.y - 10;
        ctx.fillStyle = this.getColor();
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, Math.PI * 2);
        ctx.fill();
    }
}


class Disc extends Entity {
    constructor(row, col) {
        super(row, col, CONSTANTS.ENTITY_TYPE.DISC);
        this.colorIndex = 0;
        this.flashTimer = 0;
    }

    update() {
        super.update();
        // Flash colors
        this.flashTimer++;
        if (this.flashTimer > 10) {
            this.flashTimer = 0;
            this.colorIndex = (this.colorIndex + 1) % CONSTANTS.COLORS.DISC.length;
        }
    }

    getColor() {
        return CONSTANTS.COLORS.DISC[this.colorIndex];
    }

    draw(ctx) {
        const x = this.x;
        const y = this.y - 5;
        ctx.fillStyle = this.getColor();

        // Draw Disc (Ellipse)
        ctx.beginPath();
        ctx.ellipse(x, y, 12, 4, 0, 0, Math.PI * 2);
        ctx.fill();

        // Inner detail
        ctx.fillStyle = '#000';
        ctx.beginPath();
        ctx.ellipse(x, y, 6, 2, 0, 0, Math.PI * 2);
        ctx.fill();
    }
}
