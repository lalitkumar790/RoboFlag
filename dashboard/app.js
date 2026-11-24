"use strict";
const $=id=>document.getElementById(id);
let data, replay, timer=null;
const project=(x,y,z=0)=>[370+(x-y)*18,36+(x+y)*12-z];
function poly(ctx,points,color,stroke){ctx.beginPath();points.forEach((p,i)=>i?ctx.lineTo(...p):ctx.moveTo(...p));ctx.closePath();ctx.fillStyle=color;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.stroke();}}
function cube(ctx,x,y,h,colors){const a=project(x,y),b=project(x+0.86,y),c=project(x+0.86,y+0.86),d=project(x,y+0.86);const A=project(x,y,h),B=project(x+0.86,y,h),C=project(x+0.86,y+0.86,h),D=project(x,y+0.86,h);poly(ctx,[b,c,C,B],colors[1]);poly(ctx,[c,d,D,C],colors[2]);poly(ctx,[A,B,C,D],colors[0]);}
function draw(id,run,tick,color){
 const canvas=$(id),ctx=canvas.getContext("2d"),frame=run.trace[Math.min(tick,run.trace.length-1)];
 ctx.clearRect(0,0,canvas.width,canvas.height);
 for(let x=0;x<run.width;x++)for(let y=0;y<run.height;y++)poly(ctx,[project(x,y),project(x+1,y),project(x+1,y+1),project(x,y+1)],(x+y)%2?"#172536":"#1a2b3e","#26394c");
 for(const m of run.missions){const [x,y]=m.goal;const [a,b]=project(x+.5,y+.5);ctx.beginPath();ctx.ellipse(a,b,8,5,0,0,Math.PI*2);ctx.strokeStyle="#a9b9ca";ctx.stroke();}
 const objects=run.walls.map(([x,y])=>({x,y,h:28,c:["#70859b","#3e5065","#52667c"]}));
 frame.obstacles.forEach(([x,y])=>objects.push({x,y,h:9,c:["#f87171","#9f3333","#c84b4b"]}));
 frame.positions.forEach(([x,y],i)=>{const m=run.missions[i];const done=m.success&&m.duration<=frame.tick;objects.push({x:x+.07,y:y+.07,h:12,c:done?["#4de3ba","#16866d","#24ad8f"]:color});});
 objects.sort((a,b)=>a.x+a.y-b.x-b.y).forEach(o=>cube(ctx,o.x,o.y,o.h,o.c));
 $(id+"Count").textContent=frame.completed+"/"+run.missions.length+" complete";
 $(id+"Stats").textContent="Replay tick "+frame.tick+" / "+run.trace.length+" · Final blocked proposals: "+run.prevented_conflicts+" · Final success: "+run.missions.filter(m=>m.success).length+"/"+run.missions.length;
}
function render(){const t=Number($("tick").value);$("tickLabel").textContent=t+1;draw("a",replay.arms.astar,t,["#f2c879","#987235","#bc9347"]);draw("b",replay.arms.congestion_aware,t,["#76baff","#275b99","#3a7bc5"]);}
function stop(){if(timer!==null)clearInterval(timer);timer=null;$("play").textContent="Play";}
function select(){stop();replay=data.replays[Number($("seed").value)];$("tick").max=Math.max(replay.arms.astar.trace.length,replay.arms.congestion_aware.trace.length)-1;$("tick").value=0;render();}
function play(){if(timer!==null){stop();return;}if(Number($("tick").value)>=Number($("tick").max))$("tick").value=0;$("play").textContent="Pause";timer=setInterval(()=>{if(Number($("tick").value)>=Number($("tick").max)){stop();return;}$("tick").value=Number($("tick").value)+1;render();},Number($("speed").value));}
function report(){const a=data.benchmark.astar,b=data.benchmark.congestion_aware;const rows=[["Mission success","success_rate",v=>(100*v).toFixed(1)+"%"],["Capped duration","mean_duration_capped_ticks",v=>v.toFixed(1)+" ticks"],["Movement steps","mean_steps",v=>v.toFixed(1)],["Waiting ticks","mean_waits",v=>v.toFixed(1)],["Blocked proposals","prevented_conflicts",v=>String(v)]];
 for(const [label,key,fmt] of rows){const row=document.createElement("div");row.className="metric";const name=document.createElement("span");name.textContent=label;row.append(name);for(const [title,value] of [["Control",a[key]],["Treatment",b[key]]]){const cell=document.createElement("div"),caption=document.createElement("small"),strong=document.createElement("strong"),bar=document.createElement("div"),fill=document.createElement("i");caption.textContent=title;strong.textContent=fmt(value);bar.className="bar";fill.style.width=(100*value/(key==="success_rate"?1:Math.max(a[key],b[key],1)))+"%";bar.append(fill);cell.append(caption,strong,bar);row.append(cell);}$("metrics").append(row);}
}
fetch("data.json").then(r=>{if(!r.ok)throw Error("Replay data HTTP "+r.status);return r.json();}).then(d=>{if(d.kind!=="offline_simulation"||!d.replays.length)throw Error("Invalid replay data");data=d;d.replays.forEach((r,i)=>{const option=document.createElement("option");option.value=i;option.textContent="Seed "+r.seed;$("seed").append(option);});for(const id of ["play","reset","tick"])$(id).disabled=false;select();report();$("rolloutMode").disabled=false;renderRollout();renderEvidence();}).catch(e=>{$("error").textContent=e.message+". Generate data with python -m roboflag.export_dashboard and serve the dashboard directory."});
$("seed").onchange=select;$("play").onclick=play;$("reset").onclick=()=>{stop();$("tick").value=0;render();};$("tick").oninput=()=>{stop();render();};$("speed").onchange=()=>{if(timer!==null){stop();play();}};

function renderRollout(){
 const r=data.rollouts[$("rolloutMode").value], pct=v=>(100*v).toFixed(1)+"%";
 $("rolloutSummary").textContent="Baseline "+pct(r.baseline_rate)+" · Final candidate allocation "+r.final_candidate_percentage+"% · Threshold "+pct(r.regression_limit);
 const host=$("rolloutAudit");host.replaceChildren();
 for(const s of r.history){
  const row=document.createElement("div");row.className="audit";
  for(const value of [s.stage_percent+"% target",s.assigned+"/"+s.missions+" assigned",pct(s.effective_success_rate)+" success",s.injected_losses+" injected losses",s.decision]){
   const cell=document.createElement("span");cell.textContent=value;row.append(cell);
  }
  row.lastChild.className=s.decision==="ROLLBACK"?"danger":"good";host.append(row);
 }
}
$("rolloutMode").onchange=renderRollout;

function renderEvidence(){
 const pct=v=>(100*v).toFixed(1)+"%";
 const host=$("densityEvidence");
 for(const row of data.validation.results){
  const section=document.createElement("section"), heading=document.createElement("h3");
  heading.textContent=row.robots+" robots per fleet";section.append(heading);
  for(const [label,key] of [["Mission completion","completion_rate"],["All missions completed","all_completed_rate"],["Mean capped duration (ticks)","capped_duration"]]){
   const line=document.createElement("div");line.className="metric";
   for(const value of [label,...["astar","congestion_aware"].map((arm,i)=>(i?"Adaptive: ":"Control: ")+(key==="capped_duration"?row.arms[arm][key].toFixed(1):pct(row.arms[arm][key])))]){const el=document.createElement("span");el.textContent=value;line.append(el);}
   section.append(line);
  }
  host.append(section);
 }
 const e=$("experimentEvidence"), n=data.native_experiment, m=n.native.payload.metrics[0].variants;
 const add=(value)=>{const p=document.createElement("p");p.textContent=value;e.append(p);};
 for(const [label,key] of [["Control","control"],["Adaptive","adaptive"]]){
  const v=m[key], local=n.local[key];
  add(label+" complete fleet success: "+v.sum+"/"+v.n+" ("+pct(v.sum/v.n)+")");
  add(label+" individual missions: "+local.successes+"/"+local.missions+" ("+pct(local.successes/local.missions)+") · Blocked proposals per fleet: "+(local.blocked/local.fleets).toFixed(2));
 }
 add("Absolute primary lift: "+(100*(m.adaptive.sum/m.adaptive.n-m.control.sum/m.control.n)).toFixed(2)+" percentage points");
 add("Independent Fisher exact p = "+n.independent.fisher_two_sided.toExponential(3)+" · Allocation exact binomial p = "+n.independent.allocation_binomial_two_sided.toFixed(4));
 add("Native inference: "+(n.native.payload.metrics[0].inference.adaptive===null?"unavailable":"available")+" · Snapshot "+n.native.as_of+" · Status at capture: "+n.status_at_capture);
}
