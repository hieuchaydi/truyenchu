// script.js

document.addEventListener("DOMContentLoaded", function() {
    const toggleButton = document.getElementById("toggle-dark-mode");
    const currentTheme = localStorage.getItem("theme") || "light";

    // Áp dụng chế độ hiện tại
    if (currentTheme === "dark") {
        document.body.classList.add("dark-mode");
        toggleButton.textContent = "Chế Độ Sáng";
    } else {
        toggleButton.textContent = "Chế Độ Tối";
    }

    // Xử lý sự kiện khi nhấn nút chuyển đổi
    toggleButton.addEventListener("click", function() {
        document.body.classList.toggle("dark-mode");
        let theme = "light";
        if (document.body.classList.contains("dark-mode")) {
            theme = "dark";
            toggleButton.textContent = "Chế Độ Sáng";
        } else {
            toggleButton.textContent = "Chế Độ Tối";
        }
        localStorage.setItem("theme", theme);
    });
});

const cells = document.querySelectorAll('.cell');
const gameStatusDisplay = document.getElementById('game-status');
const restartBtn = document.getElementById('restart-btn');
const ticTacToe = document.getElementById('tic-tac-toe');
const onePlayerBtn = document.getElementById('one-player-btn');
const twoPlayerBtn = document.getElementById('two-player-btn');
let currentPlayer = 'X';
let gameActive = false;
let board = Array(3).fill(null).map(() => Array(3).fill(0)); // Ma trận 3x3

const winningConditions = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
];

function handleCellClick(clickedCell, clickedCellIndex) {
    if (clickedCell.textContent !== '' || !gameActive) {
        return;
    }

    clickedCell.textContent = currentPlayer;
    board[Math.floor(clickedCellIndex / 3)][clickedCellIndex % 3] = currentPlayer === 'X' ? 1 : 2; // Cập nhật board

    checkResult();

    if (currentPlayer === 'X' && !gameActive) {
        return;
    }

    if (onePlayerBtn.classList.contains('active')) {
        setTimeout(() => aiTurn(), 500); // Cho AI có thời gian để di chuyển
    }
}
// Phần còn lại của mã script.js không thay đổi

function aiTurn() {
    fetch('/play_caro', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ board: board }),
    })
    .then(response => response.json())
    .then(data => {
        board = data.board;
        updateBoard();
        checkResult();
    });
}


function updateBoard() {
    for (let i = 0; i < board.length; i++) {
        for (let j = 0; j < board[i].length; j++) {
            const index = i * 3 + j;
            if (board[i][j] === 1) {
                cells[index].textContent = 'X';
            } else if (board[i][j] === 2) {
                cells[index].textContent = 'O';
            }
        }
    }
}

function checkResult() {
    let roundWon = false;

    for (let i = 0; i < winningConditions.length; i++) {
        const condition = winningConditions[i];
        const a = board[condition[0] / 3 | 0][condition[0] % 3];
        const b = board[condition[1] / 3 | 0][condition[1] % 3];
        const c = board[condition[2] / 3 | 0][condition[2] % 3];

        if (a === 0 || b === 0 || c === 0) {
            continue;
        }
        if (a === b && b === c) {
            roundWon = true;
            break;
        }
    }

    if (roundWon) {
        gameStatusDisplay.textContent = `Người chơi ${currentPlayer} đã thắng!`;
        gameActive = false;
        return;
    }

    if (board.flat().every(cell => cell !== 0)) {
        gameStatusDisplay.textContent = 'Trò chơi hòa!';
        gameActive = false;
        return;
    }

    currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
    gameStatusDisplay.textContent = `Lượt của người chơi ${currentPlayer}`;
}

function restartGame() {
    gameActive = true;
    currentPlayer = 'X';
    gameStatusDisplay.textContent = `Lượt của người chơi ${currentPlayer}`;
    board = Array(3).fill(null).map(() => Array(3).fill(0)); // Reset board
    cells.forEach(cell => cell.textContent = '');
}

function startTwoPlayer() {
    onePlayerBtn.classList.remove('active');
    twoPlayerBtn.classList.add('active');
    startGame();
}

function startOnePlayer() {
    twoPlayerBtn.classList.remove('active');
    onePlayerBtn.classList.add('active');
    startGame();
}

function startGame() {
    ticTacToe.style.display = 'block';
    restartGame();
}

onePlayerBtn.addEventListener('click', startOnePlayer);
twoPlayerBtn.addEventListener('click', startTwoPlayer);
cells.forEach((cell, index) => {
    cell.addEventListener('click', () => handleCellClick(cell, index));
});
restartBtn.addEventListener('click', restartGame);
