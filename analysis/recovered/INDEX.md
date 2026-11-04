# Recovered original analysis code

Verbatim copies of the analysis that produced figures published in `docs/decisions.md` before `analysis/derived.py` existed (decisions.md 2026-11-04, "[CORR] Derived-figure differences explained by the recovered originals"). They were never committed at the time.

- `<UTC timestamp>_<tool id>.cmd.sh`: the exact Bash command, with its inline Python, as recorded in the Claude Code session transcript.
- `.out.txt`: the output recorded for that command at the time.
- The two files from 2026-10-30 come from transcript `f5298640-1574-4ceb-a3d1-13cbc96eea3b`; all others from `c075c1a8-132c-4000-a89a-88e64c9c2bfd` (a fork of it, so the 2026-11-01 ids appear in both). Transcripts live in `~/.claude/projects/-Users-chalshik-Projects-aftershock-artifacts/` on the Mac.
- `2026-10-30T202124_toolu_01Tq9EcxwkXFPNnUYpXjXQVQ.judge.py`: the scratch script that call ran, copied from that session's scratchpad. Its file time (2026-10-30T20:21:21Z) is 3 s before the call, so it is the version that ran; nothing proves it was not changed later.
- **Do not edit or reformat these files.** They are records. Several commands ssh to the VM or read scratch files, so they are not re-run; `analysis/recompute_published.py` reads the values they printed from the `.out.txt` files (column "Original").
- One file per tool call, not per figure: some calls print several figures, and some figures need several calls. The table maps figures to files.

| Figure (decisions.md) | File(s) |
|---|---|
| Sweep hit by thirds 0.674 / 0.625 / 0.585 (2026-10-30, line 93); cache-on completions in overload | 2026-10-30T153748_toolu_017iqsdvq8p2rEYDXswGeVpk |
| Long-run thirds 0.609 / 0.608 / 0.600 and counter 0.6363 / 0.6254 (lines 116–118) | 2026-10-30T202124_toolu_01Tq9EcxwkXFPNnUYpXjXQVQ (runs a scratch `judge.py`; copy `.judge.py`, mtime 2026-10-30T20:21:21Z, 3 s before the call) |
| Long-run 300 s hit range 0.593–0.679 (line 209) | 2026-11-01T144142_toolu_01LsHsS5AVxGbAhSxNnhoNfV |
| Wipe-test spans (line 226): before (−120..0 s), 0–15, 15–60, 60–120 s | 2026-11-01T151616_toolu_01NT9QvG65iJCrCt2hEacrKM |
| W/C table, W tokens 47,580 / 59,722 / 72,968, F means and last thirds, whole-run hit 0.767 / 0.661 / 0.525 (lines 250–256, 405–409, 431) | 2026-11-01T173632_toolu_015jLzJdYAJ9HPDZ9RCwj2UE |
| Adjacent-window noise 0.34 / 0.076 / 0.059 (line 269); cached-share split and overlap (lines 292–293) | 2026-11-01T174226_toolu_01YMQ5wzSRPgYmhqRLqgxJN9 |
| Control verdict levels (KV 0.09 at λ = 2.5, possible origin of 8.7k; BELIEF) | 2026-11-01T215355_toolu_01ERXSiZtFdmg4pHCtdknqgA; 2026-11-01T223628_toolu_01A9yBgZCrUP8i4ddNWpf4yU |
| λ = 3 wipe spans, first attempts (line 339) | 2026-11-02T070514_toolu_018ir8NocG3MCswgEA2Sr8Rn |
| λ = 3 seed 1 rerun, 0–15 s 0.191 (line 344) | 2026-11-02T080403_toolu_01HSt1Pxb4np7XQ2UJB76R5Y |
| λ = 3 seed 3, 0–15 s 0.295, 15–60 s 0.61 (line 362) | 2026-11-02T105302_toolu_017XQn8ty2Dns5gBLkGvynVv |
| λ = 3.5 first-minute hit, seeds 1–2: 0.492, 0.534 (line 375) | 2026-11-02T120521_toolu_01W9rW5vG8xpXwAhGQ7Md46U; 2026-11-02T122512_toolu_01PnfGCWENcKH9LhD5nQNudH |
| λ = 3.5 wipe verdicts | 2026-11-02T130606_toolu_01PWhRNxP59kdNiAAxDmtAB6 |
| Burst λ = 3, 0–60 s hit 0.172 / 0.348 / 0.351 (line 393) | 2026-11-02T134123_toolu_012hfq291D9XgNCR4xNreAQV (s1); 2026-11-02T154218_toolu_01XKSd8XSeL21PAPgwfGgkib (s2, s3) |
| 72k pool size (4530 blocks, 10,687,610,880 bytes) (line 403) | 2026-11-02T175559_toolu_016Gy6F1yERXC7zUEw4RpZGn |
| 72k shock verdicts (line 450) | 2026-11-03T040439_toolu_014TkU3bmLStwpxFJqYDQoym |
| W at 5 s vs 20 s gaps, 18,705 / 74,843 tokens (line 499) | 2026-11-03T113103_toolu_01Fkc7RrjAEG9DrPCoXzTAst |

**Not found:** F_warm 6.4k / 8.7k (line 405–406); 72k spans 0.11–0.28 and 0.43 (lines 459–460); the long-run 60 s SD 0.045 (line 169); the λ = 3.5 seed-3 first minute.

## sha256

```
a4a16266399612e577442d1053de90805ec0ce5e461391590a80c64b4b722a40  2026-10-30T153748_toolu_017iqsdvq8p2rEYDXswGeVpk.cmd.sh
c210a275d44f71afabb1e8cf7dda4e3fb8b216280d9324fb877d75218cb91f2e  2026-10-30T153748_toolu_017iqsdvq8p2rEYDXswGeVpk.out.txt
44016894ec1e49b52de4ad0362da6f360a6ef02063dd8d3d8f1669aca3c77575  2026-10-30T202124_toolu_01Tq9EcxwkXFPNnUYpXjXQVQ.cmd.sh
8037d2bbcb0df6a8cbcd942b6340fdef806d20e3964a04f15b9d487f8ff1de0f  2026-10-30T202124_toolu_01Tq9EcxwkXFPNnUYpXjXQVQ.judge.py
2c57d4757a16cc9097821882deff18114862c7d2c5190db853b9a5276323849d  2026-10-30T202124_toolu_01Tq9EcxwkXFPNnUYpXjXQVQ.out.txt
3a4121a866c0e0787f7a2212dc8986d38b16560498ecdd2a002f40b788771e5a  2026-11-01T144142_toolu_01LsHsS5AVxGbAhSxNnhoNfV.cmd.sh
18c281090825f9477f8f929b408d3a283a17b7f58ff40a558ca56ccecdae35ac  2026-11-01T144142_toolu_01LsHsS5AVxGbAhSxNnhoNfV.out.txt
65fc34ca802de21e75ed0eee2a019994cecfc2ad94322c71fa4094a945c1ee70  2026-11-01T151616_toolu_01NT9QvG65iJCrCt2hEacrKM.cmd.sh
fbafa58a4b34c56c1cc20d0dd651714ae3c0a73338a2a81b081f770139807e25  2026-11-01T151616_toolu_01NT9QvG65iJCrCt2hEacrKM.out.txt
c9184580f5689023d4ff9556a575a3f86706a37ff9cea3d5818d8898e6f283a4  2026-11-01T173632_toolu_015jLzJdYAJ9HPDZ9RCwj2UE.cmd.sh
2a170fce7e8d52ebb4686098bc1a2c919ca11f39ee6ed2727a3f06038a36150d  2026-11-01T173632_toolu_015jLzJdYAJ9HPDZ9RCwj2UE.out.txt
50372ebc10bec9382e83803d03f660c2570f2828c3ca2bcfd82e4d2caacf9664  2026-11-01T174226_toolu_01YMQ5wzSRPgYmhqRLqgxJN9.cmd.sh
da0a085205e14119930ca9bf33cdad76071d2aaf3ec9bec290cb94e3b9bf131b  2026-11-01T174226_toolu_01YMQ5wzSRPgYmhqRLqgxJN9.out.txt
090706d707aed9bb9c05c913a3a67910d36ef956fe0d04c9ed37c60cf47bedfc  2026-11-01T215355_toolu_01ERXSiZtFdmg4pHCtdknqgA.cmd.sh
148679a8929be50b35530081bee42d0d086c81ae831b45bab95ecd4e5bfd939e  2026-11-01T215355_toolu_01ERXSiZtFdmg4pHCtdknqgA.out.txt
7263e7ee550fa6fe42121bc0592bfb99819a9ec9e679e73365b9973e6e3be72d  2026-11-01T223628_toolu_01A9yBgZCrUP8i4ddNWpf4yU.cmd.sh
a445fdf6e421bcb594c1c80621a759b906faf61a1d06aa9cc13e06ce6071203d  2026-11-01T223628_toolu_01A9yBgZCrUP8i4ddNWpf4yU.out.txt
5c231c3e2063c2d628860589967d3607012e0a95ac6ccd36f9e01834e3e30337  2026-11-02T070514_toolu_018ir8NocG3MCswgEA2Sr8Rn.cmd.sh
27197240bba05a162fb43431162a0f8f8c51dc843cf7a8f1fe982e5d1cd84023  2026-11-02T070514_toolu_018ir8NocG3MCswgEA2Sr8Rn.out.txt
35b3ba090b63730c23667c76e4b10d0459b8e972c7d0f908a22c7d961f9b3ddf  2026-11-02T080403_toolu_01HSt1Pxb4np7XQ2UJB76R5Y.cmd.sh
354f8d0bdba2c3db7cf1e8401d320f6667b624fcf5f3c838aa012b857f08ed86  2026-11-02T080403_toolu_01HSt1Pxb4np7XQ2UJB76R5Y.out.txt
9005697670786352f1a8afcf53da40d672beefab5ed2bfc678ddbf6cfcff21f1  2026-11-02T105302_toolu_017XQn8ty2Dns5gBLkGvynVv.cmd.sh
50724efc86dd9a00a3bf3c458f9cc6f803a735d23e44f23f1847d841e5a68481  2026-11-02T105302_toolu_017XQn8ty2Dns5gBLkGvynVv.out.txt
e509266aec5a12f1bf7d1ca38c01daf295ab6d7359b05cbdbe493beb9b21bd77  2026-11-02T120521_toolu_01W9rW5vG8xpXwAhGQ7Md46U.cmd.sh
1a23c9c4ef20db3c4164d291cd493a2d568988c148a991fedaabc14ffe718036  2026-11-02T120521_toolu_01W9rW5vG8xpXwAhGQ7Md46U.out.txt
5037892c61df4d40948292d9ac5a0e3ccfe77ffaf25af325be2ba65bda0d66d2  2026-11-02T122512_toolu_01PnfGCWENcKH9LhD5nQNudH.cmd.sh
fff7ddb44005c410f83c13f1c8303061965812f5b768856b7340d52a3f230841  2026-11-02T122512_toolu_01PnfGCWENcKH9LhD5nQNudH.out.txt
9cb3260eb2400acfb55424b7ed5b82a3560c414cfd942da95b909bad09f81ffe  2026-11-02T130606_toolu_01PWhRNxP59kdNiAAxDmtAB6.cmd.sh
62c224d204bb9442dce92087b8d47265c0d1e0401f8a0e04f23b456ae5f05768  2026-11-02T130606_toolu_01PWhRNxP59kdNiAAxDmtAB6.out.txt
7379ef0fb45c547f992b9024152ee1df144d76d704845603a16274a01068a22a  2026-11-02T134123_toolu_012hfq291D9XgNCR4xNreAQV.cmd.sh
523bd0951ced261f46510cce2a76627187bcc6977ee31959f4907ddb0ca447a0  2026-11-02T134123_toolu_012hfq291D9XgNCR4xNreAQV.out.txt
3492c2005443a9da388ce7b44e17a85470544323ab773290ff8465329cd953e5  2026-11-02T154218_toolu_01XKSd8XSeL21PAPgwfGgkib.cmd.sh
4aabbabad371d4790da9606f0c609481d5e46970884ee2df173908a80d2e4e0a  2026-11-02T154218_toolu_01XKSd8XSeL21PAPgwfGgkib.out.txt
fc1fba450bcaef3707f872e4f5d35467fc96ef90bbd2ce57bf9f52ab429016ea  2026-11-02T175559_toolu_016Gy6F1yERXC7zUEw4RpZGn.cmd.sh
707524b40ebe7e29b95242e2849daea8ba3414aed7c68a64885ae99d0aad40ac  2026-11-02T175559_toolu_016Gy6F1yERXC7zUEw4RpZGn.out.txt
53f92d34d0bd00c946694250676d76acdd89cc45e20d9f4d9d406a4c55fd7a2d  2026-11-03T040439_toolu_014TkU3bmLStwpxFJqYDQoym.cmd.sh
17f1f9fafc7341efa190c9768b068a2835e9d189139f87404b3f4747c61ecca8  2026-11-03T040439_toolu_014TkU3bmLStwpxFJqYDQoym.out.txt
a0346f9603657f2583b239d4a0837c9dbfe49cbdf52f8c127202e7bc88469b64  2026-11-03T113103_toolu_01Fkc7RrjAEG9DrPCoXzTAst.cmd.sh
efd7cbfbcfa8e46736694d971233269d21b7e01d721b35a1c2502bc52ce5e7b0  2026-11-03T113103_toolu_01Fkc7RrjAEG9DrPCoXzTAst.out.txt
```
