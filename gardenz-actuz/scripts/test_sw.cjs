// A full disk must not turn a valid online response into an offline/error result.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
async function check(path) {
  const events = {};
  const response = new Response('fresh network content', {status:200});
  const context = {
    self: {registration:{scope:'https://example.test/gardenz-actuz/'}, addEventListener:(event,callback)=>events[event]=callback},
    URL, Request, Response, Headers, Set, Promise,
    fetch:async()=>response.clone(),
    caches:{match:async()=>undefined,open:async()=>({put:async()=>{throw new Error('QuotaExceededError')}})}
  };
  vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'../sw.js'),'utf8'), context);
  let pending;
  events.fetch({request:new Request('https://example.test/gardenz-actuz/'+path),respondWith:value=>pending=value});
  const actual = await pending;
  assert.equal(actual.status,200);
  assert.equal(await actual.text(),'fresh network content');
  assert.equal(actual.headers.get('X-Gardenz-Cache'),null);
}
Promise.all([check('data/latest.json'),check('assets/live-example.jpg')]).then(()=>process.stdout.write('Cache plein : données et images réseau conservées.\n')).catch(error=>{console.error(error);process.exitCode=1});
