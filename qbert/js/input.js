class InputHandler {
    constructor() {
        this.keys = {};
        this.queue = []; // Queue inputs to handle them one by one if needed

        window.addEventListener('keydown', (e) => {
            this.keys[e.code] = true;

            // Map arrows to directions
            if (e.code === 'ArrowUp' || e.code === 'ArrowRight' || e.code === 'ArrowDown' || e.code === 'ArrowLeft') {
                e.preventDefault();
                this.handleInput(e.code);
            }

            if (e.code === 'Enter') {
                this.onEnter?.();
            }
        });

        window.addEventListener('keyup', (e) => {
            this.keys[e.code] = false;
        });
    }

    handleInput(code) {
        // Q*bert controls are diagonal.
        // We can map standard arrows to diagonals or require combo?
        // Classic arcade used a rotated joystick.
        // Mappings for keyboard usually:
        // Up -> Up-Right (or Up-Left depending on preference, let's stick to visual)
        // Actually, let's use a standard mapping that feels intuitive.
        // Up Arrow -> Up-Right? No, that's confusing.
        // Let's map:
        // Up + Right -> Up-Right
        // But that's hard.
        // Common Q*bert mapping:
        // I / 8 / Up -> Up-Right
        // K / 2 / Down -> Down-Left
        // J / 4 / Left -> Up-Left
        // L / 6 / Right -> Down-Right
        // Let's try to support Arrow Keys as diagonals directly if possible, or mapped.
        // Let's map:
        // Right Arrow -> Down-Right
        // Left Arrow -> Up-Left
        // Up Arrow -> Up-Right
        // Down Arrow -> Down-Left
        // This is a common mapping for Q*bert on PC.

        let direction = null;

        switch (code) {
            case 'ArrowUp':
                direction = CONSTANTS.DIR.UP_RIGHT; // or UP_LEFT? Let's try UP_RIGHT (Top-Right)
                // Actually, let's make it configurable or smart.
                // Standard MAME mapping:
                // Up -> Up-Right
                // Down -> Down-Left
                // Left -> Up-Left
                // Right -> Down-Right
                direction = CONSTANTS.DIR.UP_RIGHT;
                break;
            case 'ArrowDown':
                direction = CONSTANTS.DIR.DOWN_LEFT;
                break;
            case 'ArrowLeft':
                direction = CONSTANTS.DIR.UP_LEFT;
                break;
            case 'ArrowRight':
                direction = CONSTANTS.DIR.DOWN_RIGHT;
                break;
        }

        // Alternative: Numpad 7, 9, 1, 3
        if (code === 'Numpad9') direction = CONSTANTS.DIR.UP_RIGHT;
        if (code === 'Numpad7') direction = CONSTANTS.DIR.UP_LEFT;
        if (code === 'Numpad3') direction = CONSTANTS.DIR.DOWN_RIGHT;
        if (code === 'Numpad1') direction = CONSTANTS.DIR.DOWN_LEFT;

        if (direction && this.onMove) {
            this.onMove(direction);
        }
    }

    setMoveCallback(callback) {
        this.onMove = callback;
    }

    setEnterCallback(callback) {
        this.onEnter = callback;
    }
}
