// Completeness describes available evidence, never accuracy or operating status.
export function distanceMeters(a,b){
 const valid=r=>r&&[r.lat,r.lon].every(v=>v!==null&&v!==undefined&&v!==''&&Number.isFinite(Number(v)))&&Math.abs(Number(r.lat))<=90&&Math.abs(Number(r.lon))<=180;
 if(!valid(a)||!valid(b))return null;
 const rad=v=>Number(v)*Math.PI/180,dLat=rad(b.lat)-rad(a.lat),dLon=rad(b.lon)-rad(a.lon);
 const h=Math.sin(dLat/2)**2+Math.cos(rad(a.lat))*Math.cos(rad(b.lat))*Math.sin(dLon/2)**2;
 return 6371000*2*Math.asin(Math.sqrt(Math.min(1,h)));
}
export function qualityReport(groups){
 const issues=[];
 for(const g of groups){
  const add=(code,detail)=>issues.push({groupId:g.id,name:g.name,code,detail});
  for(const field of ['address','phone','city','entityId'])if(!g.values[field]?.some(v=>String(v).trim()))add('missing_'+field,`No ${field==='entityId'?'shared identifier':field} supplied. Check the original directory or ask the field team; do not infer it.`);
  for(const field of g.conflicts)add('conflict_'+field,`Sources disagree on ${field}. All values are retained; verify before outreach.`);
  let far=false;for(let i=0;i<g.records.length;i++)for(let j=i+1;j<g.records.length;j++){const d=distanceMeters(g.records[i],g.records[j]);if(d!==null&&d>500)far=true;}
  if(far)add('location_conflict','Linked records are over 500 metres apart. This may be a different branch or a source error.');
 }
 const affected=new Set(issues.map(i=>i.groupId));return {total:groups.length,complete:groups.length-affected.size,issues};
}
export function issuesCSV(report){const quote=v=>'"'+String(v??'').replace(/^[\s]*[=+@-]/,"'$&").replace(/"/g,'""')+'"';return '\uFEFF'+[['record_id','name','issue','verification_action'],...report.issues.map(i=>[i.groupId,i.name,i.code,i.detail])].map(r=>r.map(quote).join(',')).join('\r\n');}
