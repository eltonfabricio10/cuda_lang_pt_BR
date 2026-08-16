var fs = require('fs')
var parser = require('./fountain_js/parser');
 
var fname = process.argv[2]
var text = fs.readFileSync(fname).toString()
var output = parser.parse(text);
 
process.stdout.write(output['script_html'])
