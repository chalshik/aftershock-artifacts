date -u; ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=8 chalshik@192.168.3.249 'date -u; uptime -p; tmux ls 2>&1 | cut -c1-50; grep -E "ALL_DONE|_EXIT=" ~/bursts.console.log | tr "\n" " "; echo; tail -n 1 ~/bursts.console.log | cut -c1-110; nvidia-smi --query-gpu=temperature.gpu,fan.speed,power.draw,utilization.gpu --format=csv,noheader; cd ~/aftershock-artifacts && .venv/bin/python -' <<'E'
import glob,json,os,statistics as st
import pandas as pd
base="runs/"
for d in sorted(glob.glob(base+"*burst_r*_s*")):
    n=os.path.basename(d);ck=d+"/checks.json";v=json.load(open(ck)) if os.path.exists(ck) else None
    sc=pd.read_parquet(d+"/schedule.parquet")
    rs=pd.DataFrame([json.loads(l) for l in open(d+"/requests.jsonl")]) if os.path.exists(d+"/requests.jsonl") and os.path.getsize(d+"/requests.jsonl") else pd.DataFrame()
    g=[json.loads(l) for l in open(d+"/gpu.jsonl")] if os.path.exists(d+"/gpu.jsonl") else []
    w=[x for x in g if 240<=x["t"]<=2520];b=[x for x in w if x["util_pct"]>=50]
    hw=[(round(x["t"]),hex(x["throttle_reasons"])) for x in w if x["throttle_reasons"]&0xC8]
    sw=sum(1 for x in w if x["throttle_reasons"]&0x20)/max(1,len(w))
    print(n,"|",("VALID" if v["valid"] else "INVALID "+str(v["failed"])) if v else "running","| t=%.0f"%(g[-1]["t"] if g else 0),"| reqs",len(rs),(rs.status.value_counts().to_dict() if len(rs) else {}),"| hw",len(hw),hw[:3],"sw %.3f maxT %s"%(sw,max([x["temp_c"] for x in w] or [0])))
    if not len(rs): continue
    rs=rs.merge(sc[["request_id","burst"]],on="request_id");rs["ttft"]=rs.t_first_token-rs.t_planned
    bb=rs[rs.burst];print("   burst requests recorded %d/%d, sent %d, ok %d, ttft p50 %.2f max %.1f"%(len(bb),int(sc.burst.sum()),bb.t_sent.notna().sum(),(bb.status=="ok").sum(),bb.ttft.median(),bb.ttft.max()))
    ms=[json.loads(l) for l in open(d+"/metrics.jsonl")];ms=[m for m in ms if "values" in m]
    def tot(m,k): return sum(x for kk,x in m["values"].items() if kk.split("{",1)[0]==k)
    def at(t): return min(ms,key=lambda m:abs(m["t"]-t))
    s=rs[~rs.burst]
    for x0,x1,lab in [(420,900,"before"),(900,1020,"BURST"),(1020,1080,"+0..60"),(1080,1320,"+60..300"),(1320,1620,"+300..600"),(1620,1920,"+600..900"),(1920,2220,"+900..1200"),(2220,2520,"+1200..1500")]:
        if x0>ms[-1]["t"]: continue
        x1=min(x1,ms[-1]["t"]);win=[m for m in ms if x0<=m["t"]<x1];z=s[(s.t_planned>=x0)&(s.t_planned<x1)]
        A,B=at(x0),at(x1);dq=tot(B,"vllm:prefix_cache_queries_total")-tot(A,"vllm:prefix_cache_queries_total")
        if not win or not len(z): continue
        print("   %-12s sessions-only fast %.3f p99 %.1f | hit %.3f | N %.1f maxN %d | Q %.1f maxQ %d | KV %.2f maxKV %.2f | preempt %d"%(lab,((z.status=="ok")&(z.ttft<=1)).sum()/len(z),z.ttft.quantile(.99),(tot(B,"vllm:prefix_cache_hits_total")-tot(A,"vllm:prefix_cache_hits_total"))/max(dq,1),st.mean(tot(m,"vllm:num_requests_running") for m in win),max(tot(m,"vllm:num_requests_running") for m in win),st.mean(tot(m,"vllm:num_requests_waiting") for m in win),max(tot(m,"vllm:num_requests_waiting") for m in win),st.mean(tot(m,"vllm:kv_cache_usage_perc") for m in win),max(tot(m,"vllm:kv_cache_usage_perc") for m in win),tot(B,"vllm:num_preemptions_total")-tot(A,"vllm:num_preemptions_total")))
E