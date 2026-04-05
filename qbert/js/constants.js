const CONSTANTS = {
    SCREEN_WIDTH: 800,
    SCREEN_HEIGHT: 600,
    FPS: 60,

    // Grid Settings
    CUBE_SIZE: 40, // Size of a cube face side
    GRID_ROWS: 7,
    START_X: 400, // Top of pyramid X
    START_Y: 150, // Top of pyramid Y

    // Colors (Classic Arcade Palette)
    COLORS: {
        BACKGROUND: '#000000',
        CUBE_TOP_ACTIVE: '#FFFF00', // Target yellow
        CUBE_TOP_INACTIVE: '#0000FF', // Blue
        CUBE_TOP_INTERMEDIATE: '#00FF00', // Green (for multi-step)
        CUBE_LEFT: '#888888', // Shaded side
        CUBE_RIGHT: '#444444', // Darker side
        TEXT: '#FFFFFF',
        QBERT: '#FF6600',
        ENEMY_PURPLE: '#CC00CC',
        ENEMY_GREEN: '#00FF00',
        ENEMY_RED: '#FF0000',
        DISC: ['#FF00FF', '#00FFFF', '#FFFF00'] // Flashing colors
    },

    // Scoring
    SCORE: {
        COLOR_CHANGE: 25,
        INTERMEDIATE_CHANGE: 15,
        CATCH_GREEN_BALL: 100,
        CATCH_SLICK_SAM: 300,
        DEFEAT_COILY: 500,
        UNUSED_DISC: 50,
        ROUND_COMPLETE_BASE: 1000,
        ROUND_COMPLETE_INC: 250
    },

    // Entity Types
    ENTITY_TYPE: {
        PLAYER: 'player',
        RED_BALL: 'red_ball',
        PURPLE_BALL: 'purple_ball',
        COILY: 'coily',
        UGG: 'ugg',
        WRONGWAY: 'wrongway',
        SLICK: 'slick',
        SAM: 'sam',
        GREEN_BALL: 'green_ball',
        DISC: 'disc'
    },

    // Directions
    DIR: {
        UP_RIGHT: { x: 1, y: -1 },
        UP_LEFT: { x: -1, y: -1 },
        DOWN_RIGHT: { x: 1, y: 1 },
        DOWN_LEFT: { x: -1, y: 1 }
    }
};
