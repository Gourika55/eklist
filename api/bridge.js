import {timingSafeEqual} from 'node:crypto';
export const config={maxDuration:60};
const equal=(a,b)=>{const x=Buffer.from(a||''),y=Buffer.from(b||'');return x.length===y.length&&timingSafeEqual(x,y)};
export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  const {EKLIST_BACKEND_URL:base,EKLIST_BACKEND_TOKEN:token,EKLIST_DEMO_USER:user,EKLIST_DEMO_PASSWORD:password}=process.env;
  if(!base||!token||!user||!password)return res.status(503).json({error:'Deployment configuration is incomplete.'});
  const expected='Basic '+Buffer.from(`${user}:${password}`).toString('base64');
  if(!equal(req.headers.authorization,expected)){
    res.setHeader('WWW-Authenticate','Basic realm="EkList workspace", charset="UTF-8"');
    return res.status(401).json({error:'Sign in to the shared demo workspace.'});
  }
  if(!['GET','POST'].includes(req.method))return res.status(405).json({error:'Method not allowed'});
  const incoming=new URL(req.url,'http://localhost');
  // The rewrite supplies only the API path; never accept a caller-selected upstream URL.
  const path=incoming.searchParams.get('path')||'';
  if(!/^[a-z0-9/_-]+$/i.test(path)||path.includes('..'))return res.status(400).json({error:'Invalid API path'});
  incoming.searchParams.delete('path');
  const upstream=new URL(base);
  if(upstream.protocol!=='https:'&&!(process.env.EKLIST_PROXY_LOCAL_TEST==='1'&&upstream.hostname==='127.0.0.1'))return res.status(503).json({error:'Backend must use HTTPS'});
  upstream.pathname='/api/'+path;upstream.search=incoming.searchParams.toString();
  const body=req.method==='POST'?(typeof req.body==='string'?req.body:JSON.stringify(req.body)):undefined;
  if(body&&Buffer.byteLength(body)>4_000_000)return res.status(413).json({error:'Hosted request too large. Split the file into smaller batches (about 2.8 MB for XLSX).'});
  try{
    const result=await fetch(upstream,{method:req.method,headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body,redirect:'error',signal:AbortSignal.timeout(55000)});
    res.status(result.status);
    for(const key of ['content-type','content-disposition'])if(result.headers.has(key))res.setHeader(key,result.headers.get(key));
    return res.send(Buffer.from(await result.arrayBuffer()));
  }catch{return res.status(502).json({error:'Backend unavailable or timed out. Check Render health and configuration.'})}
}
