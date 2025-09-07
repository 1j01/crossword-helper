
from html import escape


JS = """
	function dragElement(evt) {
		var selectedElement = evt.target.closest('.draggable');
		if (!selectedElement) {
			return;
		}
		var offset = getMousePosition(evt);
		var transform = selectedElement.transform.baseVal.getItem(0);
		var coord = transform.matrix;
		offset.x -= coord.e;
		offset.y -= coord.f;
		selectedElement.addEventListener('pointermove', moveElement);
		selectedElement.addEventListener('pointerup', dropElement);
		selectedElement.addEventListener('pointerleave', dropElement);
		selectedElement.addEventListener('pointercancel', dropElement);
		evt.preventDefault();
		selectedElement.setPointerCapture(evt.pointerId);
		selectedElement.style.cursor = 'grabbing';
		function moveElement(evt) {
			var coord = selectedElement.transform.baseVal.getItem(0).matrix;
			var mousePos = getMousePosition(evt);
			coord.e = mousePos.x - offset.x;
			coord.f = mousePos.y - offset.y;
			transform.setMatrix(coord);
			evt.preventDefault();
		}
		function dropElement(evt) {
			selectedElement.removeEventListener('pointermove', moveElement);
			selectedElement.removeEventListener('pointerup', dropElement);
			selectedElement.removeEventListener('pointerleave', dropElement);
			selectedElement.removeEventListener('pointercancel', dropElement);
			evt.preventDefault();
			selectedElement.releasePointerCapture(evt.pointerId);
			selectedElement.style.cursor = 'grab';
			savePositions();
		}
		function getMousePosition(evt) {
			var svg = selectedElement.ownerSVGElement;
			var CTM = svg.getScreenCTM();
			return {
				x: (evt.clientX - CTM.e) / CTM.a,
				y: (evt.clientY - CTM.f) / CTM.d
			};
		}
	}
	const storageKey = 'draggableWordPositions';
	function savePositions() {
		const positions = {};
		for (const el of document.querySelectorAll('.draggable')) {
			const transform = el.transform.baseVal.getItem(0);
			const coord = transform.matrix;
			positions[el.querySelector('text').textContent] = { x: coord.e, y: coord.f };
		}
		localStorage.setItem(storageKey, JSON.stringify(positions));
	}
	function loadPositions() {
		const positions = JSON.parse(localStorage.getItem(storageKey) || '{}');
		for (const el of document.querySelectorAll('.draggable')) {
			const word = el.querySelector('text').textContent;
			if (word in positions) {
				const pos = positions[word];
				const transform = el.transform.baseVal.getItem(0);
				const coord = transform.matrix;
				coord.e = pos.x;
				coord.f = pos.y;
				transform.setMatrix(coord);
			}
		}
	}
	addEventListener('pointerdown', dragElement);
	for (const el of document.querySelectorAll('.draggable')) {
		el.style.touchAction = 'none';
		el.style.cursor = 'grab';
	}
	// must be at end; may error if localStorage not available
	loadPositions();
"""

def make_draggable_svg(
	word_lists: list[list[str]],
) -> str:
	"""
	Generates an SVG string with draggable words from the provided word lists.
	"""

	if len(word_lists) < 1:
		raise ValueError("At least one word list must be specified.")

	draggable_words = ""
	# word_width = 100
	word_height = 30
	x_per_list = 300
	y_per_word = word_height + 5
	svg_width = max(600, len(word_lists) * x_per_list + 20)
	svg_height = max(600, max(len(words) for words in word_lists) * y_per_word + 20)
	for list_index, words in enumerate(word_lists):
		x = list_index * x_per_list + 10
		golden_ratio_conjugate = 0.618033988749895
		color = f"hsl({(list_index * golden_ratio_conjugate * 360) % 360}, 70%, 50%)"
		for word_index, word in enumerate(words):
			y = word_index * y_per_word + 20
			tooltip = ""
			if "(" in word and word.endswith(")"):
				tooltip = word[word.index("(")+1:-1].strip()
				word = word[:word.index("(")].strip()
			draggable_words += f'''
			<g transform="translate({x}, {y})" class="draggable">
				<rect x="-5" y="{-word_height/2}" width="{len(word)*12 + 10}" height="{word_height}" fill="white" stroke="black" stroke-width="1" rx="5" ry="5"/>
				<text x="0" y="0" dominant-baseline="middle" fill="{color}">{escape(word)}</text>
				<title>{escape(tooltip)}</title>
			</g>
			'''

	return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" style="border:1px solid black;">
	{draggable_words}
	<style>
		.draggable text {{
			font-family: monospace;
			font-size: 16px;
			user-select: none;
		}}
	</style>
	<script>
	{JS}
	</script>
</svg>
"""