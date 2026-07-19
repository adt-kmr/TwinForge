const fs = require('fs');
const file = '/Users/deepesh/Developer/DragVerse/dashboard/src/Console.jsx';
let lines = fs.readFileSync(file, 'utf8').split('\n');

// Comment out Stage 1-5 (lines 177 to 291 -> 1-indexed)
// So indices 176 to 290
lines.splice(291, 0, '          */}');
lines.splice(176, 0, '          {/*');

// File shifted by 2 lines.
// Target stage 8 and Rescan was 365 to 408 (1-indexed). Now 367 to 410.
// Let's find Stage 08 dynamically.
let deployIndex = lines.findIndex(l => l.includes('n="08" name="Deploy"'));
// The <Stage is one line before
let deployStartIndex = deployIndex - 1;
// Find end of Rescan Stage
let rescanIndex = lines.findIndex(l => l.includes('n="↺" name="Rescan"'));
let rescanEndIndex = rescanIndex;
while (!lines[rescanEndIndex].includes('</Stage>')) {
  rescanEndIndex++;
}

lines.splice(rescanEndIndex + 1, 0, '          */}');
lines.splice(deployStartIndex, 0, '          {/*');

// Find section className="view"
let viewIndex = lines.findIndex(l => l.includes('<section className="view">'));
let viewEndIndex = lines.findIndex(l => l.includes('</section>'));

lines.splice(viewEndIndex + 1, 0, '        */}');
lines.splice(viewIndex, 0, '        {/*');

fs.writeFileSync(file, lines.join('\n'));
