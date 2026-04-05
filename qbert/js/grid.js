class Tile {
    constructor(row, col, startColor) {
        this.row = row;
        this.col = col;
        this.color = startColor;
        this.targetColor = CONSTANTS.COLORS.CUBE_TOP_ACTIVE;
        this.isTarget = false;
    }

    draw(ctx) {
        const pos = Utils.gridToScreen(this.row, this.col);
        const size = CONSTANTS.CUBE_SIZE;
        const x = pos.x;
        const y = pos.y;

        // Draw Cube
        // Top Face
        ctx.fillStyle = this.color;
        ctx.beginPath();
        ctx.moveTo(x, y - size);
        ctx.lineTo(x + size, y - size / 2);
        ctx.lineTo(x, y);
        ctx.lineTo(x - size, y - size / 2);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Right Face
        ctx.fillStyle = CONSTANTS.COLORS.CUBE_RIGHT;
        ctx.beginPath();
        ctx.moveTo(x + size, y - size / 2);
        ctx.lineTo(x + size, y + size / 2);
        ctx.lineTo(x, y + size);
        ctx.lineTo(x, y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Left Face
        ctx.fillStyle = CONSTANTS.COLORS.CUBE_LEFT;
        ctx.beginPath();
        ctx.moveTo(x - size, y - size / 2);
        ctx.lineTo(x - size, y + size / 2);
        ctx.lineTo(x, y + size);
        ctx.lineTo(x, y);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }
}

class Pyramid {
    constructor() {
        this.tiles = [];
        this.init();
    }

    init() {
        this.tiles = [];
        for (let r = 0; r < CONSTANTS.GRID_ROWS; r++) {
            for (let c = 0; c <= r; c++) {
                this.tiles.push(new Tile(r, c, CONSTANTS.COLORS.CUBE_TOP_INACTIVE));
            }
        }
    }

    getTile(row, col) {
        return this.tiles.find(t => t.row === row && t.col === col);
    }

    draw(ctx) {
        // Draw from top to bottom to handle occlusion correctly?
        // Actually back to front (painter's algorithm).
        // Row 0 is top (back). Row 6 is bottom (front).
        // So drawing 0 to 6 works.
        this.tiles.forEach(tile => tile.draw(ctx));
    }

    isComplete() {
        return this.tiles.every(t => t.color === CONSTANTS.COLORS.CUBE_TOP_ACTIVE);
    }
}
