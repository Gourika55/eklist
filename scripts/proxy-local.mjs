// Exercises the exact Vercel bridge handler locally; not a production server.
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {resolve,extname} from 'node:path';
import handler from '../api/bridge.js';
http.createServer(async(req,res)=>{
 if(req.url.startsWith('/api/')){
  const u=new URL(req.url,'http://localhost');u.searchParams.set('path',u.pathname.slice(5));req.url='/api/bridge?'+u.searchParams;
  let body='';for await(const c of req)body+=c;
  if(body){try{req.body=JSON.parse(body)}catch{res.writeHead(400);res.end();return}}
  res.status=n=>{res.statusCode=n;return res};res.json=v=>{res.setHeader('Content-Type','application/json');res.end(JSON.stringify(v))};res.send=v=>res.end(v);
  await handler(req,res);return;
 }
 try{const p=resolve('dist','.'+(req.url==='/'?'/index.html':new URL(req.url,'http://localhost').pathname));if(!p.startsWith(resolve('dist')+'/'))throw Error();res.setHeader('Content-Type',({'.html':'text/html','.js':'text/javascript','.css':'text/css'})[extname(p)]||'application/octet-stream');res.end(await readFile(p))}catch{res.writeHead(404);res.end()}
}).listen(Number(process.env.PROXY_PORT||4186),'127.0.0.1');
