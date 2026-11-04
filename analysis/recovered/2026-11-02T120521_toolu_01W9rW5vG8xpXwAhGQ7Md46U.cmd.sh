date -u; ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=8 chalshik@192.168.3.249 'date -u; uptime -p; tmux ls 2>&1 | cut -c1-50; grep -E "ALL_DONE|_EXIT=" ~/wipes_r35.console.log | tr "\n" " "; echo; tail -n 1 ~/wipes_r35.console.log | cut -c1-110; nvidia-smi --query-gpu=temperature.gpu,fan.speed,power.draw,utilization.gpu --format=csv,noheader; python3 -' <<'E'
import glob,json,os,statistics as st
base=os.path.expanduser("~/aftershock-artifacts/runs/")
for d in sorted(glob.glob(base+"*wipe_preempt_r3.5_s*")):
    n=os.path.basename(d);ck=d+"/checks.json";v=json.load(open(ck)) if os.path.exists(ck) else None
    rs=[json.loads(l) for l in open(d+"/requests.jsonl")] if os.path.exists(d+"/requests.jsonl") else []
    stt={}
    for r in rs: stt[r["status"]]=stt.get(r["status"],0)+1
    g=[json.loads(l) for l in open(d+"/gpu.jsonl")] if os.path.exists(d+"/gpu.jsonl") else []
    w=[x for x in g if 240<=x["t"]<=2400];b=[x for x in w if x["util_pct"]>=50]
    hw=[(round(x["t"]),hex(x["throttle_reasons"])) for x in w if x["throttle_reasons"]&0xC8]
    sw=sum(1 for x in w if x["throttle_reasons"]&0x20)/max(1,len(w))
    tr=d+"/trigger.jsonl";a=[json.loads(l) for l in open(tr)] if os.path.exists(tr) and os.path.getsize(tr) else []
    print(n,"|",("VALID" if v["valid"] else "INVALID "+str(v["failed"])) if v else "running","| reqs",len(rs),stt,"| t=%.0f"%(g[-1]["t"] if g else 0),"| hw",len(hw),hw[:3],"sw %.3f"%sw,"meanT %.1f maxT %s"%(st.mean(x["temp_c"] for x in b) if b else 0,max([x["temp_c"] for x in w] or [0])),"| wipe",(a[-1]["success"],round(a[-1]["t_end"],2)) if a else None)
    ms=[json.loads(l) for l in open(d+"/metrics.jsonl")];ms=[m for m in ms if "values" in m]
    if not ms: continue
    def tot(m,k): return sum(x for kk,x in m["values"].items() if kk.split("{",1)[0]==k)
    def at(t): return min(ms,key=lambda m:abs(m["t"]-t))
    T=a[-1]["t_end"] if a and a[-1]["success"] else None
    spans=[(300,900,"base")]+([(T,T+60,"+0..60"),(T+60,T+300,"+60..300"),(T+300,T+600,"+300..600"),(T+600,T+900,"+600..900"),(T+900,T+1200,"+900..1200"),(T+1200,T+1500,"+1200..1500")] if T else [])
    for x0,x1,lab in spans:
        if x0>ms[-1]["t"]: continue
        x1=min(x1,ms[-1]["t"]);win=[m for m in ms if x0<=m["t"]<x1];z=[r for r in rs if x0<=r["t_planned"]<x1]
        y=[r["t_first_token"]-r["t_planned"] for r in z if r.get("t_first_token")]
        A,B=at(x0),at(x1);dq=tot(B,"vllm:prefix_cache_queries_total")-tot(A,"vllm:prefix_cache_queries_total")
        if not win or not z: continue
        print("   %-11s fast %.3f hit %.3f N %.1f maxN %d Q %.1f maxQ %d KV %.2f maxKV %.2f preempt %d"%(lab,sum(1 for q in y if q<=1)/len(z),(tot(B,"vllm:prefix_cache_hits_total")-tot(A,"vllm:prefix_cache_hits_total"))/max(dq,1),st.mean(tot(m,"vllm:num_requests_running") for m in win),max(tot(m,"vllm:num_requests_running") for m in win),st.mean(tot(m,"vllm:num_requests_waiting") for m in win),max(tot(m,"vllm:num_requests_waiting") for m in win),st.mean(tot(m,"vllm:kv_cache_usage_perc") for m in win),max(tot(m,"vllm:kv_cache_usage_perc") for m in win),tot(B,"vllm:num_preemptions_total")-tot(A,"vllm:num_preemptions_total")))
E