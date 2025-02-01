// script.js

// ---- Configurable parameters ----
const CELL_SIZE = 10; // pixel size of each cell
const GRID_WIDTH = 60;  // number of cells horizontally
const GRID_HEIGHT = 40; // number of cells vertically
const ALIVE_COLOR = "#333";
const DEAD_COLOR = "#fff";

// ---- Global variables ----
let grid = createGrid(GRID_WIDTH, GRID_HEIGHT); // 2D array
let canvas, ctx;
let isRunning = false;
let animationId = null; // for requestAnimationFrame

window.onload = function () {
  // Get references to the canvas and context
  canvas = document.getElementById("game-canvas");
  ctx = canvas.getContext("2d");
  
  // Set canvas size based on the grid dimensions
  canvas.width = GRID_WIDTH * CELL_SIZE;
  canvas.height = GRID_HEIGHT * CELL_SIZE;

  // Draw the initial grid
  drawGrid();

  // Add event listeners to buttons
  document.getElementById("start-button").addEventListener("click", startGame);
  document.getElementById("stop-button").addEventListener("click", stopGame);
  document.getElementById("step-button").addEventListener("click", stepGame);
  document.getElementById("clear-button").addEventListener("click", clearGame);

  // Add mouse click event to toggle cells
  canvas.addEventListener("click", toggleCell);
};

// ---- Create a 2D array of dead cells ----
function createGrid(width, height) {
  let arr = new Array(height);
  for (let y = 0; y < height; y++) {
    arr[y] = new Array(width).fill(0);
  }
  return arr;
}

// ---- Draw the grid on the canvas ----
function drawGrid() {
  for (let y = 0; y < GRID_HEIGHT; y++) {
    for (let x = 0; x < GRID_WIDTH; x++) {
      // Determine color based on alive/dead
      if (grid[y][x] === 1) {
        ctx.fillStyle = ALIVE_COLOR;
      } else {
        ctx.fillStyle = DEAD_COLOR;
      }
      ctx.fillRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE);
    }
  }
}

// ---- Toggle cell state when clicked ----
function toggleCell(event) {
  // Get mouse position relative to canvas
  const rect = canvas.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  // Calculate which cell was clicked
  const x = Math.floor(mouseX / CELL_SIZE);
  const y = Math.floor(mouseY / CELL_SIZE);

  // Toggle between 1 (alive) and 0 (dead)
  grid[y][x] = grid[y][x] ? 0 : 1;

  // Redraw grid
  drawGrid();
}

// ---- Step the simulation forward by 1 generation ----
function stepGame() {
  grid = getNextGeneration(grid);
  drawGrid();
}

// ---- Conway's Game of Life rules: compute next gen from current ----
function getNextGeneration(currentGrid) {
  let newGrid = createGrid(GRID_WIDTH, GRID_HEIGHT);

  for (let y = 0; y < GRID_HEIGHT; y++) {
    for (let x = 0; x < GRID_WIDTH; x++) {
      const alive = currentGrid[y][x] === 1;
      const neighborCount = countAliveNeighbors(currentGrid, x, y);

      if (alive) {
        // 1) Any live cell with two or three live neighbours survives.
        // 2) All other live cells die.
        newGrid[y][x] = (neighborCount === 2 || neighborCount === 3) ? 1 : 0;
      } else {
        // 3) Any dead cell with three live neighbours becomes a live cell.
        if (neighborCount === 3) {
          newGrid[y][x] = 1;
        }
      }
    }
  }

  return newGrid;
}

// ---- Count the alive neighbors of cell (x, y) ----
function countAliveNeighbors(grid, x, y) {
  let count = 0;
  for (let dy = -1; dy <= 1; dy++) {
    for (let dx = -1; dx <= 1; dx++) {
      if (dx === 0 && dy === 0) {
        continue; // skip the cell itself
      }
      const nx = x + dx;
      const ny = y + dy;
      if (
        nx >= 0 && nx < GRID_WIDTH &&
        ny >= 0 && ny < GRID_HEIGHT
      ) {
        count += grid[ny][nx];
      }
    }
  }
  return count;
}

// ---- Start the simulation ----
function startGame() {
  if (!isRunning) {
    isRunning = true;
    run();
  }
}

// ---- Stop the simulation ----
function stopGame() {
  isRunning = false;
  if (animationId) {
    cancelAnimationFrame(animationId);
    animationId = null;
  }
}

// ---- Animation loop for continuous updating ----
function run() {
  stepGame(); // Step one generation
  if (isRunning) {
    animationId = requestAnimationFrame(run);
  }
}

// ---- Clear the grid (make all cells dead) ----
function clearGame() {
  stopGame();
  grid = createGrid(GRID_WIDTH, GRID_HEIGHT);
  drawGrid();
}
