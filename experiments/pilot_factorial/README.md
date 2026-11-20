# Pilot factorial artifacts

此目录存放配置 manifest schema、环境 pin、成本 profile 和冻结协议。原始 episode 与缓存不得提交到 Git，应放在 `raw/` 或外部 artifact store，并保留 checksum 和访问说明。

当前 runner 仍只支持 `mode=mock`；mock 输出是可复算的合成验证数据，不是 tau2 benchmark 结果。真实 tau2 factorial runner 尚待 Phase 0C 实现。

当前用户指定的 provider/model 为 DeepSeek API `deepseek-flash`。固定要求：thinking/CoT disabled、JSON mode、temperature 0.0、输出上限 512 tokens、DeepSeek 直连并绕过系统代理。价格 profile 使用官方高峰 cache-miss 费率作为保守上界。

`cost_profile.json` 保存模型、请求配置、token/调用上界和价格依据。真实调用前必须重新核价、通过所有 no-API preflight，并取得用户明确的付费 Smoke 批准。模型选择本身不是付费运行授权。
