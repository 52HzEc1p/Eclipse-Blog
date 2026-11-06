/* Keep untouched code blocks byte-for-byte when a visual editor normalizes them. */
(function (root) {
  'use strict';
  function createPreserver(parser, original, normalized) {
    function blocks(markdown) {
      const lines = markdown.split('\n');
      const offsets = [0];
      lines.forEach(line => offsets.push(offsets[offsets.length - 1] + line.length + 1));
      return parser.parse(markdown, {}).filter(token => token.map && (token.type === 'fence' || token.type === 'code_block'))
        .map(token => ({
          start: offsets[token.map[0]], end: Math.min(markdown.length, offsets[token.map[1]]),
          type: token.type, info: token.info,
          closed: token.type !== 'fence' || (token.map[1] - token.map[0] >= 2 &&
            new RegExp('^ {0,3}' + token.markup[0] + '{' + token.markup.length + ',}[ \\t]*$').test(lines[token.map[1] - 1])),
          raw: markdown.slice(offsets[token.map[0]], Math.min(markdown.length, offsets[token.map[1]])),
        }));
    }
    const before = blocks(original);
    const rendered = blocks(normalized);
    const replacements = new Map();
    if (before.length === rendered.length) {
      rendered.forEach((block, index) => {
        const source = before[index];
        if (!source.closed || block.type !== source.type || block.info.trim() !== source.info.trim()) return;
        if (replacements.has(block.raw) && replacements.get(block.raw) !== source.raw) {
          replacements.set(block.raw, null); // Ambiguous duplicate blocks must not be guessed.
        } else { replacements.set(block.raw, source.raw); }
      });
    }
    let lastInput, lastOutput;
    return function preserve(markdown) {
      if (markdown === lastInput) return lastOutput;
      let output = markdown;
      for (const block of blocks(markdown).reverse()) {
        const replacement = replacements.get(block.raw);
        if (replacement != null) output = output.slice(0, block.start) + replacement + output.slice(block.end);
      }
      lastInput = markdown;
      lastOutput = output;
      return output;
    };
  }
  if (typeof module === 'object' && module.exports) module.exports = createPreserver;
  else root.createMarkdownPreserver = createPreserver;
})(typeof window === 'object' ? window : globalThis);
