const grid = [
	"A B C D",
	"E F G H",
	"I J K L",
	"M N O P",
	"Q R S T",
	"U V W X",
	"Y & Z !",
].map(line => line.split(" "));

const diagonals = {
	downRight: [],
	upRight: [],
	downLeft: [],
	upLeft: [],
};
const coords = Object.fromEntries(
	Object.keys(diagonals).map(dir => [dir, []])
);
function recordDiagonal(dirName, row, col) {
	if (grid[row][col]) {
		diagonals[dirName][diagonals[dirName].length - 1].push(grid[row][col]);
		coords[dirName][coords[dirName].length - 1].push([row, col]);
	}
}
for (let i = -grid.length + 1; i < grid[0].length; i++) {
	for (const array of Object.values(diagonals)) {
		array.push([]);
	}
	for (const array of Object.values(coords)) {
		array.push([]);
	}
	for (let j = 0; j < grid.length; j++) {
		recordDiagonal("downRight", j, i + j);
		recordDiagonal("upRight", grid.length - 1 - j, i + j);
		recordDiagonal("downLeft", j, grid[0].length - 1 - (i + j));
		recordDiagonal("upLeft", grid.length - 1 - j, grid[0].length - 1 - (i + j));
	}
}

const result = Object.fromEntries(
	Object.entries(diagonals).map(([key, value]) => [key, value.map(d => d.join(""))])
);
console.log(result, coords);
