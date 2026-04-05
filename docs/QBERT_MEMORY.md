# Q*bert Project Memory Note

## Project Overview
**Objective**: Create an exact clone of the arcade game Q*bert using HTML5 Canvas and Vanilla JavaScript.
**Status**: Completed & Verified.
**Location**: `d:/Dev/repos/llm-txt-mcp/qbert/`

## Technical Architecture

### Core Engine
- **Language**: Vanilla JavaScript (ES6+).
- **Rendering**: HTML5 Canvas API (2D Context).
- **Audio**: Web Audio API for real-time synthesis (no external assets).
- **Input**: Event-based keyboard handling (`InputHandler`).

### Class Structure
1.  **`Game` (`game.js`)**:
    *   Central controller.
    *   Manages game loop (`requestAnimationFrame`), state (`MENU`, `PLAYING`, `GAMEOVER`), and entity lifecycle.
    *   Handles collision detection and level progression.

2.  **`Pyramid` & `Tile` (`grid.js`)**:
    *   **Grid System**: 7-row pyramid represented by a 2D array-like structure (managed via `tiles` array).
    *   **Rendering**: Isometric projection using `Utils.gridToScreen`.
    *   **Logic**: Tracks tile states (colors) and checks for round completion.

3.  **`Entity` System (`entities.js`)**:
    *   **Base Class**: `Entity` handles position (grid & screen), smooth movement interpolation, and basic drawing.
    *   **Player**: `Qbert` extends `Entity`, adds specific drawing and user control.
    *   **Enemies**: `Enemy` base class with `decideMove` AI hook.
        *   `Ball`: Simple bouncing logic (Red/Purple).
        *   `Coily`: Complex state machine (Ball -> Snake -> Chase AI).
        *   `UggWrongway`: Unique movement on cube sides (visualized as offset drawing).
        *   `SlickSam`: Color-reverting logic.
        *   `GreenBall`: Power-up logic.
    *   **Objects**: `Disc` for transport mechanics.

### Key Algorithms
- **Isometric Projection**:
    ```javascript
    x = (col * 0.5 + row) * TILE_WIDTH;
    y = row * TILE_HEIGHT * 0.75;
    ```
    (Simplified; actual implementation in `utils.js` handles centering).
- **Collision Detection**: Grid-based overlap checking in `Game.update`.
- **AI Pathfinding**: Coily uses a simple distance minimization heuristic to chase Q*bert.

## Implementation Details

### Graphics
- **Procedural Generation**: All visuals are drawn using `ctx.beginPath()`, `ctx.arc()`, `ctx.lineTo()`, etc.
- **Depth Sorting**: Entities are sorted by `y` coordinate before drawing to ensure correct occlusion (painter's algorithm).

### Audio
- **Synthesis**: `AudioController` uses `OscillatorNode` and `GainNode` to create retro sound effects.
- **Events**: Sounds triggered on jump, land, death, and level clear.

## Future Improvements
- **High Score Persistence**: Save scores to `localStorage`.
- **Mobile Support**: Add touch controls.
- **Enhanced AI**: Improve Ugg/Wrongway visual logic to better represent "side" movement.
- **Attract Mode**: Auto-play demo on start screen.

## Artifacts
- `QBERT_SPEC.md`: Detailed game specification.
- `implementation_plan.md`: Technical roadmap.
- `walkthrough.md`: User guide and feature summary.
