const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('assets/product.js','utf8').split('const activitySummary =')[1];
const feed = JSON.parse(fs.readFileSync('changes.json','utf8'));
async function render(data, ok=true) {
  const nodes = Object.fromEntries(['cases','evidence','unknowns','states'].map(k=>[k,{textContent:'—'}]));
  const status = {textContent:''};
  const summary = {dataset:{source:'/changes.json'},querySelector:s=>nodes[s.match(/"(.*?)"/)[1]],querySelectorAll:()=>Object.values(nodes)};
  const ctx = {document:{querySelector:s=>s==='[data-activity-summary]'?summary:status},fetch:async()=>({ok,json:async()=>data}),Date};
  vm.runInNewContext('const activitySummary ='+source,ctx);
  await new Promise(setImmediate);
  return {values:Object.values(nodes).map(x=>x.textContent),status:status.textContent};
}
(async()=>{
  let r=await render(feed);assert.deepEqual(r.values,['1','1','0','1']);
  assert.match(r.status,/INCOMPLETE COVERAGE/);assert.match(r.status,/2026-09-20 to 2026-10-13/);
  assert.match(r.status,/Metadata predates/);
  r=await render(null,false);assert.ok(r.values.every(v=>v==='Unavailable'));assert.match(r.status,/unknown, not zero/);
  r=await render({...feed,changes:[...feed.changes,feed.changes[0]]});assert.ok(r.values.every(v=>v==='Unavailable'));
  r=await render({...feed,changes:[{...feed.changes[0],unknowns_resolved:null}]});assert.ok(r.values.every(v=>v==='Unavailable'));
  r=await render({...feed,changes:[{...feed.changes[0],date:'2026-02-30'}]});assert.ok(r.values.every(v=>v==='Unavailable'));
  r=await render({...feed,changes:[{...feed.changes[0],type:'DRAFT'}]});assert.ok(r.values.every(v=>v==='Unavailable'));
  r=await render({...feed,changes:[]});assert.deepEqual(r.values,['0','0','0','0']);assert.match(r.status,/INCOMPLETE/);
  assert.equal(fs.readFileSync('assets/product.js','utf8'),fs.readFileSync('docs/assets/product.js','utf8'));
  assert.equal(fs.readFileSync('index.html','utf8'),fs.readFileSync('docs/index.html','utf8'));
  console.log('PASS: recorded totals; event date range; incomplete coverage; old metadata warning; failed fetch; duplicates; missing counts; invalid dates; drafts; empty feed; mirror parity');
})().catch(e=>{console.error(e);process.exit(1)});
