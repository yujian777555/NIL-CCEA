# Pilot factorial artifacts

此目录存放配置 manifest schema、环境 pin 和冻结前协议材料。原始 episode 与缓存不得提交到 Git，应放在 `raw/` 或外部 artifact store，并保留 checksum 和访问说明。

当前 runner 只支持 `mode=mock`，所有 mock 输出都是可复算的合成验证数据，不是 tau2 benchmark 结果。
