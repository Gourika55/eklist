import test from 'node:test';
import assert from 'node:assert/strict';
import handler from '../api/bridge.js';
const env={EKLIST_BACKEND_URL:'https://backend.example',EKLIST_BACKEND_TOKEN:'x'.repeat(32),EKLIST_DEMO_USER:'demo',EKLIST_DEMO_PASSWORD:'test-password'};
const response=()=>({headers:{},setHeader(k,v){this.headers[k]=v},status(n){this.code=n;return this},json(v){this.body=v;return this},send(v){this.body=v;return this}});
test('bridge rejects unauthenticated requests before reaching backend',async()=>{Object.assign(process.env,env);let res=response();await handler({headers:{},method:'GET',url:'/api/bridge?path=catalog'},res);assert.equal(res.code,401)});
test('bridge preserves CSV and filters without forwarding client token',async()=>{
 Object.assign(process.env,env);const old=global.fetch;let called;
 global.fetch=async(url,options)=>{called={url:String(url),options};return new Response('name\nExample\n',{headers:{'Content-Type':'text/csv','Content-Disposition':'attachment; filename="results.csv"'}})};
 try{let res=response();await handler({headers:{authorization:'Basic '+Buffer.from('demo:test-password').toString('base64')},method:'GET',url:'/api/bridge?path=opportunities/abc&export=all&q=India'},res);assert.equal(res.code,200);assert.equal(res.headers['content-type'],'text/csv');assert.match(called.url,/export=all&q=India/);assert.equal(called.options.headers.Authorization,'Bearer '+env.EKLIST_BACKEND_TOKEN);assert.equal(String(res.body),'name\nExample\n')}finally{global.fetch=old}
});
