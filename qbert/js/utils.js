const Utils = {
    // Convert Grid Coordinates (row, col) to Screen Coordinates (x, y)
    // Row 0 is top. Col 0 is left-most of that row.
    gridToScreen: (row, col) => {
        // Calculate offset based on row to center it
        // Row 0: 1 cube. Row 1: 2 cubes...
        // Center of pyramid is START_X

        const cubeWidth = CONSTANTS.CUBE_SIZE * 2; // Horizontal width of isometric cube
        const cubeHeight = CONSTANTS.CUBE_SIZE * 1.5; // Vertical step

        // Horizontal offset: Each row shifts left by half a cube width, then col shifts right by full cube width
        // Actually, let's think about the pyramid structure.
        // Row 0, Col 0: Top
        // Row 1, Col 0: Down-Left from Top. Row 1, Col 1: Down-Right from Top.

        const x = CONSTANTS.START_X + (col * cubeWidth) - (row * (cubeWidth / 2));
        const y = CONSTANTS.START_Y + (row * cubeHeight);

        return { x, y };
    },

    // Check if a coordinate is valid within the pyramid
    isValidGrid: (row, col) => {
        return row >= 0 && row < CONSTANTS.GRID_ROWS && col >= 0 && col <= row;
    },

    // Random integer between min and max (inclusive)
    randomInt: (min, max) => {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    },

    // Random array element
    randomChoice: (arr) => {
        return arr[Math.floor(Math.random() * arr.length)];
    },

    // Simple collision check (distance based for now, or grid based)
    // Since everything moves on grid, we primarily check grid coordinates.
    // But for smooth animation, we might need screen distance.
    distance: (x1, y1, x2, y2) => {
        return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
    }
};
