"use strict";
const el=id=>document.getElementById(id);
let manifest, run, time=0, playing=false,last=0, token=0;
let az=-.65,elev=.72,zoom=1,panX=0,panY=0;
const modes=["congestion_aware","progress_aware"];
const panels=[["leftScene","leftCount","leftMetrics"],["rightScene","rightCount","rightMetrics"]];
function sample(r,t){
 const a=r.trace;let lo=0,hi=a.length-1;
 while(lo<hi){const m=Math.ceil((lo+hi)/2);if(a[m].time_s<=t)lo=m;else hi=m-1;}
 const f=a[lo],g=a[Math.min(lo+1,a.length-1)],k=Math.max(0,Math.min(1,(t-f.time_s)/(g.time_s-f.time_s||1)));
 const lerp=(x,y)=>x+(y-x)*k;
 return {poses:f.poses.map((p,i)=>[lerp(p[0],g.poses[i][0]),lerp(p[1],g.poses[i][1]),p[2]+Math.atan2(Math.sin(g.poses[i][2]-p[2]),Math.cos(g.poses[i][2]-p[2]))*k]),cart:f.cart.map((v,i)=>lerp(v,g.cart[i]))};
}
function draw(canvas,r,index){
 const c=canvas.getContext("2d"),W=canvas.width,H=canvas.height,S=29*zoom;
 const ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(elev),se=Math.sin(elev);
 function camera(p){const x=p[0]-8.5,y=p[1]-5.5,z=p[2]||0;return [x*ca-y*sa,(x*sa+y*ca)*se-z*ce,(x*sa+y*ca)*ce+z*se];}
 function project(p){const q=camera(p);return [W/2+q[0]*S+panX,H/2+q[1]*S+panY];}
 const faces=[];
 function poly(points,color,stroke){const p=points.map(project);c.beginPath();p.forEach((v,i)=>i?c.lineTo(...v):c.moveTo(...v));c.closePath();c.fillStyle=color;c.fill();if(stroke){c.strokeStyle=stroke;c.stroke();}}
 function face(points,color){faces.push({points,color,depth:points.reduce((s,p)=>s+camera(p)[2],0)/points.length});}
 function box(x,y,z,l,w,h,yaw,colors){
 const q=(a,b,k)=>[x+a*Math.cos(yaw)-b*Math.sin(yaw),y+a*Math.sin(yaw)+b*Math.cos(yaw),z+k];
 const p=[q(-l/2,-w/2,0),q(l/2,-w/2,0),q(l/2,w/2,0),q(-l/2,w/2,0)],t=[q(-l/2,-w/2,h),q(l/2,-w/2,h),q(l/2,w/2,h),q(-l/2,w/2,h)];
 for(let i=0;i<4;i++)face([p[i],p[(i+1)%4],t[(i+1)%4],t[i]],colors[i%2+1]);face(t,colors[0]);
 }
 c.clearRect(0,0,W,H);c.fillStyle="#0b1522";c.fillRect(0,0,W,H);
 for(let x=0;x<run.width;x++)for(let y=0;y<run.height;y++)poly([[x-.5,y-.5,0],[x+.5,y-.5,0],[x+.5,y+.5,0],[x-.5,y+.5,0]],(x+y)%2?"#17293a":"#1c3043","#2a4052");
 for(const [,g] of run.missions){const points=Array.from({length:24},(_,i)=>[g[0]+.3*Math.cos(i*Math.PI/12),g[1]+.3*Math.sin(i*Math.PI/12),.01]);poly(points,"#284b50","#67d9bf");}
 for(const [x,y] of run.walls)box(x,y,0,.98,.98,1,0,["#8194a5","#40566d","#526b80"]);
 const f=sample(r,Math.min(time,r.simulated_seconds));
 box(f.cart[0],f.cart[1],.02,.32,.32,.36,0,["#ff8b83","#9c363b","#c45051"]);
 f.poses.forEach(([x,y,h],i)=>{
 const done=r.mission_completion_seconds[i]!==null&&r.mission_completion_seconds[i]<=time;
 const colors=done?["#4de3ba","#167b69","#229d86"]:index?["#76baff","#285d99","#397db8"]:["#f2c879","#987235","#bc9347"];
 box(x,y,.055,.31,.31,.12,h,colors);
 for(const offset of [-.18,.18])box(x-offset*Math.sin(h),y+offset*Math.cos(h),0,.16,.07,.16,h,["#536477","#1a2230","#303b49"]);
 box(x+.09*Math.cos(h),y+.09*Math.sin(h),.175,.10,.07,.02,h,["#ffffff","#999999","#cccccc"]);
 });
 faces.sort((a,b)=>a.depth-b.depth);for(const p of faces)poly(p.points,p.color);
}
function render(){
 if(!run)return;
 el("physicalClock").textContent=time.toFixed(1)+" s";el("physicalTime").value=time;
 modes.forEach((mode,i)=>{const r=run.arms[mode],p=panels[i];draw(el(p[0]),r,i);el(p[1]).textContent=r.mission_completion_seconds.filter(v=>v!==null&&v<=time).length+"/"+run.missions.length+" complete";el(p[2]).textContent="Final: "+r.successes+"/"+r.robots+" · "+r.simulated_seconds.toFixed(1)+" s · "+r.work_proxy_j.toFixed(1)+" J work proxy · "+r.external_contact_episodes+" contact episodes";});
}
function pause(){playing=false;el("physicalPlay").textContent="Play";}
function animate(now){if(playing&&run){time=Math.min(Number(el("physicalTime").max),time+Math.min(.1,(now-last)/1000)*Number(el("physicalSpeed").value));render();if(time>=Number(el("physicalTime").max))pause();}last=now;requestAnimationFrame(animate);}
async function load(){
 const id=++token;pause();el("physicalPlay").disabled=true;
 const item=manifest.scenarios[Number(el("fleetSize").value)];
 const response=await fetch("physical-data/"+item.file);if(!response.ok)throw Error("Replay unavailable");
 const d=await response.json();if(id!==token)return;
 run=d;time=0;el("physicalTime").max=Math.max(...modes.map(m=>run.arms[m].simulated_seconds));for(const id of ["physicalPlay","physicalReset","physicalTime"])el(id).disabled=false;render();
}
function error(e){el("physicalError").textContent=e.message;}
el("fleetSize").onchange=()=>load().catch(error);
el("physicalPlay").onclick=()=>{if(playing){pause();return;}if(time>=Number(el("physicalTime").max))time=0;playing=true;el("physicalPlay").textContent="Pause";};
el("physicalReset").onclick=()=>{pause();time=0;render();};
el("physicalTime").oninput=()=>{pause();time=Number(el("physicalTime").value);render();};
el("topView").onclick=()=>{elev=Math.PI/2;az=0;zoom=1;panX=panY=0;render();};
el("orbitView").onclick=()=>{az=-.65;elev=.72;zoom=1;panX=panY=0;render();};
for(const [id] of panels){const canvas=el(id);let drag=null;canvas.onpointerdown=e=>{drag=[e.clientX,e.clientY,e.shiftKey||e.button===2];canvas.setPointerCapture(e.pointerId);};canvas.onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag[0],dy=e.clientY-drag[1];if(drag[2]){panX+=dx;panY+=dy;}else{az+=dx*.008;elev=Math.max(.15,Math.min(Math.PI/2,elev+dy*.008));}drag[0]=e.clientX;drag[1]=e.clientY;render();};canvas.onpointerup=canvas.onpointercancel=()=>drag=null;canvas.oncontextmenu=e=>e.preventDefault();canvas.addEventListener("wheel",e=>{e.preventDefault();zoom=Math.max(.5,Math.min(3,zoom*Math.exp(-e.deltaY*.001)));render();},{passive:false});}
fetch("physical-data/manifest.json").then(r=>{if(!r.ok)throw Error("Generate native replay: python -m roboflag.export_physical");return r.json();}).then(d=>{manifest=d;d.scenarios.forEach((s,i)=>{const o=document.createElement("option");o.value=i;o.textContent=s.robots+" robots / seed "+s.seed;el("fleetSize").append(o);});el("fleetSize").disabled=false;return load();}).catch(error);
fetch("physical-evidence.json").then(r=>{if(!r.ok)throw Error("Evidence unavailable");return r.json();}).then(d=>{for(const campaign of d.campaigns){const section=document.createElement("section");const h=document.createElement("h3");h.textContent=campaign.label;section.append(h);for(const a of campaign.arms){const p=document.createElement("p");p.textContent=a.label+": "+a.successes+"/"+a.missions+" completed · "+a.contacts+" contacts";section.append(p);}const link=document.createElement("a");link.href=campaign.source;link.textContent="Verified benchmark ↗";section.append(link);el("physicalEvidence").append(section);}}).catch(error);
requestAnimationFrame(animate);
