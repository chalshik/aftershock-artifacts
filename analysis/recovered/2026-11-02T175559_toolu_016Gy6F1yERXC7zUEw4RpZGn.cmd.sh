cd /Users/chalshik/Projects/aftershock-artifacts; python3 -c "
per_tok=36*8*128*2*2   # layers x KV heads x head dim x (K,V) x bf16 bytes, Qwen3-4B
print('bytes/token',per_tok,'| check vs log:',round(13.27*2**30/96656))
C=96656;blk=16
for f in (0.85,0.8,0.75,0.7):
    b=int(C*f/blk);print('fraction',f,'blocks',b,'tokens',b*blk,'bytes',b*blk*per_tok)
"; grep -n "num_hidden_layers\|num_key_value_heads\|head_dim" ~/.cache/huggingface/hub/models--Qwen--Qwen3-4B/snapshots/*/config.json 2>/dev/null | head; ssh -i $HOME/.ssh/id_ed25519_vllm -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=10 chalshik@192.168.3.249 'grep -hE "\"(num_hidden_layers|num_key_value_heads|head_dim|torch_dtype)\"" ~/.cache/huggingface/hub/models--Qwen--Qwen3-4B/snapshots/*/config.json'