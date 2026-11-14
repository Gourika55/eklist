import {timingSafeEqual,createHmac} from 'node:crypto';
export const config={maxDuration:60};
const equal=(a,b)=>{const x=Buffer.from(a||''),y=Buffer.from(b||'');return x.length===y.length&&timingSafeEqual(x,y)};
export default async function handler(req,res){
  res.setHeader('Cache-Control','no-store');
  const {EKLIST_BACKEND_URL:base,EKLIST_BACKEND_TOKEN:token,EKLIST_DEMO_USER:user,EKLIST_DEMO_PASSWORD:password}=process.env;
  if(!base||!token)return res.status(503).json({error:'Deployment configuration is incomplete.'});
  if(!['GET','POST'].includes(req.method))return res.status(405).json({error:'Method not allowed'});
  const incoming=new URL(req.url,'http://localhost');
  const path=incoming.searchParams.get('path')||'';
  if(!/^[a-z0-9/_-]+$/i.test(path)||path.includes('..'))return res.status(400).json({error:'Invalid API path'});
  // Public demo: only published corpus reads and deterministic catalogue queries.
  // Uploads, saved research and provider-powered mutations retain authentication.
  const publicRead=req.method==='GET'&&['health','catalog','packs','packs/records','benchmark','source-packs'].includes(path);
  const publicQuery=req.method==='POST'&&['plan','query'].includes(path);
  const cookie=(req.headers.cookie||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('eklist_session='))?.split('=').slice(1).join('=')||'';
  const [expires,signature]=cookie.split('.');
  const validSession=Number(expires)>Date.now()&&Number(expires)<Date.now()+9*3600000&&equal(signature,createHmac('sha256',token).update('presenter:'+expires).digest('hex'));
  if(path==='session'){
    if(req.method==='GET')return res.status(200).json({authenticated:!!validSession});
    const origin=req.headers.origin;
    if(origin&&origin!==new URL('https://'+req.headers.host).origin)return res.status(403).json({error:'Invalid request origin'});
    let input;try{input=typeof req.body==='string'?JSON.parse(req.body):req.body}catch{return res.status(400).json({error:'Invalid request'})}
    if(input?.logout){res.setHeader('Set-Cookie','eklist_session=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0');return res.status(200).json({authenticated:false})}
    if(!user||!password||!equal(input?.username,user)||!equal(input?.password,password))return res.status(403).json({error:'Incorrect presenter credentials'});
    const exp=String(Date.now()+8*3600000);const sig=createHmac('sha256',token).update('presenter:'+exp).digest('hex');
    res.setHeader('Set-Cookie',`eklist_session=${exp}.${sig}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=28800`);
    return res.status(200).json({authenticated:true});
  }
  if(req.method==='POST'&&validSession&&req.headers.origin&&req.headers.origin!=='https://'+req.headers.host)return res.status(403).json({error:'Invalid request origin'});
  const signedIn=validSession||!!user&&!!password&&equal(req.headers.authorization,'Basic '+Buffer.from(`${user}:${password}`).toString('base64'));
  if(!publicRead&&!publicQuery&&!signedIn)return res.status(403).json({error:'This action requires operator access. Public catalogue search and data-pack exports are available without sign-in.'});
  incoming.searchParams.delete('path');
  const upstream=new URL(base);
  if(upstream.protocol!=='https:'&&!(process.env.EKLIST_PROXY_LOCAL_TEST==='1'&&upstream.hostname==='127.0.0.1'))return res.status(503).json({error:'Backend must use HTTPS'});
  upstream.pathname='/api/'+path;upstream.search=incoming.searchParams.toString();
  let body=req.method==='POST'?(typeof req.body==='string'?req.body:JSON.stringify(req.body)):undefined;
  if(publicQuery&&!signedIn){try{body=JSON.stringify({...JSON.parse(body),ai:false})}catch{return res.status(400).json({error:'Invalid JSON body'})}}
  if(body&&Buffer.byteLength(body)>4_000_000)return res.status(413).json({error:'Hosted request too large. Split the file into smaller batches (about 2.8 MB for XLSX).'});
  try{
    const result=await fetch(upstream,{method:req.method,headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body,redirect:'error',signal:AbortSignal.timeout(55000)});
    res.status(result.status);
    for(const key of ['content-type','content-disposition'])if(result.headers.has(key))res.setHeader(key,result.headers.get(key));
    return res.send(Buffer.from(await result.arrayBuffer()));
  }catch{return res.status(502).json({error:'Backend unavailable or timed out. Check Render health and configuration.'})}
}
